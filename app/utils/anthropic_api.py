import anthropic
from flask import current_app
import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class AnthropicAPIError(Exception):
    """Custom exception for Anthropic API errors"""
    pass

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def generate_analysis(prompt, api_key=None, model=None, max_tokens=4000):
    """
    Generate an analysis report using Anthropic's Claude API with retry logic
    
    Args:
        prompt: The enhanced prompt to send to Claude
        api_key: Anthropic API key (optional - falls back to app config)
        model: Claude model to use (optional - falls back to app config)
        max_tokens: Maximum tokens in response
        
    Returns:
        Generated analysis text
    
    Raises:
        AnthropicAPIError: If the API request fails after retries
    """
    # Use provided API key or fall back to app config
    anthropic_api_key = api_key or current_app.config['ANTHROPIC_API_KEY']
    
    if not anthropic_api_key:
        logger.error("No Anthropic API key provided")
        raise AnthropicAPIError("No Anthropic API key provided")
    
    # Use provided model or fall back to app config
    model_name = model or current_app.config['CLAUDE_MODEL']
    
    # Create Claude client
    client = anthropic.Anthropic(api_key=anthropic_api_key)
    
    try:
        logger.info(f"Sending analysis request to Anthropic API using model {model_name}")
        
        # Track start time for performance monitoring
        start_time = time.time()
        
        # Call the Claude API
        response = client.messages.create(
            model=model_name,
            max_tokens=max_tokens,
            temperature=0.2,
            system="You are a helpful data analysis assistant. Provide clear, accurate, and insightful analysis of the given data using statistical methods where appropriate. Format your response with markdown for readability.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Calculate and log elapsed time
        elapsed_time = time.time() - start_time
        logger.info(f"Received response from Anthropic API in {elapsed_time:.2f} seconds")
        
        # Extract the generated content
        analysis_text = response.content[0].text
        
        # Log basic stats about the response
        token_count = len(analysis_text.split())
        logger.info(f"Generated analysis with approximately {token_count} tokens")
        
        return analysis_text
    
    except Exception as e:
        logger.error(f"Anthropic API error: {str(e)}")
        raise AnthropicAPIError(f"Failed to generate analysis: {str(e)}")