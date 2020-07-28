from flask import render_template, Blueprint, redirect
from flask_login import login_required, logout_user


# Blueprint Configuration
home_bp = Blueprint(
    'home_bp', __name__,
    template_folder='templates',
    static_folder='static'
    # static_url_path='/home/static'
)


@home_bp.route('/')
def home():
    """ home page with basic infos """
    return render_template(
        'home.html',
        title='Home',
        template='home-page',
        body="Homepage."
    )


@home_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')
