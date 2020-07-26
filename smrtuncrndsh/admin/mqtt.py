import inspect

from flask import render_template, request, redirect, flash, url_for, \
    jsonify, make_response, Response, abort
from sqlalchemy.orm.attributes import InstrumentedAttribute

from . import admin_bp
from .forms import MqttForm
from ..models.Mqtt import Mqtt
from .misc import get_request_dict, get_datatables_order_query, get_datatables_search_query


@admin_bp.route('/mqtt/', methods=['GET', 'POST'])
def mqtt():
    return render_template(
        'mqtt.html',
        title='Admin Panel - Mqtt',
        template='admin-page',
    )


@admin_bp.route('/mqtt/query', methods=['POST'])
def query_mqtt():
    args = get_request_dict(request.form)

    query = get_datatables_search_query(Mqtt, args)
    query = get_datatables_order_query(Mqtt, args, query)

    i_d = [
        i.to_ajax() for i in query.limit(args['length']).offset(args['start']).all()
    ]

    if not i_d:
        abort(404, description="Resource not found")

    return make_response(jsonify({
        'draw': args['draw'],
        'recordsTotal': Mqtt.query.count(),
        'recordsFiltered': query.count(),
        'data': i_d,
    }), 200)


@admin_bp.route("/mqtt_js")
def mqtt_js():
    return Response(render_template("/js/mqtt.js"), mimetype="text/javascript")


@admin_bp.route('/mqtt/edit/<int:id>', methods=['POST', 'GET'])
def edit_mqtt(id):
    mqtt = Mqtt.query.filter_by(id=id).first_or_404()
    form = MqttForm(obj=mqtt)

    if form.validate_on_submit():
        test_dupl = Mqtt.query.filter_by(
            date=form.date.data,
            topic=form.topic.data,
            payload=form.payload.data,
            qos=form.qos.data,
            retain=form.retain.data,
        ).first()
        if test_dupl:
            flash("An entry with these attributes already exists.", 'error')
            return redirect(request.url)

        change_mqtt_attr(
            form.date.data,
            form.topic.data,
            form.payload.data,
            form.qos.data,
            form.retain.data,
            mqtt
        )
        mqtt.db_commit()
        redirect(url_for('admin_bp.mqtt'))
    return render_template(
        'mqtt.html',
        title='Admin Panel - Mqtt',
        template='admin-page',
        form=form,
    )


@admin_bp.route('/mqtt/delete/<int:id>', methods=['GET', 'POST'])
def delete_mqtt(id):
    mqtt = Mqtt.query.filter_by(id=id).scalar()
    if mqtt:
        mqtt.delete_from_db()
        flash("Successfully deleted entry from Database.", "success")
    else:
        flash("Entry does not exist. Nothing was delted.")
    return redirect(url_for('admin_bp.mqtt'))


def get_order(order_type, order_order):
    obj_attrs = dict(inspect.getmembers(Mqtt, lambda a: type(a) == InstrumentedAttribute))

    query = Mqtt.date.desc()
    if order_type in obj_attrs.keys() and order_order in ['desc', 'asc']:
        print("order ", order_type, " ", order_order)
        if order_order == 'asc':
            query = obj_attrs[order_type].asc()
        else:
            query = obj_attrs[order_type].desc()
    return query


def change_mqtt_attr(date, topic, payload, qos, retain, mqtt):
    if mqtt.topic != topic:
        mqtt.topic = topic
        flash(f"Successfully changed topic to {topic}.", 'success')
    if mqtt.payload != payload:
        mqtt.payload = payload
        flash(f"Successfully changed payload to {payload}.", 'success')
    if mqtt.qos != qos:
        mqtt.qos = qos
        flash(f"Successfully changed qos to {qos}.", 'success')
    if mqtt.retain != retain:
        mqtt.retain = retain
        flash(f"Successfully changed retain to {retain}.", 'success')
    return mqtt
