import inspect

from flask import render_template, request, redirect, flash, \
    url_for, jsonify, make_response, Response
from sqlalchemy.orm.attributes import InstrumentedAttribute

from . import admin_bp
from .forms import RoomDataForm
from ..models.RoomData import RoomData
from .misc import get_request_dict, get_datatables_order_query, get_datatables_search_query


@admin_bp.route('/room-data/', methods=['GET', 'POST'])
def room_data():
    return render_template(
        'room_data.html',
        title='Admin Panel - Room Data',
        template='admin-page',
    )


@admin_bp.route('/room-data/query', methods=['POST'])
def query_room_data():
    args = get_request_dict(request.form)

    query = get_datatables_search_query(RoomData, args)
    query = get_datatables_order_query(RoomData, args, query)

    i_d = [
        i.to_ajax() for i in query.limit(args['length']).offset(args['start']).all()
    ]

    return make_response(jsonify({
        'draw': args['draw'],
        'recordsTotal': RoomData.query.count(),
        'recordsFiltered': query.count(),
        'data': i_d,
    }), 200)


@admin_bp.route('/room-data/edit/<int:id>', methods=['POST', 'GET'])
def edit_room_data(id):
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
def delete_room_data(id):
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
def room_data_js():
    return Response(render_template("/js/room_data.js"), mimetype="text/javascript")
