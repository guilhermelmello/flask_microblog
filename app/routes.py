from app import app
from app.forms import LoginForm
from flask import render_template
from flask import flash
from flask import redirect
from flask import url_for


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
    form = LoginForm()

    if form.validate_on_submit():
        msg = 'Login required for user {}, remember_me={}'
        msg = msg.format(form.username.data, form.remember_me.data)
        flash(msg)
        return redirect(url_for('index'))

    template_params = dict(
        title='Sing In',
        form=form
    )
    return render_template('login.html', **template_params)
