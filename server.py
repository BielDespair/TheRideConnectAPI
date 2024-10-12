from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import dotenv

from config import Config

configs = Config()
app = Flask(__name__)
app.config.from_object(configs)

db = SQLAlchemy(app)