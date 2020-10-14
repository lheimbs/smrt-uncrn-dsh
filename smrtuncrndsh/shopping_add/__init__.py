from flask import render_template, Blueprint, jsonify, abort, request, \
    Response, current_app, flash  # , make_response, redirect
from flask_login import login_required, current_user
from wtforms import TextField
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from .misc import get_ajax_search_objects, get_category, get_shop, get_list, get_category_for_new_item
from .forms import AddList, AddItem
from ..models.Shopping import Shop, Category, Item, Liste
from ..models.Users import User

# Blueprint Configuration
shopping_add_bp = Blueprint(
    'shopping_add_bp', __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/shopping/',
)


@shopping_add_bp.route('/add', methods=['GET', 'POST'])
def add():
    if current_user.is_admin:
        current_app.logger.info("User is admin! Letting admin decide who is the owner of the added Recepit.")

        class AddListAsAdmin(AddList):
            pass

        AddListAsAdmin.user = QuerySelectField(
            query_factory=lambda: User.query,
            get_label='username',
            allow_blank=False,
            blank_text="Select a user",
            description="User",
        )
        # TextField("User", validators=[DataRequired()])
        form = AddListAsAdmin()
        # form.user = current_user
    else:
        form = AddList()

    if form.validate_on_submit():
        shop = get_shop(form.shop.data)
        category = get_category(form.category.data)

        new_list = Liste(form.date.data, float(form.price.data), shop, category)
        item_list = get_list(form.items.data)

        if not item_list:
            flash(
                "An error occured reading the supplied shopping items! Please change your input or try again alter.",
                "error"
            )
        else:
            new_list.items = item_list

            if hasattr(form, "user") and form.user.data and current_user.is_admin:
                new_list.user = form.user.data
            else:
                new_list.user = current_user

            new_list.save_to_db()
            flash("Successfully saved the entered receipt!", "success")

    return render_template(
        'add.html',
        title='Add Shopping List',
        template='shopping-add',
        form=form,
    )


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


@shopping_add_bp.route('/shopping/query/shops', methods=['GET', 'POST'])
def query_shops():
    return get_ajax_search_objects(Shop, request.args)


@shopping_add_bp.route('/shopping/query/categories', methods=['GET', 'POST'])
def query_categories():
    return get_ajax_search_objects(Category, request.args)


@shopping_add_bp.route('/shopping/query/items', methods=['GET', 'POST'])
def query_items():
    return get_ajax_search_objects(Item, request.args)


@shopping_add_bp.route("/adding_js")
def adding_js():
    return Response(render_template("/js/adding.js"), mimetype="application/javascript;")


@shopping_add_bp.before_request
@login_required
def before_request():
    if not current_user.is_activated:
        abort(403)
