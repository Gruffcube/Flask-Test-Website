from flask import Flask
from .config import Config
from .routes import main_bp
from datetime import timedelta



def create_app():
    app = Flask(__name__,
                template_folder="../../templates",
                static_folder="../../static",
                static_url_path="/static")
    
    app.config.from_object(Config)
    
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
    
    app.register_blueprint(main_bp)


    return app
