from flask import current_app as app
from flask import Blueprint, render_template, abort, render_template_string
from flask_login import current_user

from ..models.Users import User

# admin blueprint
admin_bp = Blueprint(
    'admin_bp',
    __name__,
    template_folder='templates',
    static_folder='static'
)


@admin_bp.route('/admin/', methods=['GET', 'POST'])
def admin():
    """ Admin page """
    if current_user.is_authenticated and not current_user.is_anonymous:
        if current_user.is_admin:
            users = User.query.all()
            return render_template(
                'admin.html',
                title='Admin Panel',
                template='admin-template',
                users=users
            )
    abort(403)
