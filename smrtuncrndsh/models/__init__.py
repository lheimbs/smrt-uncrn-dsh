# from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()


class BaseMixin(object):
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def db_commit(self):
        db.session.commit()

    @classmethod
    def create(model_class, **kwargs):
        new_obj = model_class(**kwargs)
        BaseMixin.add_object_to_db(new_obj)
        db.session.add(new_obj)
        db.session.commit()

    @classmethod
    def get_count(model_class):
        query = model_class.query
        count_query = query.statement.with_only_columns([func.count()]).order_by(None)
        count = query.session.execute(count_query).scalar()
        return count


def init_db(app):
    db.init_app(app)

    with app.app_context():
        from .Users import User
        from .RoomData import RoomData      # noqa: F401
        from .RfData import RfData      # noqa: F401
        from .ProbeRequest import ProbeRequest      # noqa: F401
        from .Mqtt import Mqtt      # noqa: F401
        from .State import State      # noqa: F401
        from .Tablet import TabletBattery      # noqa: F401
        from .Shopping import Liste, Shop, Category, Item      # noqa: F401

        if app.config['DROP_ALL']:
            app.logger.debug("Drop all Database Tables")
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
