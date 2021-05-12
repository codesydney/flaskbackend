import os
from dotenv import load_dotenv
from pathlib import Path


basedir = Path(__file__).parent
load_dotenv(basedir / '.env')

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'random string'
    
    if (os.environ.get('FLASK_ENV') == 'development'):
        # Dev only so browser doesnt cache for CSS
        SEND_FILE_MAX_AGE_DEFAULT = 0
        # auto reload template without needing to restart Flask
        TEMPLATES_AUTO_RELOAD = True

    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # recommended by Pythonanywhere otherwise you get mysql timeout
    SQLALCHEMY_POOL_RECYCLE = 299
    SQLALCHEMY_TRACK_MODIFICATIONS = False
