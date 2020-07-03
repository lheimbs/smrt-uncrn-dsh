
from flask import current_app, redirect, url_for, request  # , abort
from flask_login import current_user
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from wtforms.fields import PasswordField

from ..models.Users import User
from ..models import db


class UserActivateModelView(ModelView):
    can_create = False
    can_edit = True
    can_delete = False
    column_list = ('name', 'email', 'username', 'is_activated')
    column_editable_list = ('is_activated',)
    # form_columns = ('is_activated')

    def __init__(self, session, **kwargs):
        super(UserActivateModelView, self).__init__(User, session, **kwargs)

    def update_model(self, form, model):
        try:
            old_password = model.password
            form.populate_obj(model)
            if form.password.data != old_password:
                if not len(form.password.data) > 0:
                    model.password = old_password
                else:
                    model.set_password(form.password.data)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return False

    def is_accessible(self):
        return current_user.is_admin


class UserModelView(ModelView):
    can_edit = True
    column_list = ('name', 'email', 'username', 'created_on', 'last_login', 'is_admin', 'is_activated')
    form_columns = ('name', 'email', 'username', 'password', 'is_admin', 'is_activated')
    form_extra_fields = {
        'password': PasswordField('Password')
    }

    def __init__(self, session, **kwargs):
        super(UserModelView, self).__init__(User, session, **kwargs)

    def create_model(self, form):
        try:
            new_user = User()
            form.populate_obj(new_user)
            new_user.set_password(form.password.data)
            new_user.add_to_db()
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return False

    def update_model(self, form, model):
        try:
            old_password = model.password
            form.populate_obj(model)
            if form.password.data != old_password:
                if not len(form.password.data) > 0:
                    model.password = old_password
                else:
                    model.set_password(form.password.data)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return False

    def is_accessible(self):
        return current_user.is_admin


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if current_user.is_admin:
            current_app.logger.debug("render /admin")
            return self.render(
                'admin/index.html',
                # title='Admin Panel',
            )
        return redirect(url_for('auth_bp.login', next=request.url))


class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('auth_bp.login', next=request.url))
