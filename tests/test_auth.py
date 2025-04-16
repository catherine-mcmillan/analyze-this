import pytest
from app import create_app, db, bcrypt
from app.models import User
from tests.config import TestConfig
from flask_login import current_user
from flask import session

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def test_user(app):
    """Create a test user"""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            anthropic_api_key='test-api-key'
        )
        user.set_password('Password123!')
        db.session.add(user)
        db.session.commit()
        return user

def test_register_page(client):
    """Test register page loads correctly"""
    response = client.get('/auth/register')
    assert response.status_code == 200

def test_register_user(client):
    """Test user registration"""
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password123',
        'confirm_password': 'password123',
        'api_key': ''
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Congratulations, you are now a registered user!' in response.data
    
    # Check user was added to database
    user = User.query.filter_by(email='new@example.com').first()
    assert user is not None
    assert user.username == 'newuser'

def test_login_route(client):
    """Test the login page route"""
    response = client.get('/auth/login')
    assert response.status_code == 200

def test_password_reset_route(client):
    """Test password reset route"""
    response = client.get('/auth/reset_password')
    assert response.status_code == 200

def test_login_success(client, test_user):
    """Test successful login"""
    with client:
        response = client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'Password123!',
            'remember': False
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Dashboard' in response.data

def test_login_incorrect_password(client, test_user):
    """Test login with incorrect password"""
    response = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'wrongpassword',
        'remember': False
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data

def test_logout(client, test_user):
    """Test logout functionality"""
    with client:
        # First login
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'Password123!',
            'remember': False
        })
        
        # Then logout
        response = client.get('/auth/logout', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Welcome to Analyze This' in response.data

def test_profile_update(client, test_user):
    """Test profile update functionality"""
    with client:
        # First login
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'Password123!',
            'remember': False
        })
        
        # Update profile
        response = client.post('/auth/profile', data={
            'username': 'updateduser',
            'email': 'test@example.com',
            'api_key': 'new-api-key',
            'current_password': 'Password123!',
            'new_password': '',
            'confirm_new_password': ''
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Your profile has been updated!' in response.data
        
        # Check the database was updated
        user = User.query.filter_by(email='test@example.com').first()
        assert user.username == 'updateduser'
        assert user.anthropic_api_key == 'new-api-key'