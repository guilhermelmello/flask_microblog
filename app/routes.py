from app import app
from app import db
from app.email import send_password_reset_email
from app.forms import EditProfileForm
from app.forms import LoginForm
from app.forms import PostForm
from app.forms import RegistrationForm
from app.forms import ResetPasswordForm
from app.forms import ResetPasswordRequestForm
from app.models import Post
from app.models import User
from app.translate import translate
from datetime import datetime
from flask import render_template
from flask import flash
from flask import g
from flask import jsonify
from flask import redirect
from flask import request
from flask import url_for
from flask_babel import _
from flask_babel import get_locale
from flask_login import current_user
from flask_login import login_user
from flask_login import login_required
from flask_login import logout_user
from guess_language import guess_language
from werkzeug.urls import url_parse


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.locale = str(get_locale())


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    title = _('Home Page')
    form = PostForm()

    if form.validate_on_submit():
        lang = guess_language(form.post.data)
        if lang == 'UNKNOWN' or len(lang) > 5:
            lang = ''

        post = Post(
            body=form.post.data,
            author=current_user,
            language=lang
        )
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('index'))

    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page,
        app.config['POSTS_PER_PAGE'],
        False
    )
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None

    render = render_template(
        'index.html',
        title=title,
        form=form,
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url
    )

    return render


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid Username or Password.'))
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    template_params = dict(
        title=_('Sign In'),
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

        flash(_('Congratulation. You are now a registered user!'))
        return redirect(url_for('login'))

    template_params = dict(
        title=_('Register'),
        form=form
    )
    return render_template('register.html', **template_params)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('user', username=username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=username, page=posts.prev_num) \
        if posts.has_prev else None

    render = render_template(
        'user.html',
        user=user,
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url
    )

    return render


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    template_params = dict(
        title=_('Edit Profile'),
        form=form
    )
    return render_template('edit_profile.html', **template_params)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()

    if user is None:
        flash(_("User %(username)s not found.", username=username))
        return redirect(url_for('index'))

    if user == current_user:
        flash(_('You cannot follow yourself.'))
        return redirect(url_for(f"user", username=username))

    current_user.follow(user)
    db.session.commit()
    flash(_("You are following %(username)s!", username=username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()

    if user is None:
        flash(_("User %(username)s not found.", username=username))
        return redirect(url_for('index'))

    if user == current_user:
        flash(_('You cannot unfollow yourself.'))
        return redirect(url_for(f"user", username=username))

    current_user.unfollow(user)
    db.session.commit()
    flash(_("You are not following %(username)s!", username=username))
    return redirect(url_for(f"user", username=username))


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None

    render = render_template(
        'index.html',
        title=_('Explore'),
        posts=posts.items,
        next_url=next_url,
        prev_url=prev_url
    )

    return render


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            m = 'Check your email for the instructions to reset your password.'
            flash(_(m))
        else:
            flash(_('Email not registered.'))
        return redirect(url_for('login'))

    render = render_template(
        'reset_password_request.html',
        title=_('Reset Password'),
        form=form
    )

    return render


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))

    render = render_template(
        'reset_password.html',
        form=form
    )

    return render


@app.route('/translate', methods=['POST'])
@login_required
def translate_text():
    translation = translate(
        request.form['text'],
        request.form['source_language'],
        request.form['dest_language']
    )
    json = jsonify({'text': translation})
    return json
