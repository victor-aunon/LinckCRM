import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.abspath(os.path.dirname(__file__)), '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hjafkuie68867272342hghgj'
    BASEDIR = os.path.abspath(os.path.dirname(__file__))

    if os.environ.get("POSTGRES_URL"):
        DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(
            user=os.environ.get("POSTGRES_USER"),
            pw=os.environ.get("POSTGRES_PW"),
            url=os.environ.get("POSTGRES_URL"),
            db=os.environ.get("POSTGRES_DB"))

    SQLALCHEMY_DATABASE_URI = DB_URL or \
        'sqlite:///' + os.path.join(BASEDIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['victor.contenedor@gmail.com']  # TODO

    ELEMENTS_PER_PAGE = 20

    LANGUAGES = ['en', 'es']
    MS_TRANSLATOR_KEY = os.environ.get('MS_TRANSLATOR_KEY')

    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
