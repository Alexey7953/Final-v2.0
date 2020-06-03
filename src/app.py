from flask import Flask
from src.database import db
from src.blueprints.cities import bp as bp_cities
from src.blueprints.colors import bp as bp_color
from src.blueprints.image import bp as bp_image
from src.blueprints.auth import bp as bp_auth
from src.blueprints.users import bp as users_bp
from src.blueprints.ads import bp as ads_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(bp_auth, url_prefix='/auth')
    app.register_blueprint(bp_color, url_prefix='/color')
    app.register_blueprint(bp_cities, url_prefix='/cities')
    app.register_blueprint(bp_image, url_prefix='/image')
    app.register_blueprint(ads_bp, url_prefix='/ads')
    db.init_app(app)
    return app
