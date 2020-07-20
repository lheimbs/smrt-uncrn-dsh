from flask import abort, render_template, flash, jsonify, make_response
from flask import request, redirect, url_for, Markup, render_template_string
from flask_login import login_required, current_user

from .. import admin_bp
from ..forms import ItemForm
from ...models.Shopping import Item  # , Category
from ...models import db
from ..misc import get_request_dict, get_datatables_order_query, get_datatables_search_query
# from ..misc.datatables import get_request_dict, get_datatables_order_query, get_datatables_search_query


@admin_bp.route('/shopping/item/')
@login_required
def shopping_item():
    if not current_user.is_admin:
        abort(403)

    # items = Item.query.order_by(Item.name).all()
    return render_template(
        'shopping/item.html',
        title='Admin Panel - Shopping Items',
        template='admin-page',
        # items=items,
    )


@admin_bp.route('/shopping/item/query', methods=['POST'])
@login_required
def query_shopping_items():
    # if not current_user.is_admin:
    #     abort(403)
    args = get_request_dict(request.form)

    query = get_datatables_search_query(Item, args)
    query = get_datatables_order_query(Item, args, query)

    # print('length', args['length'], 'start', args['start'])
    i_d = [
        i.to_ajax() for i in query.limit(args['length']).offset(args['start']).all()
    ]

    return make_response(jsonify({
        'draw': args['draw'],
        'recordsTotal': Item.query.count(),
        'recordsFiltered': query.count(),
        'data': i_d,
    }), 200)
    # return make_response(jsonify({"message": "OK"}), 200)


@admin_bp.route('/shopping/item/new/', methods=['POST', 'GET'])
@login_required
def new_shopping_item():
    if not current_user.is_admin:
        abort(403)

    form = ItemForm()

    if form.validate_on_submit():
        item = Item(
            name=form.name.data,
            price=form.price.data,
            volume=form.volume.data,
            price_per_volume=form.price_per_volume.data,
            sale=form.sale.data,
            note=form.note.data,
        )
        if item.exists():
            flash("An Item with these attributes already exists.", 'error')
            return redirect(request.url)
        else:
            item.category = form.category.data['name']
            item.save_to_db()
            flash(f"Successfully added Item {item.name}.", 'success')
            return redirect(url_for("admin_bp.shopping_item"))

    return render_template(
        'shopping/new_item.html',
        title='Admin Panel - New Shopping Item',
        template='admin-page',
        form=form,
    )


@admin_bp.route('/shopping/item/edit/<int:id>', methods=['POST', 'GET'])
@login_required
def edit_shopping_item(id):
    if not current_user.is_admin:
        abort(403)

    item = Item.query.filter_by(id=id).scalar()
    if not item:
        flash("Sorry this item does not exist anymore. Try refreshing the site.", 'error')
        return redirect(url_for('admin_bp.shopping_items'))

    form = ItemForm(obj=item)

    if form.validate_on_submit():
        name = form.name.data
        price = form.price.data
        volume = form.volume.data
        ppv = form.price_per_volume.data
        sale = form.sale.data
        note = form.note.data
        category = form.category.data['name']

        test_dupl_item = Item.query.filter_by(
            name=name, price=price, volume=volume,
            price_per_volume=ppv, sale=sale, note=note,
            category=category
        ).all()
        if test_dupl_item:
            flash("An Item with these attributes already exists.", 'error')
            return redirect(request.url)

        item = change_item_attr(name, price, volume, ppv, sale, note, category, item)
        item.db_commit()

        return redirect(url_for("admin_bp.shopping_item"))
    return render_template(
        'shopping/edit_item.html',
        title='Admin Panel - Edit Shopping Item',
        template='admin-page',
        form=form,
        item=item,
    )


@admin_bp.route('/shopping/item/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_shopping_item(id):
    if not current_user.is_admin:
        abort(403)

    print("delete item")
    item = Item.query.filter_by(id=id).first_or_404()
    if item and item.lists:
        links = set()
        for listeitem in item.lists:
            links.add(render_template_string(
                f"<a href=\"{{{{ url_for('admin_bp.edit_shopping_list', "
                f"id={listeitem.liste.id}) }}}}\">{listeitem.liste.id}</a>"
            ))
        flash("Cannot delete Item because it exists in other List(s).", 'error')
        flash(Markup(f"Remove it from these Lists to allow deletion: {', '.join(links)}."), 'info')
    elif item:
        try:
            item.delete_from_db()
            flash(f"Item with id {id} successfully deleted from database.", 'success')
        except Exception as exc:
            flash(str(exc), 'info')
            db.session.rollback()
    else:
        flash(f"Item with id {id} does not exist in database.", 'warning')
    return redirect(url_for('admin_bp.shopping_item'))


def change_item_attr(name, price, volume, ppv, sale, note, category, item):
    if item.name != name:
        item.name = name
        flash(f"Successfully changed name to {name}.", 'success')
    if item.price != price:
        item.price = price
        flash(f"Successfully changed price to {price}.", 'success')
    if item.volume != volume:
        item.volume = volume
        flash(f"Successfully changed volume to {volume}.", 'success')
    if item.price_per_volume != ppv:
        item.price_per_volume = ppv
        flash(f"Successfully changed price per volume to {ppv}.", 'success')
    if item.sale != sale:
        item.sale = sale
        flash(f"Successfully changed sale to {sale}.", 'success')
    if item.category != category:
        item.category = category
        flash(
            f"Successfully changed Shops Category to {category.name if category else None}.",
            'success'
        )
    return item
