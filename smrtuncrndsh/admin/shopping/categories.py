from flask import render_template, request, redirect, Response, flash, \
    url_for, Markup, render_template_string, jsonify, make_response

from .. import admin_bp
from ..forms import CategoryForm
from ...models import db
from ...models.Shopping import Category
from ..misc import get_request_dict, get_datatables_order_query, get_datatables_search_query


@admin_bp.route('/shopping/category/')
def shopping_category():
    return render_template(
        'shopping/category.html',
        title='Admin Panel - Shopping Categories',
        template='admin-page',
    )


@admin_bp.route('/shopping/category/query', methods=['POST'])
def query_shopping_categories():
    args = get_request_dict(request.form)

    query = get_datatables_search_query(Category, args)
    query = get_datatables_order_query(Category, args, query)

    i_d = [
        i.to_ajax() for i in query.limit(args['length']).offset(args['start']).all()
    ]

    return make_response(jsonify({
        'draw': args['draw'],
        'recordsTotal': Category.query.count(),
        'recordsFiltered': query.count(),
        'data': i_d,
    }), 200)


@admin_bp.route('/shopping/category/new/', methods=['POST', 'GET'])
def new_shopping_category():
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
def edit_shopping_category(id):
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
def delete_shopping_category(id):
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
def category_js():
    return Response(render_template("/js/category.js"), mimetype="text/javascript")
