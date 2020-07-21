import inspect

from flask import abort, render_template, request, redirect, flash, url_for, jsonify, make_response
from flask_login import login_required, current_user
from sqlalchemy.orm.attributes import InstrumentedAttribute

from . import admin_bp
from .forms import RoomDataForm
from ..models.RoomData import RoomData
from .misc import get_request_dict, get_datatables_order_query, get_datatables_search_query


@admin_bp.route('/room-data/', methods=['GET', 'POST'])
@login_required
def room_data():
    if not current_user.is_admin:
        abort(403)

    # page = request.args.get('page', 1, type=int)
    # items = RoomData.query.order_by(RoomData.date.desc()).paginate(
    #     page, 50, False
    # )

    return render_template(
        'room_data.html',
        title='Admin Panel - Room Data',
        template='admin-page',
        # items=items,
    )


@admin_bp.route('/room-data/query', methods=['POST'])
@login_required
def query_room_data():
    if not current_user.is_admin:
        abort(403)
    args = get_request_dict(request.form)

    query = get_datatables_search_query(RoomData, args)
    query = get_datatables_order_query(RoomData, args, query)

    # print('length', args['length'], 'start', args['start'])
    i_d = [
        i.to_ajax() for i in query.limit(args['length']).offset(args['start']).all()
    ]

    return make_response(jsonify({
        'draw': args['draw'],
        'recordsTotal': RoomData.query.count(),
        'recordsFiltered': query.count(),
        'data': i_d,
    }), 200)
    # return make_response(jsonify({"message": "OK"}), 200)


@admin_bp.route('/room-data/edit/<int:id>', methods=['POST', 'GET'])
@login_required
def edit_room_data(id):
    if not current_user.is_admin:
        abort(403)

    rd = RoomData.query.filter_by(id=id).first_or_404()
    form = RoomDataForm(obj=rd)

    if form.validate_on_submit():
        test_dupl = RoomData.query.filter_by(
            date=form.date.data,
            temperature=form.temperature.data,
            humidity=form.humidity.data,
            pressure=form.pressure.data,
            brightness=form.brightness.data,
            altitude=form.altitude.data,
        ).first()
        if test_dupl:
            flash("An entry with these attributes already exists.", 'error')
            return redirect(request.url)

        change_rd_attr(
            form.date.data,
            form.temperature.data,
            form.humidity.data,
            form.pressure.data,
            form.brightness.data,
            form.altitude.data,
            rd
        )
        rd.db_commit()
        redirect(url_for('admin_bp.room_data'))
    return render_template(
        'room_data.html',
        title='Admin Panel - Room Data',
        template='admin-page',
        form=form,
    )


@admin_bp.route('/room-data/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_room_data(id):
    if not current_user.is_admin:
        abort(403)

    rd = RoomData.query.filter_by(id=id).scalar()
    if rd:
        rd.delete_from_db()
        flash("Successfully deleted entry from Database.", "success")
    else:
        flash("Entry does not exist. Nothing was delted.")
    return redirect(url_for('admin_bp.room_data'))


def get_order(order_type, order_order):
    obj_attrs = dict(inspect.getmembers(RoomData, lambda a: type(a) == InstrumentedAttribute))

    query = RoomData.date.desc()
    if order_type in obj_attrs.keys() and order_order in ['desc', 'asc']:
        print("order ", order_type, " ", order_order)
        if order_order == 'asc':
            query = obj_attrs[order_type].asc()
        else:
            query = obj_attrs[order_type].desc()
    return query


def change_rd_attr(date, temperature, humidity, pressure, brightness, altitude, rd):
    if rd.temperature != temperature:
        rd.temperature = temperature
        flash(f"Successfully changed temperature to {temperature}.", 'success')
    if rd.humidity != humidity:
        rd.humidity = humidity
        flash(f"Successfully changed humidity to {humidity}.", 'success')
    if rd.pressure != pressure:
        rd.pressure = pressure
        flash(f"Successfully changed pressure to {pressure}.", 'success')
    if rd.brightness != brightness:
        rd.brightness = brightness
        flash(f"Successfully changed brightness to {brightness}.", 'success')
    if rd.altitude != altitude:
        rd.altitude = altitude
        flash(f"Successfully changed altitude to {altitude}.", 'success')
    return rd


@admin_bp.route("/room_data_js")
@login_required
def room_data_js():
    return render_template("/js/room_data.js")
