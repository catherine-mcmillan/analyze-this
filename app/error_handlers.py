from flask import render_template, request, jsonify
import logging
import traceback
from app.utils.anthropic_api import AnthropicAPIError

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Register error handlers with Flask app"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors"""
        logger.info(f"404 error: {request.path}")
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        logger.error(f"500 error: {str(error)}\n{traceback.format_exc()}")
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 errors"""
        logger.warning(f"403 error: {request.path} - User: {getattr(request, 'user', 'Unknown')}")
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(AnthropicAPIError)
    def handle_anthropic_error(error):
        """Handle Anthropic API errors"""
        logger.error(f"Anthropic API error: {str(error)}")
        return render_template('errors/api_error.html', error=error), 500

def setup_logging(app):
    """Configure application logging"""
    if not app.debug:
        # Set up file handler
        file_handler = logging.FileHandler('app.log')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(file_handler)
        
        # Set up stderr handler
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Analyze This startup')
        
    # Register error handlers
    register_error_handlers(app)

# Add to app/__init__.py
from app.error_handlers import setup_logging

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions...
    
    # Set up logging and error handlers
    setup_logging(app)
    
    # Register blueprints...
    
    return app