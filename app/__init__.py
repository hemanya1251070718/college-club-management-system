import os
from flask import Flask
from app.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Register blueprints / routes
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    # Register authentication & RBAC blueprint
    from app.auth import auth_bp, get_current_role, get_current_user, ROLE_METADATA
    app.register_blueprint(auth_bp)

    # Inject RBAC context into all Jinja templates
    @app.context_processor
    def inject_rbac():
        role = get_current_role()
        return {
            "current_role": role,
            "current_user_name": get_current_user(),
            "role_meta": ROLE_METADATA.get(role, ROLE_METADATA["guest"]),
            "all_roles": ROLE_METADATA
        }
    
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
