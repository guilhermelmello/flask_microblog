from app import cli
from app import create_app
from app import db
from app.models import User
from app.models import Post


app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    context = {
        'db': db,
        'User': User,
        'Post': Post
    }
    return context
