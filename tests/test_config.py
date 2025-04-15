import os
import tempfile

basedir = os.path.abspath(os.path.dirname(__file__))

class TestConfig:
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    UPLOAD_FOLDER = tempfile.mkdtemp()
    ANTHROPIC_API_KEY = 'test-api-key'
    CLAUDE_MODEL = 'claude-7-sonnet-20250219'