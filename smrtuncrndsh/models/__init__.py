from flask import current_app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class BaseMixin(object):
    @classmethod
    def create(model_class, **kwargs):
        new_obj = model_class(**kwargs)
        BaseMixin.add_object_to_db(new_obj)
        db.session.add(new_obj)
        db.session.commit()


def init_db(app):
    db.init_app(app)

    with app.app_context():
        from .Users import User
        if app.config['DROP_ALL']:
            db.drop_all()
        db.create_all()

        admin = app.config['ADMIN']['username']
        user = User.query.filter_by(username=admin).first()
        if user:
            user.delete_from_db()
        user = User(
            name='Admin',
            is_admin=True,
            is_activated=True,
            username=app.config['ADMIN']['username'],
            email=app.config['ADMIN']['email']
        )
        user.set_password(app.config['ADMIN']['password'])
        user.add_to_db()
