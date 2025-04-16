from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from datetime import datetime
import json
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    # Store encrypted API key
    _anthropic_api_key = db.Column(db.Text)
    # User preferences
    preferences = db.Column(db.Text, default='{}')
    analyses = db.relationship('Analysis', backref='user', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    @property
    def anthropic_api_key(self):
        """Return decrypted API key if exists."""
        if not self._anthropic_api_key:
            return None
        
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            # Decrypt the API key
            decrypted_data = s.loads(self._anthropic_api_key)
            return decrypted_data.get('key')
        except:
            # If decryption fails, return None
            return None
    
    @anthropic_api_key.setter
    def anthropic_api_key(self, api_key):
        """Encrypt and store API key."""
        if not api_key:
            self._anthropic_api_key = None
            return
            
        s = Serializer(current_app.config['SECRET_KEY'])
        self._anthropic_api_key = s.dumps({'key': api_key}).decode('utf-8')
    
    def set_password(self, password):
        """Set hashed password."""
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        """Verify password against hash."""
        return check_password_hash(self.password, password)
    
    def get_preferences(self):
        """Get user preferences as dictionary."""
        try:
            return json.loads(self.preferences) if self.preferences else {}
        except:
            return {}
    
    def set_preferences(self, preferences_dict):
        """Store user preferences."""
        self.preferences = json.dumps(preferences_dict)
    
    def get_reset_token(self, expires_sec=1800):
        """Generate password reset token."""
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        """Verify password reset token."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
            return User.query.get(user_id)
        except:
            return None
    
    def update_last_login(self):
        """Update last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    report = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data_file = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed

    def __repr__(self):
        return f'<Analysis {self.title}>'