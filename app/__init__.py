from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from config import Config
from flask_cors import CORS


db = SQLAlchemy()
migrate = Migrate(compare_type=True)
moment = Moment()

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='../../dist/spa', static_url_path='/')
    app.config.from_object(Config)

    with app.app_context():
        db.init_app(app)
        migrate.init_app(app,db)
        moment.init_app(app)

        # this is needed if client accesses api (on different domain or port). Dont use on PROD.
        CORS(app)

        from app.errors import bp as errors_bp
        app.register_blueprint(errors_bp)
        
        from app.email import bp as email_bp
        app.register_blueprint(email_bp)

        from app.auth import bp as auth_bp
        app.register_blueprint(auth_bp, url_prefix='/api')

        from app.main import bp as main_bp
        app.register_blueprint(main_bp, url_prefix='/api')

    return app