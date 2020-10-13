import json
from collections import Counter

from flask import render_template, Blueprint, redirect, abort, request, \
    make_response, jsonify, Response, current_app, flash
from flask_login import login_required, current_user

from .forms import AddList, AddItem
from ..models import db
from ..models.Shopping import Shop, Category, Item, Liste

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
        # try:
        #     shop_dict = json.loads(form.shop.data['name'])
        #     shop = Shop.query.filter_by(id=shop_dict['id']).first_or_404()
        # except json.decoder.JSONDecodeError:
        #     current_app.logger.info("JSONDecodeError decoding shopping.add input.")
        #     shop = get_shop_from_fields()
        # new_list = Liste(date=form.date.data, price=float(form.price.data))
        shop = get_shop(form.shop.data)
        category = get_category(form.category.data)

        new_list = Liste(form.date.data, float(form.price.data), shop, category)
        item_list = get_list(form.items.data)

        new_list.items = item_list

        print(new_list)
        print(current_user)

    return render_template(
        'add.html',
        title='Add Shopping List',
        template='shopping-add',
        form=form,
    )


def get_shop(shop_data):
    try:
        shop_dict = json.loads(shop_data['name'])
        if isinstance(shop_dict, dict) and 'id' in shop_dict.keys():
            current_app.logger.debug(f"Using shop with id '{shop_dict['id']}' and name '{shop_dict['name']}'.")
            return Shop.query.filter_by(id=shop_dict['id']).first_or_404()
        else:
            current_app.logger.error(f"The given shop has not a vlid name ('{shop_data['name']}')!")
            flash("The shops name in not valid! Please choose another one.", "error")
            return None
    except json.decoder.JSONDecodeError:
        current_app.logger.debug(f"JSONDecodeError: shop '{shop_data['name']}' is not a flexdatalist item.")

    shop = Shop(name=shop_data['name'])
    if shop.exists():
        current_app.logger.debug("Shop with name '{}' exists.")
        shop = Shop.query.filter_by(name=shop_data['name']).first_or_404()
        current_app.logger.debug(f"Using shop with id '{shop.id}'.")
    else:
        category = get_category(shop_data['category'])
        if category:
            shop.category = category
        shop.save_to_db()
        current_app.logger.info(f"Added new shop {shop} to database.")
    return shop


def get_category(category_data):
    if not category_data:
        return None

    try:
        category_dict = json.loads(category_data)
        if isinstance(category_dict, dict) and 'id' in category_dict.keys():
            current_app.logger.debug(
                f"Using category with id '{category_dict['id']}' and name '{category_dict['name']}'."
            )
            return Category.query.filter_by(id=category_dict['id']).first_or_404()
        elif isinstance(category_dict, str):
            category_data = category_dict
        else:
            current_app.logger.error(f"The given category has not a vlid name ('{category_data}')!")
            flash("The Categories name in not valid! Please choose another one.", "error")
            return None
    except json.decoder.JSONDecodeError:
        current_app.logger.debug(f"JSONDecodeError: category '{category_data}' is not a flexdatalist item.")

    category = Category(name=category_data)
    if category.exists():
        current_app.logger.debug("category with name '{}' exists.")
        category = Category.query.filter_by(name=category_data).first_or_404()
        current_app.logger.debug(f"Using category with id '{category.id}'.")
    else:
        category.save_to_db()
        current_app.logger.info(f"Added new category {category} to database.")
    return category


def get_list(list_data):
    def check_item_dict(item_dict):
        if isinstance(item_dict, dict) and "id" in item_dict.keys() and "name" in item_dict.keys():
            return True
        return False

    def get_list_items_from_dict(list_dict):
        items = []
        for item in list_dict:
            if check_item_dict(item):
                item_obj = Item.query.filter_by(id=item['id']).first()
                if item_obj:
                    items.append(item_obj)
                else:
                    current_app.logger.warning(f"Item '{item['name']}' is not a valid item in the database! Skipping.")
            else:
                current_app.logger.warning(f"Item '{item}' is not valid! Skipping.")
        return items

    if isinstance(list_data, list) and all([check_item_dict(item) for item in list_data]):
        return get_list_items_from_dict(list_data)
    elif not isinstance(list_data, str):
        current_app.logger.error("List data is neither string nor dictionary. Can't parse it.")
        return []

    try:
        list_dict = json.loads(list_data)
    except json.decoder.JSONDecodeError:
        current_app.logger.error("List data is not json decodable. Aborting.")
        return []

    if isinstance(list_dict, list) and all([check_item_dict(item) for item in list_dict]):
        return get_list_items_from_dict(list_dict)
    else:
        current_app.logger.warning("Could not read items list.")
        return []

@shopping_add_bp.route('/shopping/add/new/item', methods=['GET', 'POST'])
def shopping_add_new_item():
    result = {'status': 'success', 'text': ""}
    form = AddItem()

    if request.method == 'POST':
        formdata = {entry['name']: entry['value'] for entry in request.get_json()}
        formdata['category'] = formdata['flexdatalist-category']
        form = AddItem.from_json(formdata)
        if form.validate():
            category = get_category_for_new_item(form.category.data)

            new_item = Item(
                name=form.name.data,
                price=form.price.data,
                volume=form.volume.data,
                price_per_volume=form.price_per_volume.data,
                sale=form.sale.data,
                note=form.note.data,
                category=category,
            )
            if new_item.exists():
                result['status'] = 'error'
                result['text'] = "Item already exists."
            else:
                current_app.logger.info(f"Save new item '{new_item.name}' to db.")
                new_item.save_to_db()
                result['text'] = f"Item {new_item.name} added successfully to database."
                result.update({'item': {"id": new_item.id, "name": new_item.name}})

            return jsonify(result)
        else:
            result['status'] = 'error'
            result['text'] = 'form validation failed'
            result.update({'fields': form.errors})

            return jsonify(result)
    return render_template("item_form.html", form=form)


def get_category_for_new_item(form_category):
    category = None
    if form_category:
        category = Category(name=form_category)

        if category.exists():
            current_app.logger.debug(f"Category with name '{form_category}' already exists.")
            category = Category.query.filter_by(name=form_category).first_or_404()
            current_app.logger.debug(f"Using category f{category}.")
        else:
            current_app.logger.debug(f"Add new category '{form_category}' to db.")
            category.save_to_db()

        return category
    return None


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
