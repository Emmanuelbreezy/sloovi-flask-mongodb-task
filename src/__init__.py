from datetime import timedelta
from os import environ
from flask import Flask, jsonify

from src.auth import auth
from src.constants.http_status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from src.template import temp
from src.database import db
from flask_jwt_extended import JWTManager
from flasgger import Swagger

from src.config.swagger import template, swagger_config


def create_app(test_config=None):
    
    app = Flask(__name__, 
    instance_relative_config=True)
    
    
    if test_config is None:
        
        app.config.from_mapping(
            SECRET_KEY= environ.get('SECRET_KEY'),
            MONGODB_URI= environ.get('MONGODB_URI'),
            JWT_SECRET_KEY=environ.get('JWT_SECRET_KEY'),
            JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1),
            JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30),
            SWAGGER={
                'title': "Sloovi API",
                'uiversion': 3
            }
        )
    
    else:
        app.config.from_mapping(test_config)
        
    db.app = app    
    JWTManager(app)
    
    app.register_blueprint(auth)
    app.register_blueprint(temp)
    
    #Swagger(app, config=swagger_config, template=template)
    
    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(e):
        return jsonify({'error': 'Not found'}), HTTP_404_NOT_FOUND

    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(e):
        return jsonify({'error': 'Something went wrong, we are working on it'}), HTTP_500_INTERNAL_SERVER_ERROR
    
    
    return app

# if __name__ == '__main__':
#     # run app in debug mode on port 5000
#     create_app()

