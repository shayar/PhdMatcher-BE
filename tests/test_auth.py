from fastapi.testclient import TestClient

def test_register_user(client: TestClient):
    """Test user registration"""
    user_data = {
        "email": "newuser@example.com",
        "password": "password123",
        "full_name": "New User"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_register_duplicate_email(client: TestClient):
    """Test registration with duplicate email"""
    user_data = {
        "email": "duplicate@example.com",
        "password": "password123",
        "full_name": "User One"
    }
    
    # First registration
    response1 = client.post("/api/v1/auth/register", json=user_data)
    assert response1.status_code == 200
    
    # Second registration with same email
    user_data["full_name"] = "User Two"
    response2 = client.post("/api/v1/auth/register", json=user_data)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]

def test_login_success(client: TestClient):
    """Test successful login"""
    # Register user first
    user_data = {
        "email": "logintest@example.com",
        "password": "password123",
        "full_name": "Login Test"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Test login
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client: TestClient):
    """Test login with invalid credentials"""
    login_data = {
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_test_token(client: TestClient, normal_user_token_headers: dict):
    """Test token validation"""
    response = client.post("/api/v1/auth/test-token", headers=normal_user_token_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "email" in data
    assert "id" in data