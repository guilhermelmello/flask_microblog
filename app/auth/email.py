from app.email import send_email
from flask import current_app
from flask import render_template
from flask_babel import _


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    app_name = current_app.config['NAME']
    send_email(
        _("[%(app_name)s]: Reset your password", app_name=app_name),
        sender=current_app.config['ADMINS'][0],
        recipients=[user.email],
        text_body=render_template(
            'email/reset_password.txt',
            user=user,
            token=token,
            team_name=app_name),
        html_body=render_template(
            'email/reset_password.html',
            user=user,
            token=token,
            team_name=app_name)
    )
