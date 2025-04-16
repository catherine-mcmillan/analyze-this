from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Analysis
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('home.html', title='Home')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Get user's analyses
    analyses = Analysis.query.filter_by(user_id=current_user.id).order_by(Analysis.created_at.desc()).all()
    
    # Calculate stats for dashboard
    total_analyses = len(analyses)
    completed_analyses = sum(1 for a in analyses if a.report)
    recent_analyses = analyses[:5] if analyses else []
    
    # Get data for charts
    monthly_counts = get_monthly_analysis_counts(current_user.id)
    column_types = get_column_type_distribution(analyses)
    
    return render_template(
        'dashboard.html', 
        title='Dashboard',
        analyses_count=total_analyses,
        completed_count=completed_analyses,
        recent_analyses=recent_analyses,
        monthly_counts=monthly_counts,
        column_types=column_types
    )

def get_monthly_analysis_counts(user_id):
    """Get analysis counts by month for the past year"""
    # Get current date and date 1 year ago
    now = datetime.utcnow()
    year_ago = now - timedelta(days=365)
    
    # Query to get analyses by month
    analyses = Analysis.query.filter(
        Analysis.user_id == user_id,
        Analysis.created_at >= year_ago
    ).all()
    
    # Group by month
    months = {}
    for analysis in analyses:
        month_key = analysis.created_at.strftime('%Y-%m')
        if month_key not in months:
            months[month_key] = 0
        months[month_key] += 1
    
    # Create list of last 12 months
    result = []
    for i in range(12):
        month_date = now - timedelta(days=30 * i)
        month_key = month_date.strftime('%Y-%m')
        month_name = month_date.strftime('%b %Y')
        result.append({
            'month': month_name,
            'count': months.get(month_key, 0)
        })
    
    # Reverse to get chronological order
    return list(reversed(result))

def get_column_type_distribution(analyses):
    """Get distribution of column types from all analyses"""
    types = {
        'numeric': 0,
        'text': 0,
        'datetime': 0,
        'boolean': 0,
        'other': 0
    }
    
    for analysis in analyses:
        if not analysis.column_annotations:
            continue
            
        annotations = analysis.get_column_annotations()
        for column, annotation in annotations.items():
            column_type = 'other'
            description = annotation.get('description', '').lower()
            
            if any(term in description for term in ['number', 'numeric', 'int', 'float', 'count', 'amount']):
                column_type = 'numeric'
            elif any(term in description for term in ['date', 'time', 'year', 'month']):
                column_type = 'datetime'
            elif any(term in description for term in ['text', 'string', 'name', 'description']):
                column_type = 'text'
            elif any(term in description for term in ['boolean', 'bool', 'flag', 'true/false', 'yes/no']):
                column_type = 'boolean'
                
            types[column_type] += 1
    
    return types