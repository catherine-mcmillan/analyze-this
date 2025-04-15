import os
from flask import render_template, flash, redirect, url_for, request, current_app, abort, jsonify, send_file
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app import db
from app.analysis import bp
from app.models.analysis import Analysis
from app.analysis.forms import UploadForm, ColumnAnnotationForm, PromptForm, EnhancedPromptForm
from app.utils.csv_handler import parse_csv, get_column_names, save_csv
from app.utils.claude_api import generate_enhanced_prompt, generate_analysis
from app.utils.export import create_report_file
import uuid
import json
import pandas as pd

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        # Check if the user has a valid API key
        if not current_user.is_api_key_valid:
            flash('Please add a valid Anthropic API key in your profile first.', 'warning')
            return redirect(url_for('auth.api_key'))
            
        # Save the uploaded file
        f = form.csv_file.data
        filename = secure_filename(f.filename)
        unique_id = uuid.uuid4().hex
        unique_filename = f"{unique_id}_{filename}"
        filepath = save_csv(f, unique_filename)
        
        # Create a new analysis record
        analysis = Analysis(
            title=form.title.data,
            filename=unique_filename,
            filepath=filepath,
            user_id=current_user.id
        )
        db.session.add(analysis)
        db.session.commit()
        
        flash('CSV file uploaded successfully!', 'success')
        return redirect(url_for('analysis.annotate', analysis_id=analysis.id))
    
    return render_template('analysis/upload.html', title='Upload CSV', form=form)

@bp.route('/annotate/<int:analysis_id>', methods=['GET', 'POST'])
@login_required
def annotate(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Ensure the analysis belongs to the current user
    if analysis.user_id != current_user.id:
        abort(403)
    
    # Parse the CSV to get column names
    try:
        column_names = get_column_names(analysis.filepath)
        df = parse_csv(analysis.filepath, nrows=5)
        sample_data = df.to_dict('records')
    except Exception as e:
        flash(f'Error reading CSV file: {str(e)}', 'danger')
        return redirect(url_for('analysis.upload'))
    
    # Handle form submission
    if request.method == 'POST':
        column_metadata = {}
        for column in column_names:
            column_metadata[column] = {
                'description': request.form.get(f'description_{column}', ''),
                'source': request.form.get(f'source_{column}', ''),
                'notes': request.form.get(f'notes_{column}', '')
            }
        
        analysis.column_metadata = json.dumps(column_metadata)
        db.session.commit()
        
        flash('Column annotations saved successfully!', 'success')
        return redirect(url_for('analysis.create_prompt', analysis_id=analysis.id))
    
    # For GET requests, pre-populate form if metadata exists
    column_metadata = {}
    if analysis.column_metadata:
        column_metadata = json.loads(analysis.column_metadata)
    
    return render_template('analysis/annotate.html', 
                          title='Annotate Columns', 
                          analysis=analysis,
                          column_names=column_names,
                          sample_data=sample_data,
                          column_metadata=column_metadata)

@bp.route('/prompt/<int:analysis_id>', methods=['GET', 'POST'])
@login_required
def create_prompt(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Ensure the analysis belongs to the current user
    if analysis.user_id != current_user.id:
        abort(403)
    
    form = PromptForm()
    
    # Suggested prompt templates
    prompt_templates = [
        "Please analyze this dataset and identify key trends and patterns.",
        "Provide summary statistics for all columns and highlight any interesting correlations.",
        "Analyze the relationship between [Column X] and [Column Y] and explain any observed patterns.",
        "Segment the data into meaningful groups and explain the characteristics of each segment.",
        "Identify outliers in the dataset and explain their potential impact on the analysis."
    ]
    
    if form.validate_on_submit():
        analysis.prompt = form.prompt.data
        
        try:
            # Generate enhanced prompt
            column_metadata = json.loads(analysis.column_metadata) if analysis.column_metadata else {}
            enhanced_prompt = generate_enhanced_prompt(analysis.prompt, column_metadata, analysis.filepath)
            analysis.enhanced_prompt = enhanced_prompt
            db.session.commit()
            
            flash('Prompt created successfully!', 'success')
            return redirect(url_for('analysis.review_prompt', analysis_id=analysis.id))
        except Exception as e:
            flash(f'Error generating enhanced prompt: {str(e)}', 'danger')
    
    return render_template('analysis/prompt.html', 
                          title='Create Prompt', 
                          form=form, 
                          analysis=analysis,
                          prompt_templates=prompt_templates)

@bp.route('/review_prompt/<int:analysis_id>', methods=['GET', 'POST'])
@login_required
def review_prompt(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Ensure the analysis belongs to the current user
    if analysis.user_id != current_user.id:
        abort(403)
    
    # Ensure we have an enhanced prompt to review
    if not analysis.enhanced_prompt:
        flash('No enhanced prompt found. Please create a prompt first.', 'warning')
        return redirect(url_for('analysis.create_prompt', analysis_id=analysis.id))
    
    form = EnhancedPromptForm()
    
    if request.method == 'GET':
        form.enhanced_prompt.data = analysis.enhanced_prompt
    
    if form.validate_on_submit():
        # Update the enhanced prompt with user edits
        analysis.enhanced_prompt = form.enhanced_prompt.data
        db.session.commit()
        
        # Redirect to generate analysis
        return redirect(url_for('analysis.generate', analysis_id=analysis.id))
    
    return render_template('analysis/review_prompt.html', 
                          title='Review Enhanced Prompt', 
                          form=form,
                          analysis=analysis)

@bp.route('/generate/<int:analysis_id>')
@login_required
def generate(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Ensure the analysis belongs to the current user
    if analysis.user_id != current_user.id:
        abort(403)
    
    # Ensure we have an enhanced prompt
    if not analysis.enhanced_prompt:
        flash('No enhanced prompt found. Please create a prompt first.', 'warning')
        return redirect(url_for('analysis.create_prompt', analysis_id=analysis.id))
    
    try:
        # Show a loading page
        return render_template('analysis/loading.html', 
                              title='Generating Analysis', 
                              analysis=analysis)
    except Exception as e:
        flash(f'Error preparing analysis generation: {str(e)}', 'danger')
        return redirect(url_for('analysis.review_prompt', analysis_id=analysis.id))

@bp.route('/process/<int:analysis_id>', methods=['POST'])
@login_required
def process_analysis(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Ensure the analysis belongs to the current user
    if analysis.user_id != current_user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    try:
        # Generate the analysis using Claude API
        report = generate_analysis(analysis.enhanced_prompt, current_user.anthropic_api_key)
        
        # Save the report
        analysis.report = report
        db.session.commit()
        
        return jsonify({
            'success': True,
            'redirect': url_for('analysis.report', analysis_id=analysis.id)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/report/<int:analysis_id>', methods=['GET', 'POST'])
@login_required
def report(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Ensure the analysis belongs to the current user
    if analysis.user_id != current_user.id:
        abort(403)
    
    # Ensure we have a report to display
    if not analysis.report:
        flash('No report found. Please generate the analysis first.', 'warning')
        return redirect(url_for('analysis.review_prompt', analysis_id=analysis.id))
    
    # Handle POST request for updating the report
    if request.method == 'POST':
        analysis.report = request.form.get('report_content', analysis.report)
        db.session.commit()
        flash('Report updated successfully!', 'success')
    
    return render_template('analysis/report.html', 
                          title='Analysis Report', 
                          analysis=analysis)

@bp.route('/export/<int:analysis_id>')
@login_required
def export_report(analysis_id):
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Ensure the analysis belongs to the current user
    if analysis.user_id != current_user.id:
        abort(403)
    
    # Ensure we have a report to export
    if not analysis.report:
        flash('No report found to export.', 'warning')
        return redirect(url_for('analysis.report', analysis_id=analysis.id))
    
    try:
        # Create a temporary file for download
        report_file, report_format = create_report_file(analysis)
        
        return send_file(
            report_file,
            as_attachment=True,
            download_name=f"{analysis.title.replace(' ', '_')}_report.{report_format}",
            mimetype=f'text/{report_format}'
        )
    except Exception as e:
        flash(f'Error exporting report: {str(e)}', 'danger')
        return redirect(url_for('analysis.report', analysis_id=analysis.id))