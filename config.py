import dotenv
import os

dotenv.load_dotenv()

class Config(object):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
