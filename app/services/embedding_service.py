"""
Embedding service.

Loads the BAAI/bge-large-en-v1.5 model via SentenceTransformers ONCE
at initialization. Provides single-text and batch encoding methods.
Never reloads the model per request.
"""

from __future__ import annotations

import logging
import time

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config.settings import get_settings
from app.utils.exceptions import ModelLoadError

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating text embeddings using BAAI/bge-large-en-v1.5.

    The model is loaded exactly once during initialization and reused
    for all subsequent requests. This is critical for production
    performance — model loading takes 5-15 seconds, while inference
    takes < 100ms.

    Attributes:
        _model: The loaded SentenceTransformer model instance.
        _model_name: Name of the model from configuration.
        _load_time: Time taken to load the model in seconds.
        _embedding_dimension: Dimensionality of the model output vectors.
        _device: Device the model is running on (cpu/cuda).
    """

    def __init__(self) -> None:
        """
        Initialize the embedding service and load the model.

        Raises:
            ModelLoadError: If the model fails to load.
        """
        settings = get_settings()
        self._model_name = settings.MODEL_NAME
        self._model: SentenceTransformer | None = None
        self._load_time: float = 0.0
        self._embedding_dimension: int = 0
        self._device: str = "cpu"

        self._load_model()

    def _load_model(self) -> None:
        """
        Load the SentenceTransformer model.

        Logs model name, dimension, device, and load time.

        Raises:
            ModelLoadError: If loading fails for any reason.
        """
        logger.info("Loading embedding model: %s ...", self._model_name)
        start = time.perf_counter()

        try:
            self._model = SentenceTransformer(self._model_name)
            self._load_time = time.perf_counter() - start

            # Extract model metadata
            self._device = str(self._model.device)
            self._embedding_dimension = self._model.get_sentence_embedding_dimension()  # type: ignore[assignment]

            # ── Startup Logging ─────────────────────────────────────
            logger.info("=" * 60)
            logger.info("Model Loaded Successfully")
            logger.info("  Model Name      : %s", self._model_name)
            logger.info("  Embedding Dim   : %d", self._embedding_dimension)
            logger.info("  Device          : %s", self._device)
            logger.info("  Load Time       : %.2f sec", self._load_time)
            logger.info("=" * 60)

        except Exception as exc:
            logger.error("Failed to load model '%s': %s", self._model_name, exc)
            raise ModelLoadError(
                f"Failed to load embedding model '{self._model_name}': {exc}"
            ) from exc

    def encode(self, text: str) -> np.ndarray:
        """
        Generate an embedding vector for a single text.

        Args:
            text: Input text to encode.

        Returns:
            1-D numpy array of shape (embedding_dimension,).

        Raises:
            ModelLoadError: If the model is not loaded.
        """
        if self._model is None:
            raise ModelLoadError("Embedding model is not loaded.")

        embedding = self._model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return np.asarray(embedding)

    def encode_batch(self, texts: list[str]) -> list[np.ndarray]:
        """
        Generate embeddings for a batch of texts.

        More efficient than calling ``encode()`` in a loop because
        SentenceTransformer batches internally.

        Args:
            texts: List of input texts to encode.

        Returns:
            List of 1-D numpy arrays, one per input text.

        Raises:
            ModelLoadError: If the model is not loaded.
        """
        if self._model is None:
            raise ModelLoadError("Embedding model is not loaded.")

        if not texts:
            return []

        embeddings = self._model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
            batch_size=32,
        )
        return [np.asarray(e) for e in embeddings]

    def get_model_info(self) -> dict:
        """
        Return metadata about the loaded model.

        Returns:
            Dictionary with model_name, embedding_dimension, device, load_time.
        """
        return {
            "model_name": self._model_name,
            "embedding_dimension": self._embedding_dimension,
            "device": self._device,
            "load_time": f"{self._load_time:.2f} sec",
        }

    @property
    def is_loaded(self) -> bool:
        """Return True if the model is loaded and ready for inference."""
        return self._model is not None

    @property
    def embedding_dimension(self) -> int:
        """Return the dimensionality of the model's output vectors."""
        return self._embedding_dimension

    @property
    def device(self) -> str:
        """Return the device the model is running on."""
        return self._device

    @property
    def model_name(self) -> str:
        """Return the model name."""
        return self._model_name

    @property
    def load_time(self) -> float:
        """Return the model load time in seconds."""
        return self._load_time
