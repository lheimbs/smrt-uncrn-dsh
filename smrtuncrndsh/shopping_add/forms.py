from flask import current_app

from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField
from wtforms import StringField, FloatField, TextField
from wtforms.validators import DataRequired
from wtforms.widgets import TextInput, HTMLString

from ..models import db
from ..models.Shopping import Category, Shop, Item


class DatalistInput(TextInput):
    """ Custom widget to create an input with a datalist attribute """
    def __init__(self, datalist=""):
        super(DatalistInput, self).__init__()
        self.datalist = datalist

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('name', field.name)

        # field.default - default value which you set in route as form.field.default = ... (at the begin is None)
        # field._value() - value which you get from the form on submit and can use.

        if field.default is None:
            value = ""
        else:
            value = field.default

        html = [
            u'<input list="{}_list" id="{}", name="{}" value="{}"/>'.format(
                field.id, field.id, field.name, value
            ),
            u'<datalist id="{}_list">'.format(field.id)
        ]

        for item in field.datalist:
            html.append(u'<option value="{}">'.format(item))
        html.append(u'</datalist>')

        return HTMLString(u''.join(html))


class DatalistField(StringField):
    """ Custom field type for datalist input """
    widget = DatalistInput()

    def __init__(self, label=None, datalist="", validators=None, **kwargs):
        super(DatalistField, self).__init__(label, validators, **kwargs)
        self.datalist = datalist

    def _value(self):
        if self.data:
            return u''.join(self.data)
        else:
            return u''


class AddList(FlaskForm):
    date = DateField("Date", validators=[DataRequired()])
    price = FloatField("Price", validators=[DataRequired()])
    shop = TextField("Shop", validators=[DataRequired()])
    category = TextField("Category")

    items = TextField("Items", validators=[DataRequired()])
