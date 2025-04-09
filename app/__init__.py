import os
from flask import Flask, redirect, url_for
from flask_login import current_user
from config import Config
from .extensions import db, migrate, login_manager
from .models import User
from datetime import datetime

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Sicherstellen, dass der Instanzordner existiert
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    # Sicherstellen, dass der Upload-Ordner existiert
    upload_folder = app.config.get('UPLOAD_FOLDER', os.path.join(app.instance_path, 'uploads'))
    try:
         os.makedirs(upload_folder)
    except OSError:
        pass
    app.config['UPLOAD_FOLDER'] = upload_folder

    # Erweiterungen initialisieren
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Bitte melden Sie sich an, um diese Seite anzuzeigen."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints registrieren
    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .tickets import bp as tickets_bp
    app.register_blueprint(tickets_bp) # Kein Prefix

    from .admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Root-Route
    @app.route('/')
    @app.route('/index')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('tickets.ticket_overview'))
        else:
            return redirect(url_for('auth.login'))

    # Context Processor
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow}

    return app