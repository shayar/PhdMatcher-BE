from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

def test_find_my_matches(client: TestClient, normal_user_token_headers: dict):
    """Test finding matches for current user"""
    with patch('app.services.matching_service.MatchingService') as mock_service:
        # Mock the matching service
        mock_instance = MagicMock()
        mock_service.return_value = mock_instance
        
        mock_result = {
            "user_id": 1,
            "matches": [],
            "total_matches": 0,
            "processing_time_ms": 50.0
        }
        mock_instance.find_matches.return_value = mock_result
        
        response = client.get("/api/v1/matching/me", headers=normal_user_token_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "user_id" in data
        assert "matches" in data
        assert "total_matches" in data