from flask import render_template, Blueprint, redirect, abort, request, \
    make_response, jsonify
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
    form.shop.datalist = [shop.to_dict() for shop in Shop.query]#db.session.query(Shop.name).all()
    form.category.datalist = db.session.query(Category.name).all()
    form.items.datalist = db.session.query(Item.name).all()

    if form.validate_on_submit():
        print(form.date.data)
        print(form.price.data)
        print(form.shop.data)
        print(form.category.data)
        print(form.items.data)

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

# @shopping_add_bp.before_request
# @login_required
# def before_request():
#     if not current_user.is_activated:
#         abort(403)
