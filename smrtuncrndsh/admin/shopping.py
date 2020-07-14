from flask import current_app, abort, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user

from . import admin_bp
from .forms import ListForm, FilterForm
from .misc import add_remove_items_from_liste, get_multiple_items, max_price, min_price, min_date, max_date
from ..models.Shopping import Liste, Item, Shop, Category


@admin_bp.route('/shopping/list/', methods=['GET', 'POST'])
@login_required
def shopping_list():
    page = request.args.get('page', 1, type=int)
    lists = Liste.query.order_by(Liste.date.desc()).paginate(
        page, current_app.config['SHOPPING_LISTS_PER_PAGE'], False
    )
    form = FilterForm()
    data = {
        'min_price': min_price(),
        'max_price': max_price(),
        'min_date': min_date().isoformat(),
        'max_date': max_date().isoformat(),
        'current_min_price': min_price(),
        'current_max_price': max_price(),
        'current_min_date': min_date().isoformat(),
        'current_max_date': max_date().isoformat(),
        'current_shop': "",
        'current_category': "",
        'current_item': "",
    }

    if form.validate():  # request.method == 'POST' and 
        form_min_date = form.date_min.data
        form_max_date = form.date_max.data
        form_min_price = float(form.price_min.data) if form.price_min.data else 0
        form_max_price = float(form.price_max.data) if form.price_max.data else 0
        form_shop = form.shop.data
        form_category = form.category.data
        form_item = form.item.data
        current_app.logger.debug(f"{form_min_date, form_max_date, form_min_price, form_max_price, form_shop, form_category, form_item}")

        lists_query = Liste.query
        if form_min_date and form_max_date and form_min_date <= form_max_date:
            current_app.logger.debug("Apply daterange filter")
            lists_query = lists_query.filter(
                Liste.date > form_min_date,
                Liste.date < form_max_date,
            )
            data['current_min_date'] = form_min_date.isoformat()
            data['current_max_date'] = form_max_date.isoformat()
        else:
            data['current_min_date'] = min_date().isoformat()
            data['current_max_date'] = max_date().isoformat()
        if form_min_price and form_max_price and form_min_price <= form_max_price:
            current_app.logger.debug("Apply price range filter")
            lists_query = lists_query.filter(
                Liste.price > form_min_price,
                Liste.price < form_max_price,
            )
            data['current_min_price'] = form_min_price
            data['current_max_price'] = form_max_price
        else:
            data['current_min_price'] = form_min_price
            data['current_max_price'] = form_max_price
        if form_shop:
            current_app.logger.debug("Apply shop filter")
            lists_query = lists_query.join(Liste.shop).filter(Shop.name == form_shop)
            data['current_shop'] = form_shop
        else:
            data['current_shop'] = ''
        if form_category:
            current_app.logger.debug("Apply vategory filter")
            lists_query = lists_query.join(Liste.category).filter(Category.name == form_category)
            data['current_category'] = form_category
        else:
            data['current_category'] = ''
        if form_item:
            current_app.logger.debug("Apply item filter")
            # for item in form_item.split(','):
            #     lists_query = lists_query.filter(
            #         Liste.items.has(Item.name == item)
            #     )

        if form_min_date == min_date() and form_max_date == max_date() and \
                form_min_price == min_price() and form_max_price == max_price() and \
                not form_shop and not form_category and not form_item:
            lists = lists_query.order_by(Liste.date.desc()).paginate(
                page, current_app.config['SHOPPING_LISTS_PER_PAGE'], False
            )
        else:
            lists = lists_query.order_by(Liste.date.desc()).paginate(
                1, lists_query.count(), False
            )

        next_url = url_for('admin_bp.shopping_list', page=lists.next_num) if lists.has_next else None
        prev_url = url_for('admin_bp.shopping_list', page=lists.prev_num) if lists.has_prev else None

        return render_template(
            'shopping_list.html',
            form=form,
            title='Admin Panel - Shopping Lists',
            template='admin-page',
            next_url=next_url,
            prev_url=prev_url,
            lists=lists,
            data=data,
        )
    else:
        if form.errors:
            current_app.logger.debug(form.errors)

        # return redirect(request.url)

    next_url = url_for('admin_bp.shopping_list', page=lists.next_num) if lists.has_next else None
    prev_url = url_for('admin_bp.shopping_list', page=lists.prev_num) if lists.has_prev else None

    # .all()  # .limit(30)
    return render_template(
        'shopping_list.html',
        title='Admin Panel - Shopping Lists',
        template='admin-page',
        form=form,
        lists=lists,
        next_url=next_url,
        prev_url=prev_url,
        data=data,
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
            flash(f"List with id {id} successfully deleted from database.", 'success')
        else:
            flash(f"List with id {id} does not exist in database.", 'error')
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
