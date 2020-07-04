from flask import Blueprint, render_template  # , redirect, url_for
from flask_login import login_required, current_user

# Blueprint Configuration
user_bp = Blueprint(
    'user_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@user_bp.route('/user')
@login_required
def user():
    return render_template('user.html', user=current_user, title=current_user.name)
