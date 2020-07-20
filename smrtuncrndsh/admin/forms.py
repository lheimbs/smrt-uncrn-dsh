from flask import current_app

from flask_wtf import FlaskForm
from wtforms import BooleanField
from wtforms_alchemy import model_form_factory, ModelFormField
from wtforms.fields import HiddenField, StringField
# , StringField, Field, SelectField, SelectMultipleField, SearchField,
from wtforms.fields.html5 import DateField, DecimalField, DateTimeField
from wtforms.validators import Required, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField

from ..models import db
from ..models.Shopping import Item, Shop, Category
from ..models.RoomData import RoomData
from ..models.RfData import RfData
from ..models.Mqtt import Mqtt
from ..models.ProbeRequest import ProbeRequest
from ..models.Tablet import TabletBattery
from ..models.State import State

BaseModelForm = model_form_factory(FlaskForm)


class ActivateForm(FlaskForm):
    def __init__(self, username, *args, **kwargs):
        super(ActivateForm, self).__init__(*args, **kwargs)
        self.username = username

    activate = BooleanField()


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


class CategoryForm(ModelForm):
    class Meta:
        model = Category


class CategorySelectForm(FlaskForm):
    # class Meta:
    #     model = Category
    name = QuerySelectField(
        query_factory=lambda: Category.query,
        get_label='name',
        allow_blank=True,
        blank_text="Select a category",
        description="Category",
    )


class ShopForm(ModelForm):
    class Meta:
        model = Shop

    category = ModelFormField(CategorySelectForm)


class ItemForm(ModelForm):
    class Meta:
        model = Item

    category = ModelFormField(CategorySelectForm)


def get_item_label(item):
    return (
        f"{item.name} {item.price}€"
        f"{', '+item.volume if item.volume else ''}"
        f"{', '+item.price_per_volume if item.price_per_volume else ''}"
        f"{' sale' if item.sale else ''}"
        f"{', '+item.note if item.note else ''}"
    )


def convert_str_to_int(i):
    try:
        return int(i)
    except ValueError:
        current_app.logger.debug(f"Could not convert listentry {i} to {type(int())}.")
        return None


class HiddenListIntegerField(HiddenField):
    def process_formdata(self, valuelist):
        if valuelist:
            new_valuelist = []
            for x in valuelist[0].split(','):
                x = convert_str_to_int(x.strip())
                if x:
                    new_valuelist.append(x)
            data = {}
            for x in new_valuelist:
                occurences = new_valuelist.count(x)
                data.update({x: occurences})
            self.data = data
        else:
            self.data = {}


class ListForm(FlaskForm):
    id = HiddenField()
    test = HiddenListIntegerField()
    date = DateField(validators=[Required()], description="Date of purchase")
    price = DecimalField(validators=[Required()], description="Total price")

    shop = QuerySelectField(
        validators=[Required()],
        query_factory=lambda: Shop.query.order_by(Shop.name),
        get_label='name',
        allow_blank=True,
        blank_text="Select a Shop",
        description="Shop where purchase took place",
    )
    category = QuerySelectField(
        query_factory=lambda: Category.query.order_by(Category.name),
        get_label='name',
        allow_blank=True,
        blank_text="Select a category",
        description="Category of purchase",
    )

    items_obj = QuerySelectMultipleField(
        validators=[Required()],
        query_factory=lambda: Item.query,
        allow_blank=False,
        get_label=get_item_label
    )


class FilterForm(FlaskForm):
    date_min = DateField(label="Start Date", validators=[])
    date_max = DateField(label="End Date", validators=[])
    price_min = DecimalField(label="Min Price")
    price_max = DecimalField(label="Max Price")
    shop = StringField(label="Shop")
    category = StringField(label="Category")
    item = StringField(label="Items")

    def validate_date_min(form, field):
        if form.date_max.data and field.data and form.date_max.data < field.data:
            raise ValidationError('Max date has to be higher than min date.')
        elif (form.date_max.data and not field.data) \
                or (not form.date_max.data and field.data):
            raise ValidationError('Both Max date and min date eiher have to be set or not set.')


class RoomDataForm(ModelForm):
    class Meta:
        model = RoomData
    date = DateTimeField(validators=[Required()])


class MqttForm(ModelForm):
    class Meta:
        model = Mqtt
    # date = DateTimeField()
    # Date = DateField()


class RfDataForm(ModelForm):
    class Meta:
        model = RfData
    date = DateTimeField(validators=[Required()])


class ProbeRequestForm(ModelForm):
    class Meta:
        model = ProbeRequest
    date = DateTimeField(validators=[Required()])


class StateForm(ModelForm):
    class Meta:
        model = State
    date = DateTimeField(validators=[Required()])


class TabletBatteryForm(ModelForm):
    class Meta:
        model = TabletBattery
    date = DateTimeField(validators=[Required()])
