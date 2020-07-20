#!/usr/bin/env python3

from . import db, BaseMixin


class State(db.Model, BaseMixin):
    __tablename__ = 'states'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    device = db.Column(db.String)
    state = db.Column(db.String)

    def to_dict(self):
        return {
            'date': self.date,
            'device': self.device,
            'state': self.state,
        }

    def __repr__(self):
        return (
            "<State(id={self.id}, "
            f"date={self.date}, "
            f"device={self.device}, "
            f"state={self.state})>"
        )
