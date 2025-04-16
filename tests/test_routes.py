import pytest
from app import create_app, db
from app.models import User, Analysis
from flask import url_for
import os
import tempfile
import pandas as pd
from datetime import datetime
from tests.config import TestConfig
from io import BytesIO

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

@pytest.fixture
def test_analysis(app, test_user):
    """Create a test analysis"""
    with app.app_context():
        analysis = Analysis(
            title='Test Analysis',
            description='Test Description',
            file_path='test.csv',
            user_id=test_user.id,
            row_count=100,
            column_count=5,
            file_size=1024,
            data_types={'col1': 'int', 'col2': 'str'}
        )
        db.session.add(analysis)
        db.session.commit()
        return analysis

@pytest.fixture
def test_csv_file(tmp_path):
    df = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'score': [85, 90, 95]
    })
    file_path = tmp_path / "test.csv"
    df.to_csv(file_path, index=False)
    return file_path

def test_home_route(client):
    """Test the home page route"""
    response = client.get('/')
    assert response.status_code == 200

def test_login_route(client):
    """Test the login page route"""
    response = client.get('/auth/login')
    assert response.status_code == 200

def test_register_route(client):
    """Test the register page route"""
    response = client.get('/auth/register')
    assert response.status_code == 200

def test_dashboard_route_unauthorized(client):
    """Test dashboard route without authentication"""
    response = client.get('/dashboard')
    assert response.status_code == 302  # Redirect to login
    assert '/auth/login' in response.location

def test_dashboard_route_authorized(client, test_user):
    """Test dashboard route with authentication"""
    with client:
        # Login the test user
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert b'Dashboard' in response.data

def test_create_analysis_route(client, test_user):
    """Test create analysis route"""
    with client:
        # Login the test user
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        
        response = client.get('/analysis/create')
        assert response.status_code == 200
        assert b'Create Analysis' in response.data

def test_upload_csv_route(client, test_user, test_csv_file):
    """Test CSV upload route"""
    with client:
        # Login the test user
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        
        with open(test_csv_file, 'rb') as f:
            response = client.post('/analysis/upload', data={
                'file': (f, 'test.csv'),
                'title': 'Test Analysis',
                'description': 'Test Description'
            }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Analysis created successfully' in response.data
        
        # Verify the analysis was created
        analysis = Analysis.query.filter_by(title='Test Analysis').first()
        assert analysis is not None
        assert analysis.user_id == test_user.id
        
        # Clean up
        if os.path.exists(analysis.file_path):
            os.remove(analysis.file_path)
        if os.path.exists(analysis.profile_path):
            os.remove(analysis.profile_path)
        db.session.delete(analysis)
        assert b'File uploaded successfully' in response.data

def test_view_analysis_route(client, test_user, test_analysis):
    """Test view analysis route"""
    with client:
        # Login the test user
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        
        response = client.get(f'/analysis/{test_analysis.id}')
        assert response.status_code == 200
        assert b'Test Analysis' in response.data

def test_edit_analysis_route(client, test_user, test_analysis):
    """Test edit analysis route"""
    with client:
        # Login the test user
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        
        response = client.get(f'/analysis/{test_analysis.id}/edit')
        assert response.status_code == 200
        assert b'Edit Analysis' in response.data

def test_delete_analysis_route(client, test_user, test_analysis):
    """Test delete analysis route"""
    with client:
        # Login the test user
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        
        response = client.post(f'/analysis/{test_analysis.id}/delete')
        assert response.status_code == 302  # Redirect after deletion
        assert '/dashboard' in response.location

def test_profile_route(client, test_user):
    """Test profile route"""
    with client:
        # Login the test user
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        
        response = client.get('/profile')
        assert response.status_code == 200
        assert b'Profile' in response.data

def test_password_reset_route(client):
    """Test password reset route"""
    response = client.get('/auth/reset_password')
    assert response.status_code == 200

def test_password_reset_request_route(client, test_user):
    """Test password reset request route"""
    response = client.post('/auth/reset_password_request', data={
        'email': 'test@example.com'
    })
    assert response.status_code == 302  # Redirect after request
    assert '/auth/login' in response.location

def test_password_reset_token_route(client, test_user):
    """Test password reset token route"""
    # Note: In a real test, you would need to generate a valid token
    response = client.get('/auth/reset_password/invalid_token')
    assert response.status_code == 302  # Redirect to home for invalid token
    assert '/' in response.location

def test_dashboard_access(client, test_user):
    """Test dashboard access"""
    with client:
        # First login
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'Password123!',
            'remember': False
        })
        
        # Access dashboard
        response = client.get('/dashboard', follow_redirects=True)
        assert response.status_code == 200
        assert b'Dashboard' in response.data

def test_analysis_creation(client, test_user):
    """Test analysis creation"""
    with client:
        # First login
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'Password123!',
            'remember': False
        })
        
        # Create analysis
        response = client.post('/analysis/new', data={
            'title': 'New Analysis',
            'description': 'New Description',
            'file': (BytesIO(b'col1,col2\n1,2\n3,4'), 'test.csv')
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Analysis created successfully!' in response.data

def test_analysis_view(client, test_user, test_analysis):
    """Test analysis view"""
    with client:
        # First login
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'Password123!',
            'remember': False
        })
        
        # View analysis
        response = client.get(f'/analysis/{test_analysis.id}', follow_redirects=True)
        assert response.status_code == 200
        assert b'Test Analysis' in response.data

def test_analysis_delete(client, test_user, test_analysis):
    """Test analysis deletion"""
    with client:
        # First login
        client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'Password123!',
            'remember': False
        })
        
        # Delete analysis
        response = client.post(f'/analysis/{test_analysis.id}/delete', follow_redirects=True)
        assert response.status_code == 200
        assert b'Analysis deleted successfully!' in response.data
