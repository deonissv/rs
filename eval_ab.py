import pandas as pd

from microservice.data_parsing.parse_transformed_data import (
    parse_transformed,
    WEIGHT_RATING,
)
from microservice.data_parsing.transform_sessions import transform_sessions

GROUPS_NUMBER = 3


sessions = pd.read_json("data/sessions.jsonl", lines=True)
tracks_df = pd.read_json("data/tracks.jsonl", lines=True)
users_df = pd.read_json("data/users.jsonl", lines=True)

logs = pd.read_json("microservice/logs/logs.jsonl", lines=True)


tol = pd.Timedelta(seconds=60)
s = (
    sessions.groupby(["session_id", "user_id"])
    .agg({"timestamp": min})
    .sort_values("timestamp")
    .reset_index()
)
logs = logs.sort_values("timestamp").reset_index(drop=True)
merged = pd.merge_asof(s, logs, on="timestamp", direction="nearest", tolerance=tol)


groups = [merged[merged["group"].round(1) == i] for i in range(GROUPS_NUMBER)]
groups = [g[g.apply(lambda row: row.user_id == row.users[0], axis=1)] for g in groups]

ratings = []
for group in groups:
    selected_sessions = group["session_id"].values
    filtered_sessions = sessions[sessions["session_id"].isin(selected_sessions)]

    transformed = transform_sessions(filtered_sessions)
    if transformed is None:
        ratings.append(0)
        continue
    parsed = parse_transformed(tracks_df, transformed, users_df, WEIGHT_RATING, False)
    ratings.append(parsed.sum().sum())

print(ratings)
