"""
Embedding service.

Supports dual-engine architecture:
- Production: FastEmbed (ONNX Runtime engine) — consumes ~60 MB RAM (zero OOM on Render Free Tier).
- Development: SentenceTransformers (PyTorch engine) — full local embedding feature set.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any

import numpy as np

try:
    from fastembed import TextEmbedding
    _HAS_FASTEMBED = True
except ImportError:
    TextEmbedding = None  # type: ignore[assignment, misc]
    _HAS_FASTEMBED = False

from sentence_transformers import SentenceTransformer

from app.config.settings import get_settings
from app.utils.exceptions import ModelLoadError

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating text embeddings using BAAI/bge models.

    Supports non-blocking background initialization so the web server starts
    and binds its port instantly (< 0.1s), preventing cloud deployment timeouts.
    Auto-detects FastEmbed (ONNX) in production for lightweight memory footprint (~60 MB RAM).

    Attributes:
        _model: The loaded model instance (FastEmbed or SentenceTransformer).
        _model_name: Name of the model from configuration.
        _engine: Engine used ('fastembed' or 'sentence-transformers').
        _load_time: Time taken to load the model in seconds.
        _embedding_dimension: Dimensionality of the model output vectors.
        _device: Device the model is running on (cpu/cuda).
    """

    def __init__(self) -> None:
        """
        Initialize the embedding service without blocking server startup.
        """
        settings = get_settings()
        self._model_name = settings.MODEL_NAME
        self._model: Any = None
        self._engine: str = "fastembed" if _HAS_FASTEMBED else "sentence-transformers"
        self._load_time: float = 0.0
        self._embedding_dimension: int = 384 if "small" in settings.MODEL_NAME else 1024
        self._device: str = "cpu"
        self._load_lock = threading.Lock()
        self._is_loading: bool = False

    def preload_background(self) -> None:
        """Start a non-blocking background thread to load the model without delaying server startup."""
        if self._model is None and not self._is_loading:
            thread = threading.Thread(target=self._ensure_model_loaded, daemon=True)
            thread.start()

    def _ensure_model_loaded(self) -> None:
        """Ensure the embedding model is loaded into memory thread-safely."""
        if self._model is not None:
            return
        with self._load_lock:
            if self._model is None:
                self._is_loading = True
                try:
                    self._load_model()
                finally:
                    self._is_loading = False

    def _load_model(self) -> None:
        """
        Load the embedding model using FastEmbed (ONNX) if available, or SentenceTransformers fallback.
        """
        logger.info("Loading embedding model '%s' via engine '%s' ...", self._model_name, self._engine)
        start = time.perf_counter()

        try:
            if self._engine == "fastembed" and _HAS_FASTEMBED:
                self._model = TextEmbedding(model_name=self._model_name)
                # Benchmark embedding dimension
                dummy_emb = list(self._model.embed(["test"]))[0]
                self._embedding_dimension = len(dummy_emb)
                self._device = "cpu (ONNX Runtime)"
            else:
                self._engine = "sentence-transformers"
                self._model = SentenceTransformer(self._model_name)
                self._device = str(self._model.device)
                self._embedding_dimension = self._model.get_sentence_embedding_dimension()  # type: ignore[assignment]

            self._load_time = time.perf_counter() - start

            # ── Startup Logging ─────────────────────────────────────
            logger.info("=" * 60)
            logger.info("Embedding Engine Loaded Successfully")
            logger.info("  Engine Name     : %s", self._engine)
            logger.info("  Model Name      : %s", self._model_name)
            logger.info("  Embedding Dim   : %d", self._embedding_dimension)
            logger.info("  Device          : %s", self._device)
            logger.info("  Load Time       : %.2f sec", self._load_time)
            logger.info("=" * 60)

        except Exception as exc:
            # If FastEmbed fails to load specific model name, try SentenceTransformers fallback
            if self._engine == "fastembed":
                logger.warning("FastEmbed load failed (%s). Falling back to SentenceTransformers ...", exc)
                try:
                    self._engine = "sentence-transformers"
                    self._model = SentenceTransformer(self._model_name)
                    self._device = str(self._model.device)
                    self._embedding_dimension = self._model.get_sentence_embedding_dimension()  # type: ignore[assignment]
                    self._load_time = time.perf_counter() - start
                    return
                except Exception as inner_exc:
                    exc = inner_exc

            logger.error("Failed to load model '%s': %s", self._model_name, exc)
            raise ModelLoadError(
                f"Failed to load embedding model '{self._model_name}': {exc}"
            ) from exc

    def encode(self, text: str) -> np.ndarray:
        """
        Generate an embedding vector for a single text.
        """
        self._ensure_model_loaded()
        if self._model is None:
            raise ModelLoadError("Embedding model is not loaded.")

        if self._engine == "fastembed":
            raw_emb = list(self._model.embed([text]))[0]
            norm = np.linalg.norm(raw_emb)
            if norm > 0:
                raw_emb = raw_emb / norm
            return np.asarray(raw_emb)

        embedding = self._model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return np.asarray(embedding)

    def encode_batch(self, texts: list[str]) -> list[np.ndarray]:
        """
        Generate embeddings for a batch of texts.
        """
        self._ensure_model_loaded()
        if self._model is None:
            raise ModelLoadError("Embedding model is not loaded.")

        if not texts:
            return []

        if self._engine == "fastembed":
            raw_embs = list(self._model.embed(texts))
            normalized = []
            for e in raw_embs:
                arr = np.asarray(e)
                norm = np.linalg.norm(arr)
                if norm > 0:
                    arr = arr / norm
                normalized.append(arr)
            return normalized

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
        """
        return {
            "engine": self._engine,
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
