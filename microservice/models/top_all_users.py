import pandas as pd
from typing import List


class TopAllModel:
    def __init__(self, num_tracks, *args, **kwargs):
        self.number_of_tracks = num_tracks

    def fit(self, X: pd.DataFrame, y=None):
        self._user_rating = X.fillna(0)

    def update(self, X: pd.DataFrame):
        self._user_rating = X.fillna(0)

    def predict(self, X: pd.DataFrame) -> List[str]:
        average = self._user_rating.where(lambda x: x != 0).mean()
        recommends_df = average.sort_values(ascending=False).head(self.number_of_tracks)
        return list(recommends_df.index)
