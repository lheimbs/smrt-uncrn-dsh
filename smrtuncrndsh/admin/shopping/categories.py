from flask import abort, render_template, request, redirect, flash, \
    url_for, Markup, render_template_string, jsonify, make_response
from flask_login import login_required, current_user

# from psycopg2.errors import ForeignKeyViolation
# from sqlalchemy.exc import IntegrityError

from .. import admin_bp
from ..forms import CategoryForm
from ...models import db
from ...models.Shopping import Category
from ..misc import get_request_dict, get_datatables_order_query, get_datatables_search_query


@admin_bp.route('/shopping/category/')
@login_required
def shopping_category():
    if not current_user.is_admin:
        abort(403)

    # categories = Category.query.order_by(Category.name).all()
    return render_template(
        'shopping/category.html',
        title='Admin Panel - Shopping Categories',
        template='admin-page',
        # categories=categories,
    )


@admin_bp.route('/shopping/category/query', methods=['POST'])
@login_required
def query_shopping_categories():
    if not current_user.is_admin:
        abort(403)
    args = get_request_dict(request.form)

    query = get_datatables_search_query(Category, args)
    query = get_datatables_order_query(Category, args, query)

    # print('length', args['length'], 'start', args['start'])
    i_d = [
        i.to_ajax() for i in query.limit(args['length']).offset(args['start']).all()
    ]

    return make_response(jsonify({
        'draw': args['draw'],
        'recordsTotal': Category.query.count(),
        'recordsFiltered': query.count(),
        'data': i_d,
    }), 200)
    # return make_response(jsonify({"message": "OK"}), 200)


@admin_bp.route('/shopping/category/new/', methods=['POST', 'GET'])
@login_required
def new_shopping_category():
    if not current_user.is_admin:
        abort(403)

    form = CategoryForm()

    if form.validate_on_submit():
        categoryname = form.name.data
        if Category.query.filter_by(name=categoryname).count() > 0:
            flash("A category with this name already exists. Try another name.", 'error')
            return redirect(request.url)
        else:
            new_category = Category(name=categoryname)
            new_category.save_to_db()
            flash(f"Successfully added Category {categoryname}.", 'success')
            return redirect(url_for("admin_bp.shopping_category"))
    return render_template(
        'shopping/new_category.html',
        title='Admin Panel - Shopping Categories - New',
        template='admin-page',
        form=form,
    )


@admin_bp.route('/shopping/category/edit/<int:id>', methods=['POST', 'GET'])
@login_required
def edit_shopping_category(id):
    if not current_user.is_admin:
        abort(403)

    category = Category.query.filter_by(id=id).first_or_404()
    form = CategoryForm(obj=category)

    if form.validate_on_submit():
        categoryname = form.name.data
        if category.name != categoryname:
            category.name = categoryname
            flash(f"Successfully changed Category to {categoryname}.", 'success')
        category.db_commit()
        return redirect(url_for("admin_bp.shopping_category"))
    return render_template(
        'shopping/edit_category.html',
        title='Admin Panel - Shopping Categories - New',
        template='admin-page',
        form=form,
        category=category
    )


@admin_bp.route('/shopping/category/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_shopping_category(id):
    if not current_user.is_admin:
        abort(403)

    category = Category.query.filter_by(id=id).first_or_404()
    if category and (category.lists or category.shops or category.items):
        links = []
        for liste in category.lists:
            links.append(render_template_string(
                f"<a href=\"{{{{ url_for('admin_bp.edit_shopping_list', id={liste.id}) }}}}\">{liste.id}</a>"
            ))
        for shop in category.shops:
            links.append(render_template_string(
                f"<a href=\"{{{{ url_for('admin_bp.edit_shopping_shop', id={shop.id}) }}}}\">{shop.id}</a>"
            ))
        for item in category.items:
            links.append(render_template_string(
                f"<a href=\"{{{{ url_for('admin_bp.edit_shopping_item', id={item.id}) }}}}\">{item.id}</a>"
            ))
        flash("Cannot delete Category because it exists in other Objects.", 'error')
        flash(Markup(f"Remove it from these to allow deletion: {', '.join(links)}."), 'info')
    elif category:
        try:
            category.delete_from_db()
            flash(f"Category with id {id} successfully deleted from database.", 'success')
        except Exception as exc:
            flash(str(exc), 'info')
            db.session.rollback()
    else:
        flash(f"Category with id {id} does not exist in database.", 'info')
    return redirect(url_for('admin_bp.shopping_category'))


@admin_bp.route("/category_js")
@login_required
def category_js():
    return render_template("/js/category.js")
