"""离线单元测试: 嵌入器 (HashEmbedder)。"""
from embeddings.mock import HashEmbedder


def test_deterministic():
    e = HashEmbedder(dim=128)
    v1 = e.embed(["hello world 晨星"])
    v2 = e.embed(["hello world 晨星"])
    assert v1 == v2


def test_similar_higher_than_dissimilar():
    e = HashEmbedder(dim=256)
    a, b, c = e.embed(["机器学习模型训练", "深度学习模型训练", "足球比赛直播比分"])
    from vectorstore.base import cosine

    assert cosine(a, b) > cosine(a, c)


def test_dim():
    e = HashEmbedder(dim=64)
    assert e.dim == 64
    assert len(e.embed(["x"])[0]) == 64
