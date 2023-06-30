import pandas as pd

columns = [
    "session_id",
    "duration",
    "user_id",
    "track_id",
    "like",
    "skip",
    "play",
]


def transform_track(stack, transformed_sessions):
    track_end = (
        stack[-1]["timestamp"]
        if (stack[-1]["event_type"] == "skip")
        else stack[0]["timestamp"]
    )

    duration = (track_end - stack[0]["timestamp"]).total_seconds()
    like = 0
    skip = 0
    play = 0

    for i in stack:
        if i["event_type"] == "play":
            play += 1
        elif i["event_type"] == "like":
            like += 1
        elif i["event_type"] == "skip":
            skip += 1

    transformed_sessions["session_id"].append(stack[0]["session_id"])
    transformed_sessions["duration"].append(duration)
    transformed_sessions["user_id"].append(stack[0]["user_id"])
    transformed_sessions["track_id"].append(stack[0]["track_id"])
    transformed_sessions["like"].append(like)
    transformed_sessions["skip"].append(skip)
    transformed_sessions["play"].append(play)


def transform_group(group: pd.DataFrame):
    transformed_sessions = {col: [] for col in columns}

    it = group.iterrows()
    stack = [next(it)[1]]
    for _idx, session in it:
        if session["event_type"] == "play":
            transform_track(stack, transformed_sessions)
            stack = []
        stack.append(session)

    if len(stack) == 1:
        transformed_sessions["session_id"].append(stack[0]["session_id"])
        transformed_sessions["duration"].append(0)
        transformed_sessions["user_id"].append(stack[0]["user_id"])
        transformed_sessions["track_id"].append(stack[0]["track_id"])
        transformed_sessions["like"].append(0)
        transformed_sessions["skip"].append(0)
        transformed_sessions["play"].append(1)
    else:
        transform_track(stack, transformed_sessions)

    return pd.DataFrame(transformed_sessions)


def transform_sessions(sessions: pd.DataFrame):
    sessions_filtered = sessions[sessions["event_type"] != "advertisment"]
    groups_list = [group[1] for group in sessions_filtered.groupby("session_id")]
    transformed_groups = [transform_group(group) for group in groups_list]
    transformed_dfs = [pd.DataFrame(group) for group in transformed_groups]
    transformed_sessions = pd.concat(transformed_dfs, axis=0)
    return transformed_sessions


if __name__ == "__main__":
    sessions_df = pd.read_json("data/sessions.jsonl", lines=True)
    print("Data read")

    transformed_sessions = transform_sessions(sessions_df)
    print("Groups transformed")

    transformed_sessions.to_json(
        "data/transformed_sessions.jsonl", lines=True, orient="records"
    )
