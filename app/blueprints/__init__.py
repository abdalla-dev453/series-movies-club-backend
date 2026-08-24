from app.blueprints.movies import movies_bp
from app.blueprints.auth import auth_bp  
from app.blueprints.users import users_bp

def register_blueprints(app):
    app.register_blueprint(movies_bp, url_prefix='/api/movies')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')