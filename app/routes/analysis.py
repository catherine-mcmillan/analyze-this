import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file, abort
from flask_login import login_required, current_user
from app import db
from app.models import Analysis
from app.forms import UploadCSVForm, PromptForm, ReviewPromptForm
from app.utils.csv_parser import save_csv_file, parse_csv_headers, get_csv_sample
from app.utils.prompt_formatter import create_enhanced_prompt
from app.utils.anthropic_api import generate_analysis
from werkzeug.utils import secure_filename
import json
import pandas as pd
from io import BytesIO

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadCSVForm()
    
    if form.validate_on_submit():
        try:
            # Generate a unique filename
            original_filename = secure_filename(form.file.data.filename)
            file_extension = os.path.splitext(original_filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            
            # Save the file
            file_path = save_csv_file(form.file.data, unique_filename)
            
            # Create new analysis record
            analysis = Analysis(
                title=form.title.data,
                filename=unique_filename,
                user_id=current_user.id,
                column_annotations="{}"  # Empty JSON object
            )
            db.session.add(analysis)
            db.session.commit()
            
            # Redirect to column annotation page
            return redirect(url_for('analysis.annotate_columns', analysis_id=analysis.id))
            
        except Exception as e:
            flash(f'Error processing CSV file: {str(e)}', 'danger')
    
    return render_template('analysis/upload.html', title='Upload CSV', form=form)

@analysis_bp.route('/annotate/<int:analysis_id>', methods=['GET', 'POST'])
@login_required
def annotate_columns(analysis_id):
    # Get the analysis record
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Check if the analysis belongs to the current user
    if analysis.user_id != current_user.id:
        abort(403)
    
    # Get file path
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], analysis.filename)
    
    if not os.path.exists(file_path):
        flash('CSV file not found. Please upload again.', 'danger')
        return redirect(url_for('analysis.upload'))
    
    # Parse headers and get sample data
    try:
        headers = parse_csv_headers(file_path)
        sample_data = get_csv_sample(file_path).head(5).to_dict('records')
    except Exception as e:
        flash(f'Error parsing CSV: {str(e)}', 'danger')
        return redirect(url_for('analysis.upload'))
    
    # Handle form submission
    if request.method == 'POST':
        # Process form data
        annotations = {}
        for header in headers:
            annotations[header] = {
                'description': request.form.get(f"description_{header}", ''),
                'source': request.form.get(f"source_{header}", ''),
                'notes': request.form.get(f"notes_{header}", '')
            }
        
        # Save annotations to database
        analysis.set_column_annotations(annotations)
        db.session.commit()
        
        # Redirect to prompt creation
        return redirect(url_for('analysis.create_prompt', analysis_id=analysis.id))
    
    return render_template(
        'analysis/annotate.html',
        title='Annotate Columns',
        analysis=analysis,
        headers=headers,
        sample_data=sample_data
    )

@analysis_bp.route('/prompt/<int:analysis_id>', methods=['GET', 'POST'])
@login_required
def create_prompt(analysis_id):
    # Get the analysis record
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Check if the analysis belongs to the current user
    if analysis.user_id != current_user.id:
        abort(403)
    
    form = PromptForm()
    
    if form.validate_on_submit():
        # Save the user's prompt
        analysis.prompt = form.prompt.data
        
        # Generate enhanced prompt
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], analysis.filename)
        column_annotations = analysis.get_column_annotations()
        
        try:
            enhanced_prompt = create_enhanced_prompt(
                analysis.prompt,
                column_annotations,
                file_path
            )
            
            analysis.enhanced_prompt = enhanced_prompt
            db.session.commit()
            
            # Redirect to prompt review page
            return redirect(url_for('analysis.review_prompt', analysis_id=analysis.id))
            
        except Exception as e:
            flash(f'Error generating enhanced prompt: {str(e)}', 'danger')
    
    # Suggest prompt templates
    prompt_templates = [
        "Please analyze this dataset to identify trends in [X] over time.",
        "Can you find correlations between [X] and [Y] in this dataset?",
        "What are the key factors affecting [X] in this dataset?",
        "Please provide summary statistics and distributions for all numeric variables.",
        "Analyze this sales data to identify top performing products and regions."
    ]
    
    return render_template(
        'analysis/prompt.html',
        title='Create Analysis Prompt',
        analysis=analysis,
        form=form,
        prompt_templates=prompt_templates
    )

@analysis_bp.route('/review_prompt/<int:analysis_id>', methods=['GET', 'POST'])
@login_required
def review_prompt(analysis_id):
    # Get the analysis record
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Check if the analysis belongs to the current user
    if analysis.user_id != current_user.id:
        abort(403)
    
    form = ReviewPromptForm()
    
    if form.validate_on_submit():
        # Update the enhanced prompt with user edits
        analysis.enhanced_prompt = form.enhanced_prompt.data
        db.session.commit()
        
        # Generate analysis
        try:
            # Use the user's API key if available, otherwise use the app's key
            api_key = current_user.anthropic_api_key or current_app.config['ANTHROPIC_API_KEY']
            
            if not api_key:
                flash('No Anthropic API key available. Please add one in your profile.', 'danger')
                return redirect(url_for('auth.profile'))
            
            # Generate the report
            report = generate_analysis(analysis.enhanced_prompt, api_key)
            
            # Save the report
            analysis.report = report
            db.session.commit()
            
            # Redirect to report view
            return redirect(url_for('analysis.view_report', analysis_id=analysis.id))
            
        except Exception as e:
            flash(f'Error generating analysis: {str(e)}', 'danger')
    
    elif request.method == 'GET':
        form.enhanced_prompt.data = analysis.enhanced_prompt
    
    return render_template(
        'analysis/review_prompt.html',
        title='Review Enhanced Prompt',
        analysis=analysis,
        form=form
    )

@analysis_bp.route('/report/<int:analysis_id>', methods=['GET', 'POST'])
@login_required
def view_report(analysis_id):
    # Get the analysis record
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Check if the analysis belongs to the current user
    if analysis.user_id != current_user.id:
        abort(403)
    
    # Handle report edits
    if request.method == 'POST':
        analysis.report = request.form.get('report', analysis.report)
        db.session.commit()
        flash('Report updated successfully!', 'success')
    
    return render_template(
        'analysis/report.html',
        title=f'Analysis Report: {analysis.title}',
        analysis=analysis
    )

@analysis_bp.route('/export/<int:analysis_id>')
@login_required
def export_report(analysis_id):
    # Get the analysis record
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Check if the analysis belongs to the current user
    if analysis.user_id != current_user.id:
        abort(403)
    
    # Prepare report text
    report_text = analysis.report
    
    # Create a text file in memory
    buffer = BytesIO()
    buffer.write(report_text.encode('utf-8'))
    buffer.seek(0)
    
    # Generate filename
    filename = f"analysis_report_{analysis.title.replace(' ', '_')}.md"
    
    # Return the file for download
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='text/markdown'
    )

@analysis_bp.route('/history')
@login_required
def history():
    analyses = Analysis.query.filter_by(user_id=current_user.id).order_by(Analysis.created_at.desc()).all()
    return render_template('analysis/history.html', title='Analysis History', analyses=analyses)

@analysis_bp.route('/delete/<int:analysis_id>', methods=['POST'])
@login_required
def delete_analysis(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Check if the analysis belongs to the current user
    if analysis.user_id != current_user.id:
        abort(403)
    
    # Delete associated file
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], analysis.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Delete database record
    db.session.delete(analysis)
    db.session.commit()
    
    flash('Analysis deleted successfully.', 'success')
    return redirect(url_for('analysis.history'))