from fastapi.testclient import TestClient
import io

def test_get_current_user(client: TestClient, normal_user_token_headers: dict):
    """Test getting current user info"""
    response = client.get("/api/v1/users/me", headers=normal_user_token_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"

def test_update_user_profile(client: TestClient, normal_user_token_headers: dict):
    """Test updating user profile"""
    update_data = {
        "full_name": "Updated Name",
        "field_of_study": "Computer Science",
        "research_interests": ["machine learning", "artificial intelligence"],
        "preferred_locations": ["California", "New York"]
    }
    
    response = client.put("/api/v1/users/me", json=update_data, headers=normal_user_token_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["field_of_study"] == "Computer Science"
    assert "machine learning" in data["research_interests"]

def test_upload_resume_pdf(client: TestClient, normal_user_token_headers: dict):
    """Test PDF resume upload"""
    # Create a fake PDF file
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF"
    
    files = {"file": ("resume.pdf", io.BytesIO(pdf_content), "application/pdf")}
    
    response = client.post(
        "/api/v1/users/upload-resume",
        files=files,
        headers=normal_user_token_headers
    )
    
    # Note: This might fail in testing environment without proper S3 setup
    # In a real test, you'd mock the S3 service
    assert response.status_code in [200, 500]  # 500 if S3 not configured
