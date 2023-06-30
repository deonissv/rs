from typing import List, Optional

import pickle
import logging
import pandas as pd

from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel


from logging.config import dictConfig
from logger_config import logging_schema

from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse

from utils import get_group, fmt_ab_log_msg, fmt_predict_log_msg

from data_parsing.parse_transformed_data import parse_transformed, WEIGHT_RATING
from data_parsing.transform_sessions import transform_sessions

dictConfig(logging_schema)
logger = logging.getLogger("logger")

app = FastAPI(debug=True)


class PredictionQuery(BaseModel):
    users: List[str]


class PredictionResponse(BaseModel):
    tracks: List[str]


class ABTest(BaseModel):
    group: int


class ABTestPredictionResponse(PredictionResponse, ABTest):
    ...


class SessionRecord(BaseModel):
    session_id: int
    timestamp: str
    user_id: int
    track_id: Optional[str]
    event_type: str

    def __dict__(self):
        return {
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "user_id": self.user_id,
            "track_id": self.track_id,
            "event_type": self.event_type,
        }


def load_models(model_names: List[str]):
    models = {}
    for name in model_names:
        with open(f"{MODELS_PATH / name}.pkl", "rb") as f:
            models.update({name: pickle.load(f)})
    return models


MAX_USERS = 5
MODELS_PATH = Path(__file__).parent / "models"
MODEL_NAMES = ["top_group_model", "top_all_model", "advanced_model"]
MODELS = load_models(MODEL_NAMES)

TRACKS_DF = pd.read_json("data/tracks.jsonl", lines=True)
USERS_DF = pd.read_json("data/users.jsonl", lines=True)


@app.post("/predict/abtest")
def predict_ab(users: List[int]) -> ABTestPredictionResponse:
    group = get_group(users, groups_number=len(MODELS))
    model = MODELS.get(MODEL_NAMES[group])
    tracks = model.predict(pd.Series(users))

    logger.info(msg=fmt_ab_log_msg(users, tracks, group))
    return ABTestPredictionResponse(tracks=tracks, group=group)


@app.post("/predict/{model_name}")
def predict(model_name: str, users: List[int]) -> PredictionResponse:
    if model_name not in MODEL_NAMES:
        raise HTTPException(status_code=400, detail="Model not found")
    if len(users) > MAX_USERS:
        raise HTTPException(status_code=400, detail="Users group is too big")
    model = MODELS.get(model_name)
    tracks = model.predict(pd.Series(users))

    logger.info(msg=fmt_predict_log_msg(users, tracks))
    return PredictionResponse(tracks=tracks)


@app.post("/update")
def update(sessions: List[SessionRecord]) -> HTMLResponse:
    df = pd.DataFrame([dict(session) for session in sessions])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["track_id"] = df["track_id"].astype(str)
    df["event_type"] = df["event_type"].astype(str)
    transformed = transform_sessions(df)
    parsed = parse_transformed(TRACKS_DF, transformed, USERS_DF, WEIGHT_RATING, False)
    model = MODELS.get("advanced_model")
    user_rating = model._user_rating.add(parsed, fill_value=0)
    model.update(user_rating)
    return HTMLResponse(status_code=200)
