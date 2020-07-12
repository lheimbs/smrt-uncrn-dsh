from flask import current_app, abort, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user

from . import admin_bp
from .forms import ListForm
from .misc import add_remove_items_from_liste, get_multiple_items
from ..models.Shopping import Liste


@admin_bp.route('/shopping/list/', methods=['GET', 'POST'])
@login_required
def shopping_list():
    page = request.args.get('page', 1, type=int)
    lists = Liste.query.order_by(Liste.date.desc()).paginate(
        page, current_app.config['SHOPPING_LISTS_PER_PAGE'], False
    )

    next_url = url_for('admin_bp.shopping_list', page=lists.next_num) if lists.has_next else None
    prev_url = url_for('admin_bp.shopping_list', page=lists.prev_num) if lists.has_prev else None

    # .all()  # .limit(30)
    return render_template(
        'shopping_list.html',
        all_lists=lists.items,
        title='Admin Panel - Shopping Lists',
        template='admin-page',
        next_url=next_url,
        prev_url=prev_url,
    )


@admin_bp.route('/shopping/list/edit/<id>', methods=['POST', 'GET'])
@login_required
def edit_shopping_list(id):
    if not current_user.is_admin:
        abort(403)

    current_app.logger.debug(f"Edit shopping list View, list id: {id}")
    liste = Liste.query.filter_by(id=id).scalar()

    list_form = ListForm(obj=liste)
    list_form.items_obj.data = [item for item in liste.items]

    if list_form.validate_on_submit():
        current_app.logger.debug("submit list form")
        list_form.items_obj.process_formdata(request.form.getlist('items_obj'))
        liste.date = list_form.date.data
        liste.price = list_form.price.data
        liste.shop = list_form.shop.data
        liste.category = list_form.category.data

        add_remove_items_from_liste(list_form.items_obj.data, list_form.test.data, liste)

        liste.db_commit()
        return redirect(request.url)
    else:
        if list_form.errors:
            current_app.logger.debug(f"Errors: {list_form.errors}")

    return render_template(
        'edit_shopping_list.html',
        liste=liste,
        form=list_form,
        multiples=get_multiple_items(liste),
        title='Admin Panel - Edit Shopping Liste',
        template="admin-page",
    )


@admin_bp.route('/shopping/list/delete/<id>', methods=['POST', 'GET'])
@login_required
def delete_shopping_list(id):
    if not current_user.is_admin:
        abort(403)

    if id:
        liste = Liste.query.filter_by(id=id).scalar()
        if liste:
            liste.delete_from_db()
            flash(f"List with id {id} successfully deleted from database.")
        else:
            flash(f"List with id {id} does not exist in database.")
    return redirect(url_for('admin_bp.shopping_list'))


@admin_bp.route('/shopping/list/new', methods=['POST', 'GET'])
@login_required
def new_shopping_list():
    if not current_user.is_admin:
        abort(403)

    list_form = ListForm()

    if list_form.validate_on_submit():
        current_app.logger.debug("submit list form")

        liste = Liste(
            date=list_form.date.data,
            price=list_form.price.data,
            shop=list_form.shop.data,
            category=list_form.category.data
        )

        list_form.items_obj.process_formdata(request.form.getlist('items_obj'))
        add_remove_items_from_liste(list_form.items_obj.data, list_form.test.data, liste)

        liste.save_to_db()
        return redirect(url_for('admin_bp.edit_shopping_list', id=liste.id))
    else:
        if list_form.errors:
            current_app.logger.debug(f"Errors: {list_form.errors}")

    return render_template(
        'new_shopping_list.html',
        form=list_form,
        title='Admin Panel - New Shopping Liste',
        template="admin-page",
    )
