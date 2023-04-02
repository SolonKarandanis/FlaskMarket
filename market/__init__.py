from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://sales_db:sales_db@192.168.1.5:5432/sales_db"
db = SQLAlchemy(app)

from market import routes
