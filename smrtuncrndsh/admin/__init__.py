from flask import Blueprint, abort
from flask_login import login_required, current_user

admin_bp = Blueprint(
    'admin_bp', __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix="/admin/"
)


@admin_bp.before_request
@login_required
def before_request():
    if not current_user.is_admin:
        abort(403)
