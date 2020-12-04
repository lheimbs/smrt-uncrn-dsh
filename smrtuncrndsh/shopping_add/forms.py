from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField, DecimalField, IntegerField
from wtforms import TextField, FieldList, FormField, BooleanField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired


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


class PdfForm(FlaskForm):
    reciept = FileField(validators=[FileRequired()])
    shop = TextField("Shop", validators=[])


class ReceiptItem(FlaskForm):
    name = TextField("Name", validators=[DataRequired()])
    price_per_piece = DecimalField("Price per piece", validators=[DataRequired()])
    total_price = DecimalField("Total Price")
    amount = IntegerField("Amount", validators=[DataRequired()])
    volume = TextField("Volume")
    ppv = TextField("Price per Volume")


class ReceiptForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()])
    price = DecimalField("Price", validators=[DataRequired()])
    shops = FieldList(
        TextField("Shop"),
        min_entries=1,
    )
    category = TextField("Category")

    new_items = FieldList(
        FormField(ReceiptItem, label=None),
        min_entries=0,
    )
