import os
from flask import Flask
from app.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Register blueprints / routes
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # Custom error handlers for clean error pages without leaking stack traces
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        return render_template("errors/500.html"), 500

    return app
