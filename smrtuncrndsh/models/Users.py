from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import db


class User(UserMixin, db.Model):
    """User account model."""
    __bind_key__ = 'users'
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True, unique=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    username = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(200), primary_key=False, unique=False, nullable=False)
    created_on = db.Column(db.DateTime, index=False, unique=False, nullable=True)
    last_login = db.Column(db.DateTime, index=False, unique=False, nullable=True)
    is_admin = db.Column(db.Boolean, index=False, unique=False, nullable=False)
    is_activated = db.Column(db.Boolean, index=False, unique=False, nullable=False)

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(
            password,
            method='sha256'
        )

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def add_to_db(self):
        self.created_on = datetime.now()
        db.session.add(self)
        self.db_commit()

    def delete_from_db(self):
        db.session.delete(self)
        self.db_commit()

    def db_commit(self):
        db.session.commit()

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def to_dict(self):
        return {
            'name': self.name,
            'email': self.email,
            'last_login': self.last_login
        }

    # Required for administrative interface
    def __unicode__(self):
        return self.username


# class AccessRequested(db.Model):
#     __bind_key__ = 'users'
#     __tablename__ = 'flaskregister-requested-users'

#     user = db.Column(
#         User
#     )
