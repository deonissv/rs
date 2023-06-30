from typing import List

import numpy as np
import pandas as pd

WEIGHT_RATING = [3, 1]


def init_matrix(users: List, tracks: pd.DataFrame):
    users_ratings = pd.DataFrame(index=users, columns=tracks["id"].squeeze())

    return users_ratings


def calc_rating(row, weight_rating) -> float:
    track_duration = row["duration_ms"]
    plays_unskipped = row["play"] - row["skip"]
    total_duration = (track_duration * plays_unskipped) + (row["duration"] * 1000)
    rating = (row["like"] * weight_rating[0]) + (
        (total_duration * weight_rating[1]) / (row["play"] * track_duration)
    )
    return rating


def parse_transformed(
    tracks_df: pd.DataFrame,
    sessions_df: pd.DataFrame,
    users_list,
    weight_rating,
    extend=True,
):
    user_rating_ = (
        sessions_df.merge(
            tracks_df["duration_ms"],
            how="left",
            left_on=sessions_df["track_id"],
            right_on=tracks_df["id"],
        )
        .drop(["key_0", "session_id"], axis=1)
        .groupby(["user_id", "track_id"])
        .sum()
    )
    user_rating_["rating"] = calc_rating(user_rating_, weight_rating)
    user_rating_ = user_rating_.reset_index()
    user_rating_ = user_rating_.pivot(
        index="user_id", columns="track_id", values="rating"
    )

    if not extend:
        return user_rating_

    user_rating = pd.DataFrame(index=users_list, columns=tracks_df["id"].squeeze()).add(
        user_rating_, fill_value=0
    )
    return user_rating


if __name__ == "__main__":
    sessions_df = pd.read_json("data/transformed_sessions.jsonl", lines=True)
    tracks_df = pd.read_json("data/tracks.jsonl", lines=True)
    users_df = pd.read_json("data/users.jsonl", lines=True)

    users_list = users_df["user_id"].squeeze()
    user_ratings = parse_transformed(tracks_df, sessions_df, users_list, WEIGHT_RATING)

    user_ratings.to_pickle("data/user_ratings.pkl")
