from app import db
from app.auth import bp
from app.auth.forms import LoginForm
from app.auth.forms import RegistrationForm
from app.auth.forms import ResetPasswordForm
from app.auth.forms import ResetPasswordRequestForm
from app.auth.email import send_password_reset_email
from app.models import User
from flask import render_template
from flask import flash
from flask import redirect
from flask import request
from flask import url_for
from flask_babel import _
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user
from werkzeug.urls import url_parse


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid Username or Password.'))
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)

    template_params = dict(
        title=_('Sign In'),
        form=form
    )
    return render_template('auth/login.html', **template_params)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash(_('Congratulation. You are now a registered user!'))
        return redirect(url_for('auth.login'))

    template_params = dict(
        title=_('Register'),
        form=form
    )
    return render_template('auth/register.html', **template_params)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            m = 'Check your email for the instructions to reset your password.'
            flash(_(m))
        else:
            flash(_('Email not registered.'))
        return redirect(url_for('auth.login'))

    render = render_template(
        'auth/reset_password_request.html',
        title=_('Reset Password'),
        form=form
    )

    return render


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))

    render = render_template(
        'auth/reset_password.html',
        form=form
    )

    return render
