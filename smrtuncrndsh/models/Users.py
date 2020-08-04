from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import db, BaseMixin


class User(UserMixin, db.Model, BaseMixin):
    """User account model."""
    # __bind_key__ = 'users'
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

    # lists = db.relationship("Liste")

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(
            password,
            method='sha256'
        )

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def activate_user(self):
        self.is_activated = True
        self.db_commit()

    def add_to_db(self):
        self.created_on = datetime.now()
        db.session.add(self)
        self.db_commit()

    def __repr__(self):
        return (
            f"<User(id={self.id}, "
            f"name={self.name}, "
            f"username={self.username}, "
            f"email={self.email}, "
            f"is_admin='{self.is_admin}', "
            f"is_activated='{self.is_activated}')>"
        )

    def to_dict(self):
        return {
            'name': self.name,
            'email': self.email,
            'last_login': self.last_login
        }

    def to_ajax(self):
        return {
            'edit': '',
            'delete': '',
            'id': self.id,
            'date': self.date,
            'name': self.name if self.name else '-',
            'username': self.username if self.username else '-',
            'email': self.email if self.email else '-',
            'last_login': self.last_login if self.last_login else '-',
            'created_on': self.created_on if self.created_on else '-',
            'is_admin': self.is_admin,
            'is_activated': self.is_activated,

        }

    # Required for administrative interface
    def __unicode__(self):
        return self.username
