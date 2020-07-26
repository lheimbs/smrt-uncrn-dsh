from flask import current_app, render_template, request, \
    redirect, flash, url_for, jsonify, make_response, Response

from .. import admin_bp
from ..forms import ListForm
from ..misc import add_remove_items_from_liste, get_multiple_items, max_price, min_price
from ...models.Shopping import Liste
from ..misc import get_request_dict, get_datatables_order_query, get_datatables_search_query


@admin_bp.route('/shopping/list/', methods=['GET', 'POST'])
def shopping_list():
    return render_template(
        'shopping/list.html',
        title='Admin Panel - Shopping Lists',
        template='admin-page',
        data={
            'min_price': min_price(),
            'max_price': max_price(),
        }
    )


@admin_bp.route('/shopping/list/query', methods=['POST'])
def query_shopping_list():
    args = get_request_dict(request.form)

    query = get_datatables_search_query(Liste, args)
    query = get_datatables_order_query(Liste, args, query)

    i_d = [
        i.to_ajax() for i in query.limit(args['length']).offset(args['start']).all()
    ]

    return make_response(jsonify({
        'draw': args['draw'],
        'recordsTotal': Liste.query.count(),
        'recordsFiltered': query.count(),
        'data': i_d,
    }), 200)


@admin_bp.route('/shopping/list/edit/<id>', methods=['POST', 'GET'])
def edit_shopping_list(id):
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
        'shopping/edit_list.html',
        liste=liste,
        form=list_form,
        multiples=get_multiple_items(liste),
        title='Admin Panel - Edit Shopping Liste',
        template="admin-page",
    )


@admin_bp.route('/shopping/list/delete/<id>', methods=['POST', 'GET'])
def delete_shopping_list(id):
    if id:
        liste = Liste.query.filter_by(id=id).scalar()
        if liste:
            liste.delete_from_db()
            flash(f"List with id {id} successfully deleted from database.", 'success')
        else:
            flash(f"List with id {id} does not exist in database.", 'error')
    return redirect(url_for('admin_bp.shopping_list'))


@admin_bp.route('/shopping/list/new', methods=['POST', 'GET'])
def new_shopping_list():
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
        'shopping/new_list.html',
        form=list_form,
        title='Admin Panel - New Shopping Liste',
        template="admin-page",
    )


@admin_bp.route("/list_js")
def list_js():
    return Response(render_template("/js/list.js"), mimetype="text/javascript")
