import pytest
import os
import tempfile
import pandas as pd
from app import create_app, db
from app.utils.csv_parser import save_csv_file, parse_csv_headers, get_csv_sample, validate_csv_file, CSVValidationError
from unittest.mock import patch
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
def test_csv_file(tmp_path):
    # Create a test CSV file
    df = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'score': [85, 90, 95]
    })
    file_path = tmp_path / "test.csv"
    df.to_csv(file_path, index=False)
    return file_path

def test_parse_csv_headers(app, test_csv_file):
    """Test parsing CSV headers"""
    headers = parse_csv_headers(test_csv_file)
    assert headers == ['name', 'age', 'score']

def test_get_csv_sample(app, test_csv_file):
    """Test getting a sample of CSV data"""
    df = get_csv_sample(test_csv_file)
    assert len(df) == 3
    assert list(df.columns) == ['name', 'age', 'score']
    assert df.iloc[0]['name'] == 'Alice'
    assert df.iloc[1]['age'] == 30

def test_save_csv_file(app, test_csv_file, test_user):
    """Test saving a CSV file"""
    with open(test_csv_file, 'rb') as f:
        # Create a file-like object
        from io import BytesIO
        file_obj = BytesIO(f.read())
        file_obj.filename = 'test.csv'
        
        # Save the file and create analysis
        analysis = save_csv_file(
            file_obj,
            user_id=test_user.id,
            title='Test Analysis',
            description='Test Description'
        )
        
        # Verify the analysis was created
        assert analysis is not None
        assert analysis.title == 'Test Analysis'
        assert analysis.user_id == test_user.id
        assert analysis.row_count == 3
        assert analysis.column_count == 3
        
        # Verify the files were saved
        assert os.path.exists(analysis.file_path)
        assert os.path.exists(analysis.profile_path)
        
        # Clean up
        os.remove(analysis.file_path)
        os.remove(analysis.profile_path)
        db.session.delete(analysis)
        db.session.commit()

def test_validate_csv_file(app, test_csv_file):
    """Test CSV file validation"""
    metadata = validate_csv_file(test_csv_file)
    assert metadata['rows'] == 3
    assert metadata['columns'] == 3
    assert metadata['column_names'] == ['name', 'age', 'score']
    assert metadata['has_header'] is True

def test_invalid_csv_file(app):
    """Test handling invalid CSV files"""
    # Create an invalid CSV file
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        f.write(b"This is not a valid CSV file")
        invalid_path = f.name
    
    try:
        with pytest.raises(CSVValidationError):
            validate_csv_file(invalid_path)
    finally:
        os.remove(invalid_path)

def test_save_csv_file_validation_error(app, test_user):
    """Test handling validation errors during file save"""
    # Create an invalid file object
    from io import BytesIO
    file_obj = BytesIO(b"Invalid CSV content")
    file_obj.filename = 'test.csv'

    with pytest.raises(CSVValidationError):
        save_csv_file(file_obj, test_user.id)