import pytest
import os
import tempfile
import pandas as pd
from app import create_app
from app.utils.csv_parser import save_csv_file, parse_csv_headers, get_csv_sample
from tests.config import TestConfig

@pytest.fixture
def app():
    app = create_app(TestConfig)
    
    with app.app_context():
        yield app

@pytest.fixture
def test_csv_file():
    """Create a temporary CSV file for testing"""
    fd, path = tempfile.mkstemp(suffix='.csv')
    try:
        with os.fdopen(fd, 'w') as f:
            f.write("id,name,value\n")
            f.write("1,test1,10.5\n")
            f.write("2,test2,20.3\n")
            f.write("3,test3,30.1\n")
        yield path
    finally:
        os.unlink(path)

def test_parse_csv_headers(app, test_csv_file):
    """Test parsing CSV headers"""
    headers = parse_csv_headers(test_csv_file)
    assert headers == ['id', 'name', 'value']

def test_get_csv_sample(app, test_csv_file):
    """Test getting a sample of CSV data"""
    df = get_csv_sample(test_csv_file)
    assert len(df) == 3
    assert list(df.columns) == ['id', 'name', 'value']
    assert df.iloc[0]['name'] == 'test1'
    assert df.iloc[1]['value'] == 20.3

def test_save_csv_file(app):
    """Test saving a CSV file"""
    # Create test CSV content
    test_data = "id,name,value\n1,test1,10.5\n"
    
    # Create a temporary test file
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
        temp_file.write(test_data.encode('utf-8'))
        temp_path = temp_file.name
    
    try:
        # Create an in-memory file-like object to simulate a file upload
        from io import BytesIO
        file_obj = BytesIO(test_data.encode('utf-8'))
        file_obj.filename = 'test.csv'
        
        # Save the file
        saved_path = save_csv_file(file_obj, 'saved_test.csv')
        
        # Check the file exists and has correct content
        assert os.path.exists(saved_path)
        with open(saved_path, 'r') as f:
            content = f.read()
        assert content == test_data
        
        # Clean up
        os.unlink(saved_path)
    finally:
        # Clean up the original temp file
        os.unlink(temp_path)

def test_handle_invalid_csv(app):
    """Test handling invalid CSV files"""
    # Create an invalid CSV file
    fd, path = tempfile.mkstemp(suffix='.csv')
    try:
        with os.fdopen(fd, 'w') as f:
            f.write("This is not a valid CSV file")
        
        # Test that an exception is raised when parsing headers
        with pytest.raises(ValueError):
            parse_csv_headers(path)
    finally:
        os.unlink(path)