from datetime import datetime

from flask import flash, redirect, url_for, render_template, request, Blueprint
from flask_login import LoginManager, AnonymousUserMixin, current_user, login_user

from ..models.Users import User
from .forms import SignupForm, LoginForm

login_manager = LoginManager()


class MyAnonymousUser(AnonymousUserMixin):
    is_admin = False


def init_login(app):
    """ initiate login manager with custom anonymoususer class """
    login_manager.anonymous_user = MyAnonymousUser
    login_manager.init_app(app)


# Blueprint Configuration
auth_bp = Blueprint(
    'auth_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Log-in page for registered users.

    GET requests serve Log-in page.
    POST requests validate and redirect user to dashboard.
    """
    # Bypass if user is logged in
    if current_user.is_authenticated:
        return redirect(url_for('user', username=current_user.username))

    form = LoginForm()
    # Validate login attempt
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(password=form.password.data):
            login_user(user)
            if login_user(user):  # Log in as newly created user
                user.last_login = datetime.now()
                user.db_commit()
            next_page = request.args.get('next')
            return redirect(next_page or url_for('user', username=user.username))
        flash('Invalid username/password combination')
        return redirect(url_for('login'))
    return render_template(
        'login.html',
        form=form,
        title='Log in.',
        template='login-page',
        body="Log in with your User account."
    )


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user is None:
            user = User(
                name=form.name.data,
                username=form.username.data,
                email=form.email.data,
                is_admin=False,
                is_activated=False,
            )
            user.set_password(form.password.data)
            user.add_to_db()
            if login_user(user):  # Log in as newly created user
                user.last_login = datetime.now()
                user.db_commit()
            return redirect(url_for('user', username=user.username))
        flash('A user already exists with that email address.')
    return render_template(
        'register.html',
        title='Create an Account.',
        form=form,
        template='register-page',
        body="Sign up for a user account."
    )


@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth_bp.login'))
