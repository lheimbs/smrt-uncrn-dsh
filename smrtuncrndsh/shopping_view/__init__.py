from flask import Blueprint, current_app, render_template, request, \
    redirect, flash, url_for, jsonify, make_response, Response, abort

from flask_login import login_required, current_user

from ..admin.forms import ListForm
from ..admin.misc import add_remove_items_from_liste, get_multiple_items, max_price, min_price
from ..models.Shopping import Liste
from ..admin.misc import get_request_dict, get_datatables_order_query, get_datatables_search_query


# Blueprint Configuration
shopping_view_bp = Blueprint(
    'shopping_view_bp', __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/shopping/view',
)


@shopping_view_bp.before_request
@login_required
def before_request():
    pass


@login_required
@shopping_view_bp.route('/list/', methods=['GET', 'POST'])
@shopping_view_bp.route('/list/<int:id>', methods=['GET', 'POST'])
def shopping_view_list(id=-1):
    return render_template(
        'list.html',
        title='Your Shopping Lists',
        template='shopping-view-page',
        data={
            'min_price': min_price(),
            'max_price': max_price(),
        },
        edit_id=id,
    )


@login_required
@shopping_view_bp.route('/list/query', methods=['POST'])
def query_shopping_list():
    args = get_request_dict(request.form)

    query = get_datatables_search_query(Liste, args)
    query = get_datatables_order_query(Liste, args, query)

    query = query.filter_by(user=current_user)

    i_d = [
        i.to_ajax() for i in query.limit(args['length']).offset(args['start']).all()
    ]

    return make_response(jsonify({
        'draw': args['draw'],
        'recordsTotal': Liste.query.count(),
        'recordsFiltered': query.count(),
        'data': i_d,
    }), 200)


@login_required
@shopping_view_bp.route('/list/edit/<int:id>', methods=['POST', 'GET'])
def edit_shopping_list(id):
    current_app.logger.debug(f"Edit shopping list View, list id: {id}")
    liste = Liste.query.filter_by(id=id)
    if not liste:
        current_app.logger.warning(f"Resource unavailable. Liste with id {id} does not exist!")
        # flash("Not found. Something must have gone wrong.", 'error')
        abort(404)

    liste = liste.filter_by(user=current_user).scalar()
    if not liste:
        current_app.logger.warning(
            f"Access denied. User {current_user.get_id()} does have access to this shopping list"
        )
        # flash("Access denied. You do not have access to this shopping list!", 'error')
        abort(401, "You do not have access to this shopping list!")

    list_form = ListForm(obj=liste)
    list_form.items_obj.data = [item for item in liste.items]

    if list_form.validate_on_submit():
        current_app.logger.debug("submit list form")
        list_form.items_obj.process_formdata(request.form.getlist('items_obj'))
        liste.date = list_form.date.data
        liste.price = list_form.price.data
        liste.shop = list_form.shop.data
        liste.category = list_form.category.data
        liste.user = list_form.user.data

        add_remove_items_from_liste(list_form.items_obj.data, list_form.test.data, liste)

        liste.db_commit()
        return redirect(url_for('shopping_view_bp.shopping_view_list', id=liste.id))
    else:
        if list_form.errors:
            current_app.logger.debug(f"Errors: {list_form.errors}")

    return render_template(
        'edit_list.html',
        liste=liste,
        form=list_form,
        multiples=get_multiple_items(liste),
        title='Edit Shopping List',
        template='shopping-view-page',
    )


@login_required
@shopping_view_bp.route('/list/delete/<int:id>', methods=['POST', 'GET'])
def delete_shopping_list(id):
    if id:
        liste = Liste.query.filter_by(user=current_user).filter_by(id=id).scalar()
        if liste:
            liste.delete_from_db()
            flash("List successfully deleted from database.", 'success')
        else:
            flash("Oh-oh... it seems this list does not exist in the database or does not belong to you!", 'error')
    return redirect(url_for('shopping_view_bp.shopping_view_list'))


@login_required
@shopping_view_bp.route("/shopping_view_list_js")
def shopping_view_list_js():
    return Response(render_template("/js/list_view.js"), mimetype="text/javascript")


@login_required
@shopping_view_bp.route("/shopping_edit_list_js")
def shopping_edit_list_js():
    return Response(render_template("/js/edit_list.js"), mimetype="text/javascript")
