import flask_admin as admin
from flask_admin.form import RenderTemplateWidget
from flask_admin.model.form import InlineFormAdmin
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.form import InlineModelConverter
from flask_admin.contrib.sqla.fields import InlineModelFormList

from flask import Flask, request, render_template

from wtforms import fields

from ..models.Users import User




# Administrative class
class LocationAdmin(ModelView):
    inline_model_form_converter = CustomInlineModelConverter

    inline_models = (InlineModelForm(),)

    def __init__(self):
        super(LocationAdmin, self).__init__(Location, db.session, name='Locations')

