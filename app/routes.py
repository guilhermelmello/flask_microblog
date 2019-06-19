from app import app
from flask import render_template


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
