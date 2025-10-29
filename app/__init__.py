from flask import Flask
from flask_cors import CORS
from .config import Config

def create_app(config_class=Config):
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    CORS(app)

  
    from .postgres_api.routes import pg_api

   
    app.register_blueprint(pg_api, url_prefix='/api/postgres')
   
    return app