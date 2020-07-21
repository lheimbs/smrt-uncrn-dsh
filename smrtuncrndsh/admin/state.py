import inspect

from flask import abort, render_template, request, redirect, flash, url_for, \
    jsonify, make_response
from flask_login import login_required, current_user
from sqlalchemy.orm.attributes import InstrumentedAttribute

from . import admin_bp
from .forms import StateForm
from ..models.State import State
from .misc import get_request_dict, get_datatables_order_query, get_datatables_search_query


@admin_bp.route('/state/', methods=['GET', 'POST'])
@login_required
def state():
    if not current_user.is_admin:
        abort(403)

    # page = request.args.get('page', 1, type=int)
    # items = State.query.order_by(State.date.desc()).paginate(
    #     page, 50, False
    # )

    return render_template(
        'state.html',
        title='Admin Panel - States',
        template='admin-page',
        # items=items,
    )


@admin_bp.route('/state/query', methods=['POST'])
@login_required
def query_state():
    if not current_user.is_admin:
        abort(403)
    args = get_request_dict(request.form)

    query = get_datatables_search_query(State, args)
    query = get_datatables_order_query(State, args, query)

    i_d = [
        i.to_ajax() for i in query.limit(args['length']).offset(args['start']).all()
    ]

    return make_response(jsonify({
        'draw': args['draw'],
        'recordsTotal': State.query.count(),
        'recordsFiltered': query.count(),
        'data': i_d,
    }), 200)


@admin_bp.route("/state_js")
@login_required
def state_js():
    return render_template("/js/state.js")


@admin_bp.route('/state/edit/<int:id>', methods=['POST', 'GET'])
@login_required
def edit_state(id):
    if not current_user.is_admin:
        abort(403)

    state = State.query.filter_by(id=id).first_or_404()
    form = StateForm(obj=state)

    if form.validate_on_submit():
        test_dupl = State.query.filter_by(
            date=form.date.data,
            device=form.device.data,
            state=form.state.data,
        ).first()
        if test_dupl:
            flash("An entry with these attributes already exists.", 'error')
            return redirect(request.url)

        change_state_attr(
            form.date.data,
            form.device.data,
            form.state.data,
            state
        )
        state.db_commit()
        redirect(url_for('admin_bp.state'))
    return render_template(
        'state.html',
        title='Admin Panel - States',
        template='admin-page',
        form=form,
    )


@admin_bp.route('/state/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_state(id):
    if not current_user.is_admin:
        abort(403)

    state = State.query.filter_by(id=id).scalar()
    if state:
        state.delete_from_db()
        flash("Successfully deleted entry from Database.", "success")
    else:
        flash("Entry does not exist. Nothing was delted.")
    return redirect(url_for('admin_bp.state'))


def get_order(order_type, order_order):
    obj_attrs = dict(inspect.getmembers(State, lambda a: type(a) == InstrumentedAttribute))

    query = State.date.desc()
    if order_type in obj_attrs.keys() and order_order in ['desc', 'asc']:
        print("order ", order_type, " ", order_order)
        if order_order == 'asc':
            query = obj_attrs[order_type].asc()
        else:
            query = obj_attrs[order_type].desc()
    return query


def change_state_attr(date, device, state_, state):
    if state.device != device:
        state.device = device
        flash(f"Successfully changed device to {device}.", 'success')
    if state.state != state_:
        state.state = state_
        flash(f"Successfully changed state to {state_}.", 'success')
    return state
