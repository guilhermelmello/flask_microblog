from config import Config
from flask import Flask
from flask import request
from flask_babel import Babel
from flask_babel import lazy_gettext as _l
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler

import logging
import os


app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = 'login'
login.login_message = _l('Please log in to access this page.')

mail = Mail(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
babel = Babel(app)

if not app.debug:
    # sends error by email
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])

        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()

        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr=f"no_reply@{app.config['MAIL_SERVER']}",
            toaddrs=app.config['ADMINS'],
            subject=f"{app.config['NAME']} Failure!",
            credentials=auth,
            secure=secure
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    # log error to a file
    if not os.path.exists('logs'):
        os.mkdir('logs')

    file_handler = RotatingFileHandler(
        os.path.join('logs', 'microblog.log'),
        maxBytes=10240,
        backupCount=10
    )

    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))

    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info(f"{app.config['NAME']} startup")


from app.errors import bp as errors_bp
app.register_blueprint(errors_bp)


@babel.localeselector
def get_locale():
    r = request.accept_languages.best_match(app.config['LANGUAGES'])
    return r


from app import routes
from app import models
