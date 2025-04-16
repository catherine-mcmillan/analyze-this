import pandas as pd
import os
import csv
from werkzeug.utils import secure_filename
from flask import current_app
import logging
from ydata_profiling import ProfileReport
from wtforms import ValidationError
from datetime import datetime
import json

class CSVValidationError(Exception):
    """Custom exception for CSV validation errors"""
    pass

class CSVFileValidator:
    """WTForms validator for CSV file uploads"""
    def __init__(self, message=None):
        if not message:
            message = 'Invalid CSV file'
        self.message = message

    def __call__(self, form, field):
        if not field.data:
            raise ValidationError('No file selected')
        
        filename = secure_filename(field.data.filename)
        if not filename.lower().endswith('.csv'):
            raise ValidationError('File must be a CSV')
        
        if field.data.content_length > 10 * 1024 * 1024:  # 10MB limit
            raise ValidationError('File size must be less than 10MB')

def validate_csv_file(file_path):
    """Validate a CSV file and return metadata"""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            raise CSVValidationError('File does not exist')

        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > 10 * 1024 * 1024:  # 10MB limit
            raise CSVValidationError('File size exceeds 10MB limit')

        # Try to read the CSV file
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            raise CSVValidationError(f'Invalid CSV format: {str(e)}')

        # Get metadata
        metadata = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'file_size': file_size,
            'data_types': df.dtypes.astype(str).to_dict(),
            'columns': df.columns.tolist()
        }

        return metadata

    except Exception as e:
        raise CSVValidationError(f'Error validating CSV: {str(e)}')

def save_csv_file(file, user_id):
    """Save uploaded CSV file and generate profile"""
    try:
        # Create user directory if it doesn't exist
        user_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id))
        os.makedirs(user_dir, exist_ok=True)

        # Save the file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(user_dir, f'{timestamp}_{filename}')
        file.save(file_path)

        # Validate the file
        metadata = validate_csv_file(file_path)

        # Generate data profile
        df = pd.read_csv(file_path)
        profile = ProfileReport(df, title=f"Data Profile - {filename}")
        profile_path = file_path.replace('.csv', '_profile.html')
        profile.to_file(profile_path)

        return {
            'file_path': file_path,
            'profile_path': profile_path,
            **metadata
        }

    except Exception as e:
        # Clean up if something goes wrong
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise CSVValidationError(f'Error processing CSV: {str(e)}')

def parse_csv_headers(file_path):
    """Parse CSV headers"""
    try:
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            return headers
    except Exception as e:
        raise CSVValidationError(f'Error parsing CSV headers: {str(e)}')

def get_csv_sample(file_path, n_rows=5):
    """Get a sample of the CSV data"""
    try:
        df = pd.read_csv(file_path)
        return df.head(n_rows).to_dict('records')
    except Exception as e:
        raise CSVValidationError(f'Error getting CSV sample: {str(e)}')

def get_csv_stats(file_path):
    """Get basic statistics for numeric columns"""
    try:
        df = pd.read_csv(file_path)
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        stats = {}
        for col in numeric_cols:
            stats[col] = {
                'mean': df[col].mean(),
                'std': df[col].std(),
                'min': df[col].min(),
                'max': df[col].max(),
                'median': df[col].median()
            }
        return stats
    except Exception as e:
        raise CSVValidationError(f'Error calculating statistics: {str(e)}')