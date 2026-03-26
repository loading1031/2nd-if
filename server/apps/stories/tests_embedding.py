"""임베딩 유틸리티 테스트 (cosine_similarity는 순수 함수, get_embedding은 skipif)."""

import os

import pytest

from apps.stories.embedding import cosine_similarity, get_embedding


class TestCosineSimilarity:
    """cosine_similarity 순수 함수 테스트."""

    def test_identical_vectors(self):
        a = [1.0, 2.0, 3.0]
        assert cosine_similarity(a, a) == pytest.approx(1.0)

    def test_orthogonal_vectors(self):
        a = [1.0, 0.0]
        b = [0.0, 1.0]
        assert cosine_similarity(a, b) == pytest.approx(0.0)

    def test_opposite_vectors(self):
        a = [1.0, 0.0]
        b = [-1.0, 0.0]
        assert cosine_similarity(a, b) == pytest.approx(-1.0)

    def test_zero_vector(self):
        a = [0.0, 0.0]
        b = [1.0, 2.0]
        assert cosine_similarity(a, b) == 0.0

    def test_both_zero_vectors(self):
        a = [0.0, 0.0]
        assert cosine_similarity(a, a) == 0.0

    def test_similar_vectors_high_score(self):
        a = [1.0, 2.0, 3.0]
        b = [1.1, 2.1, 3.1]
        sim = cosine_similarity(a, b)
        assert sim > 0.99

    def test_different_vectors_lower_score(self):
        a = [1.0, 0.0, 0.0]
        b = [0.0, 0.0, 1.0]
        assert cosine_similarity(a, b) == pytest.approx(0.0)

    def test_single_dimension(self):
        a = [5.0]
        b = [3.0]
        assert cosine_similarity(a, b) == pytest.approx(1.0)


@pytest.mark.skipif(
    not os.environ.get("OLLAMA_URL"),
    reason="Ollama not available",
)
class TestGetEmbedding:
    @pytest.mark.asyncio
    async def test_returns_list_of_floats(self):
        result = await get_embedding("hello world")
        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], float)
