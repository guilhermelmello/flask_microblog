from app import app
from app import db
from app.models import User
from app.models import Post


@app.shell_context_processor
def make_shell_context():
    context = {
        'db': db,
        'User': User,
        'Post': Post
    }
    return context
