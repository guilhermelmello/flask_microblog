from app import app
from app.forms import LoginForm
from app.models import User
from flask import render_template
from flask import flash
from flask import redirect
from flask import url_for
from flask_login import current_user
from flask_login import login_user
from flask_login import logout_user


@app.route('/')
@app.route('/index')
def index():
    template_params = dict(
        title='Home',
        user={'username': 'melloGuilherme'},
        posts=[
            {
                'author': {'username': 'John'},
                'body': 'Beautiful day in Portland.'
            },
            {
                'author': {'username': 'Susan'},
                'body': 'The Avengers movie was so cool!'
            }
        ]
    )
    return render_template('index.html', **template_params)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid Username or Password.')
            return redirect(url_for('login'))
        login_user(user, remember_me=form.remember_me.data)
        return redirect(url_for('index'))

    template_params = dict(
        title='Sing In',
        form=form
    )
    return render_template('login.html', **template_params)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
