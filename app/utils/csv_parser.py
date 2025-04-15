import pandas as pd
import os
from werkzeug.utils import secure_filename
from flask import current_app

def save_csv_file(file, filename=None):
    """
    Save a CSV file to the upload folder
    
    Args:
        file: The file object from the request
        filename: Optional custom filename
        
    Returns:
        The saved file path
    """
    if filename is None:
        filename = secure_filename(file.filename)
    
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    return file_path

def parse_csv_headers(file_path):
    """
    Parse a CSV file and return its headers/column names
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        List of column headers
    """
    try:
        df = pd.read_csv(file_path, nrows=0)  # Only read header row
        return list(df.columns)
    except Exception as e:
        current_app.logger.error(f"Error parsing CSV headers: {str(e)}")
        raise ValueError(f"Unable to parse CSV file: {str(e)}")

def get_csv_sample(file_path, rows=5):
    """
    Get a sample of the CSV data
    
    Args:
        file_path: Path to the CSV file
        rows: Number of rows to sample
        
    Returns:
        DataFrame containing the sample data
    """
    try:
        df = pd.read_csv(file_path, nrows=rows)
        return df
    except Exception as e:
        current_app.logger.error(f"Error sampling CSV data: {str(e)}")
        raise ValueError(f"Unable to read CSV file: {str(e)}")