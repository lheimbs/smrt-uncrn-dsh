#!/usr/bin/env python3

import logging
from ..app import db, server

logger = logging.getLogger()


def precheck_errors():
    tables = ['room-data', 'rf-data', 'mqtt-message', 'list', 'item', 'shop', 'category']
    errors_str = []
    errors_dict = {
        'database': False,
        'database-probes': False,
    }
    try:
        db.session.execute("SELECT 1")
    except Exception as exc:
        logger.warning("Database not found.")
        logger.debug(exc)
        errors_str.append("ERROR: Database not found.")
        errors_dict['database'] = True
    try:
        db.session.execute("SELECT 1", bind=db.get_engine(server, 'probe-requests'))
    except Exception as exc:
        logger.warning("Database for Probe-Requests not found.")
        logger.debug(exc)
        errors_str.append("ERROR: Database for Probe-Requests not found.")
        errors_dict['database-probes'] = True

    for table in tables:
        if db.engine.has_table(table):
            errors_dict[table] = False
        else:
            logger.warning(f"Table {table} not found in database.")
            errors_str.append(f"ERROR: Table {table} not found in database.")
            errors_dict.update({table: True})
    return errors_str, errors_dict
