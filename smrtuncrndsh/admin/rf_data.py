import inspect

from flask import abort, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user
from sqlalchemy.orm.attributes import InstrumentedAttribute

from . import admin_bp
from .forms import RfDataForm
from ..models.RfData import RfData


@admin_bp.route('/rf-data/', methods=['GET', 'POST'])
@login_required
def rf_data():
    if not current_user.is_admin:
        abort(403)

    page = request.args.get('page', 1, type=int)
    items = RfData.query.order_by(RfData.date.desc()).paginate(
        page, 50, False
    )

    return render_template(
        'rf_data.html',
        title='Admin Panel - Rf Data',
        template='admin-page',
        items=items,
    )


@admin_bp.route('/rf-data/edit/<int:id>', methods=['POST', 'GET'])
@login_required
def edit_rf_data(id):
    if not current_user.is_admin:
        abort(403)

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
@login_required
def delete_rf_data(id):
    if not current_user.is_admin:
        abort(403)

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
        print("order ", order_type, " ", order_order)
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
