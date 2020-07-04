from flask_wtf import FlaskForm
from wtforms import BooleanField


class ActivateForm(FlaskForm):
    def __init__(self, username, *args, **kwargs):
        super(ActivateForm, self).__init__(*args, **kwargs)
        self.username = username

    activate = BooleanField()
