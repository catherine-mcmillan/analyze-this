# This file makes the forms directory a Python package 

from app.forms.auth import (
    LoginForm, RegistrationForm, UpdateProfileForm,
    ResetPasswordRequestForm, ResetPasswordForm
)
from app.forms.analysis import UploadCSVForm, PromptForm, ReviewPromptForm

__all__ = [
    'LoginForm', 'RegistrationForm', 'UpdateProfileForm',
    'ResetPasswordRequestForm', 'ResetPasswordForm',
    'UploadCSVForm', 'PromptForm', 'ReviewPromptForm'
] 