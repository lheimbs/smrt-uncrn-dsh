from flask import abort, render_template, request, redirect, flash, url_for, \
    Markup, render_template_string, jsonify, make_response
from flask_login import login_required, current_user

from .. import admin_bp
from ..forms import ShopForm
from ...models import db
from ...models.Shopping import Shop
from ..misc import get_request_dict, get_datatables_order_query, get_datatables_search_query


@admin_bp.route('/shopping/shop/')
@login_required
def shopping_shop():
    if not current_user.is_admin:
        abort(403)

    # shops = Shop.query.order_by(Shop.name).all()
    return render_template(
        'shopping/shop.html',
        title='Admin Panel - Shopping Shops',
        template='admin-page',
        # shops=shops,
    )


@admin_bp.route('/shopping/shop/query', methods=['POST'])
@login_required
def query_shopping_shops():
    if not current_user.is_admin:
        abort(403)
    args = get_request_dict(request.form)

    query = get_datatables_search_query(Shop, args)
    query = get_datatables_order_query(Shop, args, query)

    # print('length', args['length'], 'start', args['start'])
    i_d = [
        i.to_ajax() for i in query.limit(args['length']).offset(args['start']).all()
    ]

    return make_response(jsonify({
        'draw': args['draw'],
        'recordsTotal': Shop.query.count(),
        'recordsFiltered': query.count(),
        'data': i_d,
    }), 200)


@admin_bp.route('/shopping/shop/new/', methods=['POST', 'GET'])
@login_required
def new_shopping_shop():
    if not current_user.is_admin:
        abort(403)

    form = ShopForm()

    if form.validate_on_submit():
        shopname = form.name.data
        if Shop.query.filter_by(name=shopname).count() > 0:
            flash("A shop with this name already exists. Try another name.", 'error')
            return redirect(request.url)
        else:
            new_shop = Shop(name=shopname)
            new_shop.category = form.category.data
            new_shop.save_to_db()
            flash(f"Successfully added Shop {shopname}.", 'success')
            return redirect(url_for("admin_bp.shopping_shop"))
    return render_template(
        'shopping/new_shop.html',
        title='Admin Panel - Shopping Shops - New',
        template='admin-page',
        form=form,
    )


@admin_bp.route('/shopping/shop/edit/<int:id>', methods=['POST', 'GET'])
@login_required
def edit_shopping_shop(id):
    if not current_user.is_admin:
        abort(403)
    shop = Shop.query.filter_by(id=id).first_or_404()
    form = ShopForm(obj=shop)
    form.populate_obj(shop)

    with db.session.no_autoflush:
        if form.validate_on_submit():
            shopname = form.name.data
            shopcategory = form.category.data

            test_dupl_shop = Shop.query.filter_by(
                name=shopname,
                category=shopcategory
            ).all()
            if test_dupl_shop:
                flash("A Shop with these attributes already exists.", 'warning')
                return redirect(request.url)

            shop = change_shop_attr(shopname, shopcategory, shop)
            shop.db_commit()

            return redirect(url_for("admin_bp.shopping_shop"))
    return render_template(
        'shopping/edit_shop.html',
        title='Admin Panel - Shopping Shops - New',
        template='admin-page',
        form=form,
        shop=shop
    )


@admin_bp.route('/shopping/shop/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_shopping_shop(id):
    if not current_user.is_admin:
        abort(403)

    if id:
        shop = Shop.query.filter_by(id=id).first_or_404()
        if shop and shop.lists:
            links = []
            for liste in shop.lists:
                links.append(render_template_string(
                    f"<a href=\"{{{{ url_for('admin_bp.edit_shopping_list', id={liste.id}) }}}}\">{liste.id}</a>"
                ))
            flash("Cannot delete Shop because it exists in a List.", 'error')
            flash(Markup(f"Remove it from these Lists to allow deletion: {', '.join(links)}."), 'info')
        elif shop:
            try:
                shop.delete_from_db()
                flash(f"Shop with id {id} successfully deleted from database.", 'success')
            except Exception as exc:
                flash(str(exc), 'info')
                db.session.rollback()
        else:
            flash(f"Shop with id {id} does not exist in database.", 'warning')
    return redirect(url_for('admin_bp.shopping_shop'))


@admin_bp.route("/shop_js")
@login_required
def shop_js():
    return render_template("/js/shop.js")


def change_shop_attr(name, category, shop):
    if shop.name != name:
        shop.name = name
        flash(f"Successfully changed name to {name}.", 'success')
    if shop.category != category:
        shop.category = category
        flash(
            f"Successfully changed Shops Category to {category.name if category else None}.",
            'success'
        )
    return shop
