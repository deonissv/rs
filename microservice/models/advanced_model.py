import pandas as pd
from typing import List
import numpy as np
from sklearn.neighbors import NearestNeighbors


class AdvancedModel:
    def __init__(self, num_tracks, *args, **kwargs):
        self.number_of_tracks = num_tracks
        self.model_knn = NearestNeighbors(metric = 'cosine',
                                          algorithm = 'brute')

    def fit(self, X: pd.DataFrame, y=None):
        self._user_rating = X

        self._scaled_rating = self._user_rating.copy()
        averages = self._scaled_rating.mean(axis=1, skipna=True).values
        for col in self._scaled_rating.columns:
            self._scaled_rating[col] = self._scaled_rating[col].div(averages)

        self._scaled_rating = self._scaled_rating.fillna(0)
        self.model_knn.fit(self._scaled_rating)

    def update(self, X: pd.DataFrame, y=None):
        self._user_rating = X

        self._scaled_rating = self._user_rating.copy()
        averages = self._scaled_rating.mean(axis=1, skipna=True).values
        for col in self._scaled_rating.columns:
            self._scaled_rating[col] = self._scaled_rating[col].div(averages)
        self._scaled_rating = self._scaled_rating.fillna(0)
        self.model_knn.fit(self._scaled_rating)

    def predict(self, X: pd.DataFrame):

        X = self.check_correctness(X)
        if len(X) == 0:
            average = self._user_rating.where(lambda x: x != 0).mean()
            recommends_df = (
                average.sort_values(ascending=False)
                .head(self.number_of_tracks)
            )
            return list(recommends_df.index)


        avg_user = self._average_users(X.values)
        current_rating = np.array([avg_user.iloc[:]])
        similarity_list = self.model_knn.kneighbors(current_rating, n_neighbors=50)
        for track_id in self._user_rating.columns:
            if avg_user[track_id] == 0:
                avg_user[track_id] = self.get_similarity(
                    track_id, self._scaled_rating, similarity_list
                )

        recommends_df = avg_user.sort_values(ascending=False).head(
            self.number_of_tracks
        )
        return list(recommends_df.index)

    def _average_users(self, users: List[int]):
        users = [self.user_id_to_idx(user) for user in users]
        average = (
            self._scaled_rating.iloc[users].where(lambda x: x != 0).mean().fillna(0)
        )
        return average

    def check_correctness(self, X: pd.DataFrame):
        to_drop = []
        for user in X.values:
            idx = self.user_id_to_idx(user)
            count = (self._scaled_rating.iloc[idx] != 0).sum()
            if count < 20: to_drop.append(idx)
        X.drop(labels=to_drop, inplace=True)
        return X

    def user_id_to_idx(self, user_id: int) -> int:
        return user_id - 101

    def idx_to_user_id(self, idx: int) -> int:
        return idx + 101

    def get_similarity(self, track_id, user_rating, similarity_list):
        numerator = 0
        denominator = 0
        cos_sim = similarity_list[0][0]
        user_other_id = similarity_list[1][0]
        for idx, user_idx in enumerate(user_other_id):
            other_user_rating = user_rating[track_id].values[self.user_id_to_idx(user_idx)]
            if other_user_rating != 0:
                numerator = numerator + (other_user_rating * cos_sim[idx])
                denominator += cos_sim[idx]

        if denominator == 0:
            expected_rating = 0
        else:
            expected_rating = round(numerator / denominator, 5)
        return expected_rating