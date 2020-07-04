from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user

from ..models.Users import User

admin_bp = Blueprint(
    'admin_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@admin_bp.route('/users/')
@login_required
def users():
    if current_user.is_admin:
        users_obj = User.query.all()
        return render_template(
            'users.html',
            all_users=users_obj,
            title='Admin Panel - Users',
            template='users-page'
        )
    abort(403)


@admin_bp.route('/activation/')
@login_required
def activation():
    if current_user.is_admin:
        users = User.query.filter(User.is_activated == False).all()
        return render_template(
            'activation.html',
            act_users=users,
            title='Admin Panel - Activation',
            template='activation-page'
        )
    abort(403)


# <!-- {{ url_for('admin_bp.edit', userid=user.id) }} -->
