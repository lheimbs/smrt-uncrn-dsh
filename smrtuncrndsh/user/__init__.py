from flask import Blueprint, redirect, url_for, render_template
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
    # if current_user.is_admin:
    #     return redirect(url_for("admin_bp.admin"))
    return render_template('user.html', user=current_user, title=current_user.name)
