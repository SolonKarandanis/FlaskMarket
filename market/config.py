import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ec9439cfc6c796ae2029594d'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') \
                              or "postgresql://sales_db:sales_db@192.168.1.5:5432/sales_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.googlemail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or 1
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'skarandanis@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or '7ujm&UJM'
    ADMINS = ['skarandanis@gmail.com']

    LANGUAGES = ['en', 'gr']
