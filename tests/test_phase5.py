"""
Phase 5 Verification Tests & Benchmarks.

Tests:
1. EmbeddingService initialization & model load time measurement (ONCE)
2. Single-text embedding vector shape (1024,) and unit norm verification
3. Single-text embedding latency benchmark (ms)
4. Batch embedding latency benchmark (ms)
5. Semantic cosine similarity sanity checks
"""

import sys
import time
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.embedding_service import EmbeddingService


@pytest.fixture(scope="module")
def embedding_service():
    """Module-scoped fixture so model is loaded ONCE for all Phase 5 tests."""
    start = time.perf_counter()
    service = EmbeddingService()
    load_duration = time.perf_counter() - start
    print(f"\n[BENCHMARK] Model Load Time: {load_duration:.3f} sec (Cached Load: {service.load_time:.3f} sec)")
    return service


def test_model_loading_and_properties(embedding_service):
    """Verify model initialization, dimension, device, and properties."""
    assert embedding_service.is_loaded is True
    assert embedding_service.model_name == "BAAI/bge-large-en-v1.5"
    assert embedding_service.embedding_dimension == 1024
    assert embedding_service.device in ("cpu", "cuda")
    assert embedding_service.load_time > 0.0


def test_single_embedding_shape_and_latency(embedding_service):
    """Measure single text embedding latency and verify output vector shape and normalization."""
    # Warmup call for PyTorch JIT setup
    embedding_service.encode("Warmup text")

    sample_text = "Senior Backend Engineer with 5 years experience in Python, FastAPI, Docker, and PostgreSQL."

    start = time.perf_counter()
    vector = embedding_service.encode(sample_text)
    latency_ms = (time.perf_counter() - start) * 1000.0

    print(f"\n[BENCHMARK] Single Text Embedding Latency (Warm): {latency_ms:.2f} ms")

    assert isinstance(vector, np.ndarray)
    assert vector.shape == (1024,)
    # Verify L2 normalization: ||v||_2 should be ~1.0
    norm = np.linalg.norm(vector)
    assert abs(norm - 1.0) < 1e-4
    assert latency_ms < 10000.0  # CPU execution threshold


def test_batch_embedding_latency(embedding_service):
    """Measure batch text embedding latency for 10 document sections."""
    sections = [
        "Technical Skills: Python, FastAPI, Docker, AWS, PostgreSQL",
        "Professional Experience: Senior Engineer at TechCorp",
        "Responsibilities: Designed REST APIs handling 5M daily requests",
        "Education: Bachelor of Science in Computer Science",
        "Projects: AI Resume Matcher using SentenceTransformers",
        "Requirements: 3+ years experience in Python backend development",
        "Qualifications: Strong knowledge of PostgreSQL and Redis",
        "Certifications: AWS Certified Solutions Architect",
        "Soft Skills: Leadership, Agile development, Problem solving",
        "Summary: Passionate backend developer building cloud applications",
    ]

    start = time.perf_counter()
    vectors = embedding_service.encode_batch(sections)
    batch_latency_ms = (time.perf_counter() - start) * 1000.0

    print(f"\n[BENCHMARK] Batch Embedding Latency (10 items): {batch_latency_ms:.2f} ms (Avg: {batch_latency_ms/10:.2f} ms/item)")

    assert len(vectors) == 10
    assert all(v.shape == (1024,) for v in vectors)
    assert batch_latency_ms < 10000.0


def test_semantic_similarity_sanity(embedding_service):
    """Verify semantic closeness between related vs unrelated text pairs."""
    vec_resume = embedding_service.encode("Python FastAPI Backend Engineer building microservices")
    vec_jd_match = embedding_service.encode("Python Backend Developer experienced in FastAPI and APIs")
    vec_jd_diff = embedding_service.encode("Registered Nurse specializing in clinical patient care and EHR")

    sim_high = float(np.dot(vec_resume, vec_jd_match))
    sim_low = float(np.dot(vec_resume, vec_jd_diff))

    print(f"\n[BENCHMARK] High Similarity (Backend vs Backend): {sim_high:.4f}")
    print(f"[BENCHMARK] Low Similarity (Backend vs Nursing): {sim_low:.4f}")

    assert sim_high > 0.80
    assert sim_low < 0.50
    assert sim_high > sim_low
