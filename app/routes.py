from app import app
from app import db
from app.forms import LoginForm
from app.forms import RegistrationForm
from app.models import User
from flask import render_template
from flask import flash
from flask import redirect
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_user
from flask_login import login_required
from flask_login import logout_user
from werkzeug.urls import url_parse


@app.route('/')
@app.route('/index')
@login_required
def index():
    template_params = dict(
        title='Home Page',
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
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    template_params = dict(
        title='Sing In',
        form=form
    )
    return render_template('login.html', **template_params)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Congratulation. You are now a registered user!')
        return redirect(url_for('login'))

    template_params = dict(
        title='Register',
        form=form
    )
    return render_template('register.html', **template_params)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    template_params = dict(
        user=user,
        posts=posts
    )
    return render_template('user.html', **template_params)
