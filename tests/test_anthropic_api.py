import pytest
from unittest.mock import MagicMock, patch
from app.utils.anthropic_api import generate_analysis, AnthropicAPIError
from app import create_app, db
from tests.config import TestConfig

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
def mock_anthropic():
    with patch('app.utils.anthropic_api.anthropic') as mock:
        yield mock

def test_generate_analysis_success(app, mock_anthropic):
    with app.app_context():
        # Mock the Anthropic API response
        mock_response = MagicMock()
        mock_response.content = [{"type": "text", "text": "Test analysis result"}]
        mock_anthropic.Anthropic.return_value.messages.create.return_value = mock_response
        
        # Test the function
        result = generate_analysis("Test prompt")
        assert result == "Test analysis result"

def test_generate_analysis_api_error(app, mock_anthropic):
    with app.app_context():
        # Mock the Anthropic API to raise an exception
        mock_anthropic.Anthropic.return_value.messages.create.side_effect = Exception("API Error")
        
        # Test the function
        with pytest.raises(AnthropicAPIError):
            generate_analysis("Test prompt")

def test_generate_analysis_no_api_key(app, mock_anthropic):
    with app.app_context():
        # Test with no API key
        app.config['ANTHROPIC_API_KEY'] = None
        with pytest.raises(AnthropicAPIError):
            generate_analysis("Test prompt")