"""This file makes the models directory a Python package"""
from app.models.analysis import Analysis
from app.models.user import User

__all__ = ['Analysis', 'User'] 