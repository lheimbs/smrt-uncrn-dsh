"""Routes for parent Flask app."""
# from datetime import datetime

from flask import current_app as app
from flask import redirect, render_template  # , flash, request, url_for
from flask_login import login_required, logout_user  # , current_user, login_user
# from .models import db
from .models.Users import User
# from .auth.forms import SignupForm, LoginForm


# @app.route('/')
# def home():
#     """Landing page."""
#     return render_template(
#         'index.html',
#         title='Flask Dash experiment',
#         description='Embed Plotly Dash into Flask applications.',
#         template='home-template',
#         body="This is a homepage served with Flask."
#     )


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     """
#     Log-in page for registered users.

#     GET requests serve Log-in page.
#     POST requests validate and redirect user to dashboard.
#     """
#     # Bypass if user is logged in
#     if current_user.is_authenticated:
#         return redirect(url_for('user', username=current_user.username))

#     form = LoginForm()
#     # Validate login attempt
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data).first()
#         if user and user.check_password(password=form.password.data):
#             login_user(user)
#             if login_user(user):  # Log in as newly created user
#                 user.last_login = datetime.now()
#                 user.db_commit()
#             next_page = request.args.get('next')
#             return redirect(next_page or url_for('user', username=user.username))
#         flash('Invalid username/password combination')
#         return redirect(url_for('login'))
#     return render_template(
#         'login.html',
#         form=form,
#         title='Log in.',
#         template='login-page',
#         body="Log in with your User account."
#     )


# @app.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     return redirect('/')


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = SignupForm()
#     if form.validate_on_submit():
#         existing_user = User.query.filter_by(username=form.username.data).first()
#         if existing_user is None:
#             user = User(
#                 name=form.name.data,
#                 username=form.username.data,
#                 email=form.email.data,
#                 is_admin=False,
#                 is_activated=False,
#             )
#             user.set_password(form.password.data)
#             user.add_to_db()
#             if login_user(user):  # Log in as newly created user
#                 user.last_login = datetime.now()
#                 user.db_commit()
#             return redirect(url_for('user', username=user.username))
#         flash('A user already exists with that email address.')
#     return render_template(
#         'register.html',
#         title='Create an Account.',
#         form=form,
#         template='register-page',
#         body="Sign up for a user account."
#     )
