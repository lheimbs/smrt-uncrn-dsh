from flask import flash, redirect, url_for
from flask_login import LoginManager, current_user, AnonymousUserMixin


class LoginManagerWithActivation(LoginManager):
    def unactivated(self):
        if not current_user.is_authenticated:
            return self.unauthorized()
        flash(
            "Tour account needs to be activated to access this page. "
            "Please wait for your account to get activated and try again later "
            "or use another account.",
            "error"
        )
        return redirect(url_for('user_bp.user'))


class MyAnonymousUser(AnonymousUserMixin):
    is_admin = False
    is_activated = False
