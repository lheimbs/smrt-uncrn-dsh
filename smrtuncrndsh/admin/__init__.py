
from flask_admin import Admin

from .views import UserModelView, MyAdminIndexView, UserActivateModelView
from ..models import db


def init_admin(app):
    admin_obj = Admin(index_view=MyAdminIndexView())
    admin_obj.add_view(UserModelView(db.session))
    admin_obj.add_view(UserActivateModelView(db.session, name='Activate', endpoint='Activate'))
    admin_obj.init_app(app)
