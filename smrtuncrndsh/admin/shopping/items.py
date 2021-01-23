from sqlalchemy import inspect
from flask import render_template, flash, jsonify, make_response, current_app, \
    request, redirect, url_for, Markup, render_template_string, Response

from .. import admin_bp
from ..forms import ItemForm, ItemsForm
from ...models.Shopping import Item  # , Category
from ...models import db
from ..misc import get_request_dict, get_datatables_order_query, get_datatables_search_query


@admin_bp.route('/shopping/item/')
def shopping_item():
    return render_template(
        'shopping/item.html',
        title='Admin Panel - Shopping Items',
        template='admin-page',
    )


@admin_bp.route('/shopping/item/query', methods=['POST'])
def query_shopping_items():
    args = get_request_dict(request.form)

    query = get_datatables_search_query(Item, args)
    query = get_datatables_order_query(Item, args, query)
    i_d = [
        i.to_ajax() for i in query.limit(args['length']).offset(args['start']).all()
    ]
    return make_response(jsonify({
        'draw': args['draw'],
        'recordsTotal': Item.query.count(),
        'recordsFiltered': query.count(),
        'data': i_d,
    }), 200)


@admin_bp.route('/shopping/item/new/', methods=['POST', 'GET'])
def new_shopping_item():
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
            item.category = form.category.data
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
@admin_bp.route('/shopping/item/edit/<int_list:ids>', methods=['POST', 'GET'])
def edit_shopping_item(id=None, ids=None):
    items = get_items_from_ids(id, ids)
    if not items:
        flash("No valid items supplied that can be edited!", 'error')
        return redirect(url_for('admin_bp.shopping_items'))
    elif len(items) == 1:
        form = ItemForm(obj=items[0])
    else:
        form = ItemsForm()

    if form.validate_on_submit():
        form_data = dict(
            name=form.name.data,
            price=form.price.data,
            volume=form.volume.data,
            price_per_volume=form.price_per_volume.data,
            sale=form.sale.data,
            note=form.note.data,
            category=form.category.data,
        )

        if len(items) == 1:
            test_dupl_item = Item.query.filter_by(**form_data).first()
            handle_existing_item(items[0], test_dupl_item, form_data)
        else:
            for item in items:
                changed_attrs = get_changed_attributes(**form_data)
                blacklisted_attrs = ('id', 'lists', 'category_id')
                existing_attrs = {}
                for attr in inspect(item).attrs:
                    if attr.key not in blacklisted_attrs:
                        existing_attrs[attr.key] = getattr(item, attr.key)

                existing_item = Item.query.filter_by(
                    **{**existing_attrs, **changed_attrs}
                ).first()
                handle_existing_item(item, existing_item, changed_attrs)

        return redirect(url_for("admin_bp.shopping_item"))
    elif form.is_submitted():
        flash("Something failed processing your data. Please try again later.", 'error')
        return redirect(url_for("admin_bp.shopping_item"))

    return render_template(
        'shopping/edit_item_modal.html',
        title='Admin Panel - Edit Shopping Item',
        template='admin-page',
        form=form,
        items=[item.id for item in items],
    )


@admin_bp.route('/shopping/item/delete/<int:id>', methods=['GET', 'POST'])
@admin_bp.route('/shopping/item/delete/<int_list:ids>', methods=['GET', 'POST'])
def delete_shopping_item(id=None, ids=None):
    items = get_items_from_ids(id, ids)
    if not items:
        flash("No valid items supplied. Please try again.", 'error')
        return redirect(url_for("admin_bp.shopping_item"))
    print(items)

    for item in items:
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
            item_id = item.id
            current_app.logger.debug(f"Remove item {item_id}.")
            try:
                item.delete_from_db()
                flash(f"Item with id {item_id} successfully deleted from database.", 'success')
            except Exception as exc:
                flash(str(exc), 'info')
                db.session.rollback()
        else:
            flash("No item like that exists in this database.", 'warning')
    return redirect(url_for('admin_bp.shopping_item'))


@admin_bp.route("/item_js")
def item_js():
    return Response(render_template("/js/item.js"), mimetype="text/javascript")


def handle_existing_item(item, existing_item, change_attributes):
    if not existing_item:
        change_item_attr(item, **change_attributes)
        item.db_commit()
    elif existing_item and existing_item != item:
        flash(f"Item {existing_item.id} already has these attributes. Replacing item {item.id}.", 'info')
        replace_item(item, existing_item)
    else:
        flash(f"No change detected. Skipping item {item.id}.", 'info')


def change_item_attr(item, **kwargs):
    if 'supress_flash' in kwargs.keys():
        supress_flash = kwargs['supress_flash']
        kwargs.pop('supress_flash')
    else:
        supress_flash = False

    for key, value in kwargs.items():
        if hasattr(item, key) and getattr(item, key) != value and (getattr(item, key) or value):
            orig_val = getattr(item, key)
            setattr(item, key, value)
            current_app.logger.debug(f"Changed item {item.id} attr {key}: '{orig_val}' to '{value}'")
            if not supress_flash:
                flash((
                    f"Successfully changed {key} to "
                    f"{value if key != 'category' else value.name if value else None} of item {item.id}."
                ), 'success')
    return item


def replace_item(original_item, new_item):
    for liste_item in original_item.lists:
        liste = liste_item.liste
        current_app.logger.debug(
            f"Replacing item {original_item.id} in Liste {liste.id} with new item {new_item.id}."
        )
        liste.items.remove(original_item)
        liste.items.append(new_item)
        liste.db_commit()
    original_item.db_commit()
    new_item.db_commit()


def get_items_from_ids(id, ids):
    if id and ids is None:
        ids = [id]
    items = []
    for id in ids:
        item = Item.query.filter_by(id=id).first_or_404()
        if item:
            items.append(item)
        else:
            flash(f"Supplied item is invalid (id: {id})!", 'warning')
    return items


def get_changed_attributes(**kwargs):
    return {key: val for key, val in kwargs.items() if val}
