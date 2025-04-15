import anthropic
from flask import current_app
import time

def generate_analysis(prompt, api_key=None):
    """
    Generate an analysis report using Anthropic's Claude API
    
    Args:
        prompt: The enhanced prompt to send to Claude
        api_key: Anthropic API key (optional - falls back to app config)
        
    Returns:
        Generated analysis text
    """
    # Use provided API key or fall back to app config
    anthropic_api_key = api_key or current_app.config['ANTHROPIC_API_KEY']
    
    if not anthropic_api_key:
        raise ValueError("No Anthropic API key provided")
    
    # Create Claude client
    client = anthropic.Anthropic(api_key=anthropic_api_key)
    
    try:
        # Call the Claude API
        response = client.messages.create(
            model=current_app.config['CLAUDE_MODEL'],
            max_tokens=4000,
            temperature=0.2,
            system="You are a helpful data analysis assistant. Provide clear, accurate, and insightful analysis of the given data.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract the generated content
        analysis_text = response.content[0].text
        return analysis_text
    
    except Exception as e:
        current_app.logger.error(f"Error calling Anthropic API: {str(e)}")
        raise RuntimeError(f"Failed to generate analysis: {str(e)}")