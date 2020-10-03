from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField
from wtforms import DecimalField, TextField, FieldList, FormField, BooleanField
from wtforms.validators import DataRequired


class AddItem(FlaskForm):
    name = TextField("Name", validators=[DataRequired()])
    price = DecimalField("Price", validators=[DataRequired()])
    volume = TextField("Volume")
    price_per_volume = TextField("Price Per Volume")
    sale = BooleanField("Sale")
    note = TextField("Note")
    category = TextField("Category")


class ShopForm(FlaskForm):
    name = TextField("Shop", validators=[DataRequired()])
    category = TextField("Category")


class AddList(FlaskForm):
    date = DateField("Date", validators=[DataRequired()])
    price = DecimalField("Price", validators=[DataRequired()])
    shop = FormField(ShopForm)
    category = TextField("Category")

    items = TextField("Items")
    new_items = FieldList(
        FormField(AddItem, label=None),
        min_entries=0,
    )
