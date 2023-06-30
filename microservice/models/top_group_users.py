import pandas as pd
from typing import List


class TopGroupModel:
    def __init__(self, num_tracks, *args, **kwargs):
        self.number_of_tracks = num_tracks

    def fit(self, X: pd.DataFrame, y=None):
        self._user_rating = X

    def update(self, X: pd.DataFrame):
        self._user_rating = X.fillna(0)

    def predict(self, X: pd.DataFrame) -> List[str]:
        avg_user = self._average_users(X.values)
        recommends_df = avg_user.sort_values(ascending=False).head(
            self.number_of_tracks
        )
        return list(recommends_df.index)

    def _average_users(self, users: List[int]):
        users = [self.user_id_to_idx(user) for user in users]
        average = self._user_rating.iloc[users].mean(skipna=True)
        return average

    def user_id_to_idx(self, user_id: int) -> int:
        return user_id - 101

    def idx_to_user_id(self, idx: int) -> int:
        return idx + 101
