from flask import current_app

from flask_wtf import FlaskForm

from wtforms import BooleanField
from wtforms_alchemy import model_form_factory
from wtforms.fields import HiddenField
# , StringField, Field, SelectField, SelectMultipleField, SearchField,
from wtforms.fields.html5 import DateField, DecimalField
from wtforms.validators import Required
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField

from ..models import db
from ..models.Shopping import Item, Shop, Category

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


class ItemForm(ModelForm):
    class Meta:
        model = Item


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
        query_factory=lambda: Shop.query,
        get_label='name',
        allow_blank=True,
        blank_text="Select a Shop",
        description="Shop where purchase took place",
    )
    category = QuerySelectField(
        query_factory=lambda: Category.query,
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
