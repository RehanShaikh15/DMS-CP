from flask import Flask
from flask_bootstrap import Bootstrap5
from models import db
from config import config

from flask_migrate import Migrate

def create_app(config_name='development', test_config=None):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    if test_config:
        app.config.from_mapping(test_config)

    # Initialize extensions
    db.init_app(app)
    Migrate(app, db)
    Bootstrap5(app)

    # Register Blueprints
    from routes.auth_routes import auth_bp
    from routes.admin import admin_bp
    from routes.faculty_routes import faculty_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(faculty_bp)

    from flask import session
    
    @app.context_processor
    def inject_user_roles():
        return {
            'is_admin': 'admin_id' in session,
            'is_faculty': 'faculty_id' in session,
            'admin_username': session.get('admin_username'),
            'faculty_name': session.get('faculty_name')
        }

    
    # Register CLI Commands
    from commands import register_commands
    register_commands(app)

    return app

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
