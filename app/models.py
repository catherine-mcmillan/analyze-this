from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime, timedelta
from datetime import datetime
import json

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    anthropic_api_key = db.Column(db.String(128))
    analyses = db.relationship('Analysis', backref='user', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    column_annotations = db.Column(db.Text)  # JSON string of column annotations
    prompt = db.Column(db.Text)
    enhanced_prompt = db.Column(db.Text)
    report = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_column_annotations(self, annotations):
        self.column_annotations = json.dumps(annotations)
    
    def get_column_annotations(self):
        return json.loads(self.column_annotations) if self.column_annotations else {}
    
    def __repr__(self):
        return f'<Analysis {self.title}>'