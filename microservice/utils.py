import json
from typing import List, Optional


def get_group(users: List[str], groups_number: int = 2) -> int:
    assert groups_number > 1
    return hash(tuple(sorted(users))) % groups_number


def fmt_predict_log_msg(users: List[str], tracks: List[str]) -> str:
    return f'"users": {json.dumps(users)}, "tracks": {json.dumps(tracks)}'


def fmt_ab_log_msg(
    users: List[str], tracks: List[str], group: Optional[int] = None
) -> str:
    return f'"group": {group}, "users": {json.dumps(users)}, "tracks": {json.dumps(tracks)}'
