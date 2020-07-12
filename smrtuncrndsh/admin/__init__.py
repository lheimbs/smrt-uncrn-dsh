from datetime import datetime

from flask import Blueprint, render_template, abort, redirect, url_for, current_app, request
#  , request, jsonify, make_response
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import RadioField
from wtforms.ext.sqlalchemy.orm import model_form
# from wtforms.validators import Required
# from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField

# from ..models import db
from ..models.Users import User
from ..models.Shopping import List
# , Shop, Category, Item
from .forms import ListForm

admin_bp = Blueprint(
    'admin_bp', __name__,
    template_folder='templates',
    static_folder='static'
)


@admin_bp.route('/users/')
@login_required
def users():
    if not current_user.is_admin:
        abort(403)

    users_obj = User.query.all()
    return render_template(
        'users.html',
        all_users=users_obj,
        title='Admin Panel - Users',
        template='admin-page'
    )


@admin_bp.route('/users/edit/<username>', methods=['POST', 'GET'])
@login_required
def edit_user(username):
    if not current_user.is_admin:
        abort(403)

    current_app.logger.debug(f"Edit User View, user: {username}")
    user = User.query.filter_by(username=username).scalar()
    UserForm = model_form(User, base_class=FlaskForm, exclude=['password', 'created_on', 'last_login'])
    UserForm.is_admin.kwargs['validators'] = []
    UserForm.is_activated.kwargs['validators'] = []
    user_form = UserForm(obj=user)

    print(dir(user_form))

    if user_form.validate_on_submit():
        user.name = user_form.name.data
        user.username = user_form.username.data
        user.email = user_form.email.data
        user.is_activated = user_form.is_activated.data
        user.is_admin = user_form.is_admin.data
        user.db_commit()

        return redirect(url_for('admin_bp.users'))
    else:
        current_app.logger.debug(user_form.errors)

    return render_template(
        'edit_users.html',
        user=user,
        form=user_form,
        title='Admin Panel - Edit User',
        template="admin-page",
    )


@admin_bp.route('/users/delete/<username>')
@login_required
def delete_user(username):
    if not current_user.is_admin:
        abort(403)

    if username:
        user = User.query.filter_by(username=username).scalar()
        if user:
            user.delete_from_db()

    return redirect(url_for('admin_bp.users'))

    current_app.logger.debug(f"Delete User View, user: {username}")
    users_obj = User.query.all()
    return render_template(
        'users.html',
        all_users=users_obj,
        title='Admin Panel - Users',
        template='admin-page'
    )


@admin_bp.route('/activation/', methods=['GET', 'POST'])
@login_required
def activation():
    if not current_user.is_admin:
        abort(403)

    class ActivateForm(FlaskForm):
        pass

    users = User.query.filter(User.is_activated == False).all()      # noqa: E712
    for user in users:
        setattr(
            ActivateForm, user.username, RadioField(
                u'Activate',
                choices=[('yes', 'Yes'), ('no', 'No'), ('delete', 'Delete')], default='no'
            )
        )

    form = ActivateForm()
    if form.validate_on_submit():
        for user in users:
            formfield = getattr(form, user.username, None)
            if not formfield:
                current_app.logger.warning(f"Formfield {user.username} does not exist!")
            else:
                print(formfield.data)
                if formfield.data == 'yes':
                    user.activate_user()
                elif formfield.data == 'delete':
                    current_app.logger.warning(f"Deleting user {user.username}")
                    user.delete_from_db()

        users = User.query.filter(User.is_activated == False).all()      # noqa: E712
    else:
        current_app.logger.debug(form.errors)

    return render_template(
        'activation.html',
        title='Admin Panel - Activation',
        template='admin-page',
        users=users,
        form=form
    )


@admin_bp.route('/shopping/list/', methods=['GET', 'POST'])
@login_required
def shopping_list():
    lists = List.query.order_by(List.date.desc()).limit(5).all()
    return render_template(
        'shopping_list.html',
        all_lists=lists,
        title='Admin Panel - Shopping Lists',
        template='admin-page'
    )


@admin_bp.route('/shopping/list/edit/<id>', methods=['POST', 'GET'])
@login_required
def edit_shopping_list(id):
    if not current_user.is_admin:
        abort(403)

    current_app.logger.debug(f"Edit shopping list View, list id: {id}")
    liste = List.query.filter_by(id=id).scalar()

    list_form = ListForm(obj=liste)
    list_form.items_obj.data = [item for item in liste.items]

    if list_form.validate_on_submit():
        print(request.form.getlist('items_obj'))
        current_app.logger.debug("submit list form")
        list_form.items_obj.process_formdata(request.form.getlist('items_obj'))
        current_app.logger.debug(list_form.date.data)
        current_app.logger.debug(list_form.price.data)
        current_app.logger.debug(list_form.shop.data)
        current_app.logger.debug(list_form.category.data)
        current_app.logger.debug(list_form.items_obj.data)
        current_app.logger.debug(list_form.test.data)

        liste.date = datetime.combine(list_form.date.data, datetime.min.time())
        liste.price = list_form.price.data
        liste.shop = list_form.shop.data
        liste.category = list_form.category.data

        # add new items:
        for item in list_form.items_obj.data:
            if item.id in list_form.test.data.keys():
                for _ in range(list_form.test.data[item.id] - liste.items.count(item)):
                    current_app.logger.debug(f"Add <Item({item.id}, {item.name})> to list with id {liste.id}.")
                    liste.items.append(item)

        # remove deleted items
        for item in liste.items:
            if item not in list_form.items_obj.data:
                current_app.logger.debug(f"Remove <Item({item.id}, {item.name})> from list with id {liste.id}.")
                liste.items.pop(item)

        liste.db_commit()

        print(List.query.filter(List.id==liste.id).scalar())

        return redirect(request.url)
    else:
        current_app.logger.debug(f"Errors: {list_form.errors}")

    return render_template(
        'edit_shopping_list.html',
        liste=liste,
        form=list_form,
        title='Admin Panel - Edit Shopping List',
        template="admin-page",
    )
