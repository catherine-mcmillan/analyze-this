import json
from flask import current_app

def create_enhanced_prompt(user_prompt, column_annotations, file_path):
    """
    Create an enhanced prompt for Claude by combining user input and column annotations
    
    Args:
        user_prompt: The user's original prompt text
        column_annotations: Dictionary of column names and their annotations
        file_path: Path to the CSV file
        
    Returns:
        Enhanced prompt string
    """
    # Import pandas here to avoid circular imports
    import pandas as pd
    
    # Get a sample of the CSV data
    try:
        df = pd.read_csv(file_path, nrows=5)
        sample_data = df.head(5).to_string()
    except Exception as e:
        current_app.logger.error(f"Error reading CSV for prompt: {str(e)}")
        sample_data = "Error: Could not read sample data from CSV file."
    
    # Format the column annotations
    columns_context = ""
    for column, annotation in column_annotations.items():
        if annotation.get('description') or annotation.get('source') or annotation.get('notes'):
            columns_context += f"Column: {column}\n"
            if annotation.get('description'):
                columns_context += f"Description: {annotation.get('description')}\n"
            if annotation.get('source'):
                columns_context += f"Data Source: {annotation.get('source')}\n"
            if annotation.get('notes'):
                columns_context += f"Additional Notes: {annotation.get('notes')}\n"
            columns_context += "\n"
    
    # Construct the enhanced prompt
    enhanced_prompt = f"""
I have a CSV dataset with the following columns and meanings:

{columns_context}

Here's a sample of the data:
```
{sample_data}
```

My analysis goal/question:
{user_prompt}

Please provide a comprehensive analysis based on this data. Include:

1. Summary of the dataset
2. Key insights and patterns
3. Statistical analysis where appropriate
4. Visualizations recommendations (describe what would be useful to visualize)
5. Answers to my specific questions
6. Any limitations in the data or analysis
7. Recommendations for further analysis

Format your response with clear headings and bullet points where appropriate for readability.
"""
    
    return enhanced_prompt.strip()