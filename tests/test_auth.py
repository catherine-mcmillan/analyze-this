import pytest
from app import create_app, db, bcrypt
from app.models import User
from tests.config import TestConfig
from flask_login import current_user
from flask import session

@pytest.fixture
def client():
    app = create_app(TestConfig)
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def test_user(client):
    """Create a test user"""
    hashed_password = bcrypt.generate_password_hash('password123').decode('utf-8')
    user = User(
        username='testuser',
        email='test@example.com',
        password=hashed_password
    )
    db.session.add(user)
    db.session.commit()
    return user

def test_register_page(client):
    """Test register page loads correctly"""
    response = client.get('/register')
    assert response.status_code == 200
    assert b'Create an Account' in response.data

def test_register_user(client):
    """Test user registration"""
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password123',
        'confirm_password': 'password123',
        'api_key': ''
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Your account has been created!' in response.data
    
    # Check user was added to database
    user = User.query.filter_by(email='new@example.com').first()
    assert user is not None
    assert user.username == 'newuser'

def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123',
        'remember': False
    }, follow_redirects=True)
    
    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert '_user_id' in sess  # Check that the user is logged in

def test_login_incorrect_password(client, test_user):
    """Test login with incorrect password"""
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'wrongpassword',
        'remember': False
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Login unsuccessful' in response.data

def test_logout(client, test_user):
    """Test logout functionality"""
    # First login
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123',
        'remember': False
    })
    
    # Then logout
    response = client.get('/logout', follow_redirects=True)
    
    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert '_user_id' not in sess  # Check that the user is logged out

def test_profile_update(client, test_user):
    """Test profile update functionality"""
    # First login
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    # Update profile
    response = client.post('/profile', data={
        'username': 'updateduser',
        'email': 'test@example.com',
        'api_key': 'test-api-key',
        'current_password': 'password123',
        'new_password': '',
        'confirm_new_password': ''
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Your profile has been updated!' in response.data
    
    # Check the database was updated
    user = User.query.filter_by(email='test@example.com').first()
    assert user.username == 'updateduser'
    assert user.anthropic_api_key == 'test-api-key'