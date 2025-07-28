import pytest
from app.services.embedding_service import EmbeddingService

@pytest.fixture
def embedding_service():
    return EmbeddingService()

def test_encode_text(embedding_service):
    """Test text encoding"""
    text = "This is a test sentence for machine learning research."
    embedding = embedding_service.encode_text(text)
    
    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(x, float) for x in embedding)

def test_encode_batch(embedding_service):
    """Test batch encoding"""
    texts = [
        "Machine learning research",
        "Natural language processing",
        "Computer vision applications"
    ]
    
    embeddings = embedding_service.encode_batch(texts)
    
    assert len(embeddings) == len(texts)
    assert all(isinstance(emb, list) for emb in embeddings)

def test_compute_similarity(embedding_service):
    """Test similarity computation"""
    text1 = "Machine learning research"
    text2 = "Machine learning applications"
    text3 = "Cooking recipes"
    
    emb1 = embedding_service.encode_text(text1)
    emb2 = embedding_service.encode_text(text2)
    emb3 = embedding_service.encode_text(text3)
    
    # Similar texts should have higher similarity
    sim_high = embedding_service.compute_similarity(emb1, emb2)
    sim_low = embedding_service.compute_similarity(emb1, emb3)
    
    assert 0 <= sim_high <= 1
    assert 0 <= sim_low <= 1
    assert sim_high > sim_low