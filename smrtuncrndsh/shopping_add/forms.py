from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField, DecimalField, IntegerField
from wtforms import TextField, FieldList, FormField, BooleanField, RadioField
from wtforms.validators import DataRequired, Optional
from flask_wtf.file import FileField, FileRequired


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
    # submit = SubmitField('Submit')


class ReceiptItem(FlaskForm):
    item = TextField("Name")
    price_per_piece = DecimalField("Price per piece")
    total_price = DecimalField("Total Price")
    amount = IntegerField("Amount")
    volume = TextField("Volume")
    ppv = TextField("Price per Volume")
    sale = BooleanField("Sale")


class ShopSelectForm(FlaskForm):
    # select = BooleanField("Select")
    shop = TextField("Shop", validators=[DataRequired()])
    category = TextField("Category")


class ReceiptForm(FlaskForm):
    date = DateField("Date", validators=[DataRequired()])
    sums = RadioField("Prices", coerce=float, validate_choice=False)
    price = DecimalField("Price", validators=[Optional()])
    category = TextField("Category")
    shops = FieldList(
        FormField(ShopSelectForm),
        min_entries=1,
    )
    items = FieldList(
        FormField(ReceiptItem),
        min_entries=1,
    )
