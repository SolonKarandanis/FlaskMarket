import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
logging.basicConfig(format='[%(asctime)s] %(levelname)s %(name)s: %(message)s')
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://sales_db:sales_db@192.168.1.5:5432/sales_db"
app.config['SECRET_KEY'] = 'ec9439cfc6c796ae2029594d'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'
login_manager.login_message_category = 'info'
from market import routes

