from datetime import datetime
from app import db

class Analysis(db.Model):
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(500), nullable=False)
    profile_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Metadata columns
    row_count = db.Column(db.Integer)
    column_count = db.Column(db.Integer)
    file_size = db.Column(db.Float)  # in MB
    data_types = db.Column(db.JSON)
    
    def __repr__(self):
        return f'<Analysis {self.title}>' 