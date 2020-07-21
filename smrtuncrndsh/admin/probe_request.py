import inspect

from flask import abort, render_template, request, redirect, flash, url_for, \
    jsonify, make_response
from flask_login import login_required, current_user
from sqlalchemy.orm.attributes import InstrumentedAttribute

from . import admin_bp
from .forms import ProbeRequestForm
from ..models.ProbeRequest import ProbeRequest
from .misc import get_request_dict, get_datatables_order_query, get_datatables_search_query


@admin_bp.route('/probe-request/', methods=['GET', 'POST'])
@login_required
def probe_request():
    if not current_user.is_admin:
        abort(403)

    # page = request.args.get('page', 1, type=int)
    # items = ProbeRequest.query.order_by(ProbeRequest.date.desc()).paginate(
    #     page, 50, False
    # )

    return render_template(
        'probe_request.html',
        title='Admin Panel - Probe Requests',
        template='admin-page',
        # items=items,
    )


@admin_bp.route('/probe_request/query', methods=['POST'])
@login_required
def query_probe_request():
    if not current_user.is_admin:
        abort(403)
    args = get_request_dict(request.form)

    query = get_datatables_search_query(ProbeRequest, args)
    query = get_datatables_order_query(ProbeRequest, args, query)

    i_d = [
        i.to_ajax() for i in query.limit(args['length']).offset(args['start']).all()
    ]

    return make_response(jsonify({
        'draw': args['draw'],
        'recordsTotal': ProbeRequest.query.count(),
        'recordsFiltered': query.count(),
        'data': i_d,
    }), 200)


@admin_bp.route("/probe_request_js")
@login_required
def probe_request_js():
    return render_template("/js/probe_request.js")


@admin_bp.route('/probe-request/edit/<int:id>', methods=['POST', 'GET'])
@login_required
def edit_probe_request(id):
    if not current_user.is_admin:
        abort(403)

    probe_request = ProbeRequest.query.filter_by(id=id).first_or_404()
    form = ProbeRequestForm(obj=probe_request)

    if form.validate_on_submit():
        test_dupl = ProbeRequest.query.filter_by(
            date=form.date.data,
            macaddress=form.macaddress.data,
            make=form.make.data,
            ssid=form.ssid.data,
            rssi=form.rssi.data,
        ).first()
        if test_dupl:
            flash("An entry with these attributes already exists.", 'error')
            return redirect(request.url)

        change_probe_request_attr(
            form.date.data,
            form.macaddress.data,
            form.make.data,
            form.ssid.data,
            form.rssi.data,
            probe_request
        )
        probe_request.db_commit()
        redirect(url_for('admin_bp.probe_request'))
    return render_template(
        'probe_request.html',
        title='Admin Panel - Probe Requests',
        template='admin-page',
        form=form,
    )


@admin_bp.route('/probe-request/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_probe_request(id):
    if not current_user.is_admin:
        abort(403)

    probe_request = ProbeRequest.query.filter_by(id=id).scalar()
    if probe_request:
        probe_request.delete_from_db()
        flash("Successfully deleted entry from Database.", "success")
    else:
        flash("Entry does not exist. Nothing was delted.")
    return redirect(url_for('admin_bp.probe_request'))


def get_order(order_type, order_order):
    obj_attrs = dict(inspect.getmembers(ProbeRequest, lambda a: type(a) == InstrumentedAttribute))

    query = ProbeRequest.date.desc()
    if order_type in obj_attrs.keys() and order_order in ['desc', 'asc']:
        print("order ", order_type, " ", order_order)
        if order_order == 'asc':
            query = obj_attrs[order_type].asc()
        else:
            query = obj_attrs[order_type].desc()
    return query


def change_probe_request_attr(date, macaddress, make, ssid, rssi, probe_request):
    if probe_request.date != date:
        probe_request.date = date
        flash(f"Successfully changed date to {date}.", 'success')
    if probe_request.macaddress != macaddress:
        probe_request.macaddress = macaddress
        flash(f"Successfully changed macaddress to {macaddress}.", 'success')
    if probe_request.make != make:
        probe_request.make = make
        flash(f"Successfully changed make to {make}.", 'success')
    if probe_request.ssid != ssid:
        probe_request.ssid = ssid
        flash(f"Successfully changed ssid to {ssid}.", 'success')
    if probe_request.rssi != rssi:
        probe_request.rssi = rssi
        flash(f"Successfully changed rssi to {rssi}.", 'success')
    return probe_request
