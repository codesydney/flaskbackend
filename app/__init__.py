from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_moment import Moment
from config import Config
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint


db = SQLAlchemy()
migrate = Migrate(compare_type=True)
moment = Moment()

# swagger specific
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "MyApp"
    }
)

def create_app(config_class=Config):
    app = Flask(__name__)
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

        app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

    return app