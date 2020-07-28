import inspect

from flask import render_template, request, redirect, flash, url_for, \
    jsonify, make_response, Response
from sqlalchemy.orm.attributes import InstrumentedAttribute

from . import admin_bp
from .forms import RfDataForm
from ..models.RfData import RfData
from .misc import get_request_dict, get_datatables_order_query, get_datatables_search_query


@admin_bp.route('/rf-data/', methods=['GET', 'POST'])
def rf_data():
    return render_template(
        'rf_data.html',
        title='Admin Panel - Rf Data',
        template='admin-page',
    )


@admin_bp.route('/rf_data/query', methods=['POST'])
def query_rf_data():
    args = get_request_dict(request.form)

    query = get_datatables_search_query(RfData, args)
    query = get_datatables_order_query(RfData, args, query)

    i_d = [
        i.to_ajax() for i in query.limit(args['length']).offset(args['start']).all()
    ]

    return make_response(jsonify({
        'draw': args['draw'],
        'recordsTotal': RfData.query.count(),
        'recordsFiltered': query.count(),
        'data': i_d,
    }), 200)


@admin_bp.route("/rf_data_js")
def rf_data_js():
    return Response(render_template("/js/rf_data.js"), mimetype="text/javascript")


@admin_bp.route('/rf-data/edit/<int:id>', methods=['POST', 'GET'])
def edit_rf_data(id):
    rf = RfData.query.filter_by(id=id).first_or_404()
    form = RfDataForm(obj=rf)

    if form.validate_on_submit():
        test_dupl = RfData.query.filter_by(
            date=form.date.data,
            decimal=form.decimal.data,
            bits=form.bits.data,
            binary=form.binary.data,
            pulse_length=form.pulse_length.data,
            protocol=form.protocol.data,
        ).first()
        if test_dupl:
            flash("An entry with these attributes already exists.", 'error')
            return redirect(request.url)

        change_rf_attr(
            form.date.data,
            form.decimal.data,
            form.bits.data,
            form.binary.data,
            form.pulse_length.data,
            form.protocol.data,
            rf
        )
        rf.db_commit()
        redirect(url_for('admin_bp.rf_data'))
    return render_template(
        'rf_data.html',
        title='Admin Panel - Rf Data',
        template='admin-page',
        form=form,
    )


@admin_bp.route('/rf-data/delete/<int:id>', methods=['GET', 'POST'])
def delete_rf_data(id):
    rf = RfData.query.filter_by(id=id).scalar()
    if rf:
        rf.delete_from_db()
        flash("Successfully deleted entry from Database.", "success")
    else:
        flash("Entry does not exist. Nothing was delted.")
    return redirect(url_for('admin_bp.rf_data'))


def get_order(order_type, order_order):
    obj_attrs = dict(inspect.getmembers(RfData, lambda a: type(a) == InstrumentedAttribute))

    query = RfData.date.desc()
    if order_type in obj_attrs.keys() and order_order in ['desc', 'asc']:
        if order_order == 'asc':
            query = obj_attrs[order_type].asc()
        else:
            query = obj_attrs[order_type].desc()
    return query


def change_rf_attr(date, decimal, bits, binary, pulse_length, protocol, rf):
    if rf.decimal != decimal:
        rf.decimal = decimal
        flash(f"Successfully changed decimal to {decimal}.", 'success')
    if rf.bits != bits:
        rf.bits = bits
        flash(f"Successfully changed bits to {bits}.", 'success')
    if rf.binary != binary:
        rf.binary = binary
        flash(f"Successfully changed binary to {binary}.", 'success')
    if rf.pulse_length != pulse_length:
        rf.pulse_length = pulse_length
        flash(f"Successfully changed pulse_length to {pulse_length}.", 'success')
    if rf.protocol != protocol:
        rf.protocol = protocol
        flash(f"Successfully changed protocol to {protocol}.", 'success')
    return rf
