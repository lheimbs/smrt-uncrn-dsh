import inspect

from flask import abort, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user
from sqlalchemy.orm.attributes import InstrumentedAttribute

from . import admin_bp
from .forms import MqttForm
from ..models.Mqtt import Mqtt


@admin_bp.route('/mqtt/', methods=['GET', 'POST'])
@login_required
def mqtt():
    if not current_user.is_admin:
        abort(403)

    page = request.args.get('page', 1, type=int)
    items = Mqtt.query.order_by(Mqtt.date.desc()).paginate(
        page, 50, False
    )

    return render_template(
        'mqtt.html',
        title='Admin Panel - Mqtt',
        template='admin-page',
        items=items,
    )


@admin_bp.route('/mqtt/edit/<int:id>', methods=['POST', 'GET'])
@login_required
def edit_mqtt(id):
    if not current_user.is_admin:
        abort(403)

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
@login_required
def delete_mqtt(id):
    if not current_user.is_admin:
        abort(403)

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
