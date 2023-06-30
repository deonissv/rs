import pandas as pd
from typing import List
import numpy as np
from sklearn.neighbors import NearestNeighbors


def cos_rating(
    user_rating: pd.DataFrame,
    users: List[int],
    playlist: List[str],
    knn,
) -> int:
    scaled_rating = user_rating.copy()
    averages = scaled_rating.mean(axis=1,  skipna = True).values
    scaled_rating_ = scaled_rating.fillna(0)
    averages_all = scaled_rating_.mean(axis=1,  skipna = True).values
    for i in range(len(averages_all)):
        if averages_all[i] != 0:
            scaled_rating.iloc[i,:] = (scaled_rating.iloc[i,:] / averages[i])

    scaled_rating = scaled_rating.fillna(0)
    total_ratings = []
    for user_id in users:
        current_rating = np.array([scaled_rating.iloc[user_id-101, :]])
        similarity_list = knn.kneighbors(current_rating, n_neighbors=50)
        playlist_rating = []
        for track_id in playlist:
            rating = scaled_rating[track_id].values[user_id - 101]
            if rating == 0:
                rating = get_similarity(user_id, track_id, scaled_rating, similarity_list)
            playlist_rating.append(rating)
        total_ratings.append(np.mean(playlist_rating) if len(playlist_rating) > 0 else 0)
    return min(total_ratings)

def get_similarity(track_id, user_rating, similarity_list):
    numerator = 0
    denominator = 0
    cos_sim = similarity_list[0][0]
    user_other_id = similarity_list[1][0]
    for idx, user_idx in enumerate(user_other_id):
        other_user_rating = user_rating[track_id].values[user_idx - 101]
        if other_user_rating != 0:
            numerator = numerator + (other_user_rating * cos_sim[idx])
            denominator += cos_sim[idx]

    if denominator == 0:
        expected_rating = 0
    else:
        expected_rating = round(numerator / denominator, 5)
    return expected_rating