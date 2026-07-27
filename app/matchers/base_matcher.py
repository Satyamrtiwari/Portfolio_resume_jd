"""
Base matcher.

Abstract base class for all section-wise matchers.
Provides the common cosine similarity computation utility.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class BaseMatcher(ABC):
    """
    Abstract base class for section-wise matching engines.

    All matchers must implement ``score()`` which returns a float
    between 0 and 100 representing the match quality for their
    specific dimension (skills, experience, education, semantic).
    """

    @abstractmethod
    def score(self, *args, **kwargs) -> float:
        """
        Compute a score (0-100) for this matching dimension.

        Returns:
            Float between 0 and 100.
        """
        ...

    @staticmethod
    def compute_cosine_similarity(
        vec_a: np.ndarray,
        vec_b: np.ndarray,
    ) -> float:
        """
        Compute cosine similarity between two vectors.

        Uses sklearn.metrics.pairwise.cosine_similarity internally.

        Args:
            vec_a: First embedding vector (1-D).
            vec_b: Second embedding vector (1-D).

        Returns:
            Cosine similarity value between -1 and 1.
        """
        # Reshape to 2D arrays for sklearn
        a = vec_a.reshape(1, -1)
        b = vec_b.reshape(1, -1)
        similarity = cosine_similarity(a, b)[0][0]
        return float(similarity)
