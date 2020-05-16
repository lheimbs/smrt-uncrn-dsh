#!/usr/bin/env python3

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
ProbeBase = declarative_base()
Session = sessionmaker()
ProbeSession = sessionmaker()

def bind_engine(engine):
    Base.metadata.bind = engine
    Session.configure(bind=engine)


def bind_probe_engine(engine):
    ProbeBase.metadata.bind = engine
    ProbeSession.configure(bind=engine)
