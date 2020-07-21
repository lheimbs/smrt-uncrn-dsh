import inspect

from flask import abort, render_template, request, redirect, flash, url_for, \
    jsonify, make_response
from flask_login import login_required, current_user
from sqlalchemy.orm.attributes import InstrumentedAttribute

from . import admin_bp
from .forms import TabletBatteryForm
from ..models.Tablet import TabletBattery
from .misc import get_request_dict, get_datatables_order_query, get_datatables_search_query


@admin_bp.route('/tablet-battery/', methods=['GET', 'POST'])
@login_required
def tablet_battery():
    if not current_user.is_admin:
        abort(403)

    # page = request.args.get('page', 1, type=int)
    # items = TabletBattery.query.order_by(TabletBattery.date.desc()).paginate(
    #     page, 50, False
    # )

    return render_template(
        'tablet_battery.html',
        title='Admin Panel - Tablet Battery',
        template='admin-page',
        # items=items,
    )


@admin_bp.route('/tablet_battery/query', methods=['POST'])
@login_required
def query_tablet_battery():
    if not current_user.is_admin:
        abort(403)
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
@login_required
def tablet_battery_js():
    return render_template("/js/tablet_battery.js")


@admin_bp.route('/tablet-battery/edit/<int:id>', methods=['POST', 'GET'])
@login_required
def edit_tablet_battery(id):
    if not current_user.is_admin:
        abort(403)

    tablet_battery = TabletBattery.query.filter_by(id=id).first_or_404()
    form = TabletBatteryForm(obj=tablet_battery)

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
            tablet_battery
        )
        tablet_battery.db_commit()
        redirect(url_for('admin_bp.tablet_battery'))
    return render_template(
        'tablet_battery.html',
        title='Admin Panel - Probe Requests',
        template='admin-page',
        form=form,
    )


@admin_bp.route('/tablet-battery/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_tablet_battery(id):
    if not current_user.is_admin:
        abort(403)

    tablet_battery = TabletBattery.query.filter_by(id=id).scalar()
    if tablet_battery:
        tablet_battery.delete_from_db()
        flash("Successfully deleted entry from Database.", "success")
    else:
        flash("Entry does not exist. Nothing was delted.")
    return redirect(url_for('admin_bp.tablet_battery'))


def get_order(order_type, order_order):
    obj_attrs = dict(inspect.getmembers(TabletBattery, lambda a: type(a) == InstrumentedAttribute))

    query = TabletBattery.date.desc()
    if order_type in obj_attrs.keys() and order_order in ['desc', 'asc']:
        print("order ", order_type, " ", order_order)
        if order_order == 'asc':
            query = obj_attrs[order_type].asc()
        else:
            query = obj_attrs[order_type].desc()
    return query


def change_tablet_battery_attr(date, level, make, ssid, rssi, tablet_battery):
    if tablet_battery.date != date:
        tablet_battery.date = date
        flash(f"Successfully changed date to {date}.", 'success')
    if tablet_battery.level != level:
        tablet_battery.level = level
        flash(f"Successfully changed level to {level}.", 'success')
    return tablet_battery
