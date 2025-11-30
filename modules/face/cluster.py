from typing import List, Optional, Tuple

import numpy as np
from sklearn.cluster import KMeans


def find_cluster_centroids(embeddings: List, max_k: int = 10) -> np.ndarray:
    """Find optimal cluster centroids using elbow method with early exit."""
    if not embeddings:
        return np.array([])

    embeddings_arr = np.array(embeddings)
    n_samples = len(embeddings_arr)

    # Early exit for small datasets
    if n_samples == 1:
        return embeddings_arr
    if n_samples <= 2:
        return embeddings_arr

    max_k = min(max_k, n_samples)
    if max_k < 2:
        return embeddings_arr

    inertias = []
    all_centroids = []

    for k in range(1, max_k + 1):
        kmeans = KMeans(n_clusters=k, random_state=0, n_init=10)
        kmeans.fit(embeddings_arr)
        inertias.append(kmeans.inertia_)
        all_centroids.append(kmeans.cluster_centers_)

        # Early exit if inertia is negligible
        if kmeans.inertia_ < 1e-6:
            return all_centroids[-1]

    # Find elbow using maximum drop in inertia
    if len(inertias) < 2:
        return all_centroids[0]

    diffs = np.diff(inertias)
    optimal_k_idx = np.argmin(diffs)  # Largest drop (most negative)

    return all_centroids[optimal_k_idx + 1]


def find_closest_centroid(
    centroids: List, normed_face_embedding: np.ndarray
) -> Optional[Tuple[int, np.ndarray]]:
    """Find closest centroid using vectorized cosine similarity."""
    if centroids is None or len(centroids) == 0:
        return None

    centroids_arr = np.asarray(centroids)
    embedding_arr = np.asarray(normed_face_embedding)

    # Vectorized dot product for cosine similarity (embeddings are normalized)
    similarities = centroids_arr @ embedding_arr
    closest_idx = int(np.argmax(similarities))

    return closest_idx, centroids_arr[closest_idx]
