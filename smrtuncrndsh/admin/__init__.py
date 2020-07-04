from flask import Blueprint, render_template, abort, request, jsonify, make_response, redirect, url_for, current_app
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import RadioField, SelectField

from ..models.Users import User
# from .forms import ActivateForm

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
        template='activation-page',
        users=users,
        form=form
    )

# @admin_bp.route('/activation/', methods=['GET', 'POST'])
# @login_required
# def activation():
#     if not current_user.is_admin:
#         abort(403)

#     if request.method == 'GET':
#         print('GET')
#         data = []
#         for user in User.query.filter(User.is_activated == False).all():     # noqa: E712
#             data.append({'user': user, 'form': ActivateForm(user.username)})
#         return render_template(
#             'activation.html',
#             title='Admin Panel - Activation',
#             template='activation-page',
#             data=data,
#         )

#     formid = request.args.get('formid', '')
#     submitted_user, submitted_form = None, None
#     if formid:
#         for date in data:
#             user = date['user']
#             form = date['form']
#             if form.username == formid:
#                 break
#     if submitted_form:
#         if form.validate_on_submit():
#             print(form.username, user)
#             user.activate_user()

#             data = []
#             for user in User.query.filter(User.is_activated == False).all():     # noqa: E712
#                 data.append({'user': user, 'form': ActivateForm(user.username)})
#             # return render_template(
#             #     'activation.html',
#             #     title='Admin Panel - Activation',
#             #     template='activation-page',
#             #     data=data,
#             # )

#     return render_template(
#         'activation.html',
#         title='Admin Panel - Activation',
#         template='activation-page',
#         data=data,
#     )


# @admin_bp.route('/activation/<formid>', methods=['POST'])
# @login_required
# def toggle_activated():
#     if not current_user.is_admin:
#         res = make_response(jsonify({"message": "Not Authorized"}), 403)
#     else:
#         req = request.get_json()
#         user_id = int(req['id'].split('-')[-1])
#         user = User.query.filter(User.id == user_id).scalar()
#         print(req, user)
#         if user:
#             user.activate_user()

#         res = make_response(redirect(url_for('admin_bp.activation')))  # jsonify({"message": "OK"}), 200)
#         # return res
#     return res
