import inspect

from flask import render_template, request, redirect, flash, url_for, \
    jsonify, make_response, Response
from sqlalchemy.orm.attributes import InstrumentedAttribute

from . import admin_bp
from .forms import TabletBatteryForm
from ..models.Tablet import TabletBattery
from .misc import get_request_dict, get_datatables_order_query, get_datatables_search_query


@admin_bp.route('/tablet-battery/', methods=['GET', 'POST'])
def tablet_battery():
    return render_template(
        'tablet_battery.html',
        title='Admin Panel - Tablet Battery',
        template='admin-page',
    )


@admin_bp.route('/tablet_battery/query', methods=['POST'])
def query_tablet_battery():
    args = get_request_dict(request.form)

    query = get_datatables_search_query(TabletBattery, args)
    query = get_datatables_order_query(TabletBattery, args, query)

    i_d = [
        i.to_ajax() for i in query.limit(args['length']).offset(args['start']).all()
    ]

    return make_response(jsonify({
        'draw': args['draw'],
        'recordsTotal': TabletBattery.query.count(),
        'recordsFiltered': query.count(),
        'data': i_d,
    }), 200)


@admin_bp.route("/tablet_battery_js")
def tablet_battery_js():
    return Response(render_template("/js/tablet_battery.js"), mimetype="text/javascript")


@admin_bp.route('/tablet-battery/edit/<int:id>', methods=['POST', 'GET'])
def edit_tablet_battery(id):
    tablet_battery_obj = TabletBattery.query.filter_by(id=id).first_or_404()
    form = TabletBatteryForm(obj=tablet_battery_obj)

    if form.validate_on_submit():
        test_dupl = TabletBattery.query.filter_by(
            date=form.date.data,
            level=form.level.data,
        ).first()
        if test_dupl:
            flash("An entry with these attributes already exists.", 'error')
            return redirect(request.url)

        change_tablet_battery_attr(
            form.date.data,
            form.level.data,
            tablet_battery_obj
        )
        tablet_battery_obj.db_commit()
        redirect(url_for('admin_bp.tablet_battery'))
    return render_template(
        'tablet_battery.html',
        title='Admin Panel - Probe Requests',
        template='admin-page',
        form=form,
    )


@admin_bp.route('/tablet-battery/delete/<int:id>', methods=['GET', 'POST'])
def delete_tablet_battery(id):
    tablet_battery_obj = TabletBattery.query.filter_by(id=id).scalar()
    if tablet_battery_obj:
        tablet_battery_obj.delete_from_db()
        flash("Successfully deleted entry from Database.", "success")
    else:
        flash("Entry does not exist. Nothing was delted.")
    return redirect(url_for('admin_bp.tablet_battery'))


def get_order(order_type, order_order):
    obj_attrs = dict(inspect.getmembers(TabletBattery, lambda a: type(a) == InstrumentedAttribute))

    query = TabletBattery.date.desc()
    if order_type in obj_attrs.keys() and order_order in ['desc', 'asc']:
        if order_order == 'asc':
            query = obj_attrs[order_type].asc()
        else:
            query = obj_attrs[order_type].desc()
    return query


def change_tablet_battery_attr(date, level, make, ssid, rssi, tablet_battery_obj):
    if tablet_battery_obj.date != date:
        tablet_battery_obj.date = date
        flash(f"Successfully changed date to {date}.", 'success')
    if tablet_battery_obj.level != level:
        tablet_battery_obj.level = level
        flash(f"Successfully changed level to {level}.", 'success')
    return tablet_battery_obj
