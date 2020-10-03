import json
from collections import Counter

from flask import render_template, Blueprint, redirect, abort, request, \
    make_response, jsonify, Response, current_app
from flask_login import login_required, current_user

from .forms import AddList
from ..models import db
from ..models.Shopping import Shop, Category, Item

# Blueprint Configuration
shopping_add_bp = Blueprint(
    'shopping_add_bp', __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/shopping/',
)


@shopping_add_bp.route('/add', methods=['GET', 'POST'])
def add():
    form = AddList()

    if form.validate_on_submit():
        try:
            shop = json.loads(form.shop.data['name'])
            shop = Shop.query.get(shop['id'])
        except json.decoder.JSONDecodeError:
            current_app.logger.info("JSONDecodeError decoding shopping.add input.")
            shop = get_shop_from_fields()
        
        
        print(shop)
        print(form.category.data)
        print(form.items.data)
        print(form.new_items.data)

    return render_template(
        'add.html',
        title='Add Shopping List',
        template='shopping-add',
        form=form,
    )


@shopping_add_bp.route('/shopping/query/shops', methods=['GET', 'POST'])
def query_shops():
    return get_ajax_search_objects(Shop, request.args)


@shopping_add_bp.route('/shopping/query/categories', methods=['GET', 'POST'])
def query_categories():
    return get_ajax_search_objects(Category, request.args)


@shopping_add_bp.route('/shopping/query/items', methods=['GET', 'POST'])
def query_items():
    return get_ajax_search_objects(Item, request.args)


def get_ajax_search_objects(obj, request):
    query = obj.query
    if request and 'keyword' in request.keys():
        if 'contain' in request.keys() and request['contain']:
            query = query.filter(obj.name.contains(request['keyword']))
        else:
            query = query.filter(obj.name.startswith(request['keyword']))

    if 'load' in request:
        query = query.limit(request['limit'])

    return make_response(jsonify({
        "results": [entry.to_ajax() for entry in query]
    }), 200)


@shopping_add_bp.route("/adding_js")
def adding_js():
    return Response(render_template("/js/adding.js"), mimetype="application/javascript;")


@shopping_add_bp.before_request
@login_required
def before_request():
    if not current_user.is_activated:
        abort(403)


def get_shop_from_fiels(name, category):
    existing_shop = Shop.query.filter_by(name=name).join(Shop.category).filter(Category.name == category).first()
    if existing_shop:
        shop = existing_shop
    else:
        shop = Shop(name=name)
        if category:
            existing_category = Category.query.filter_by(name=category).first()
            if existing_category:
                shop.category = existing_category
            else:
                new_category = Category(name=category)
                new_category.save_to_db()
                shop.category = new_category
        shop.save_to_db()
    return shop
