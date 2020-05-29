#!/usr/bin/env python3

import argparse
import logging

# setup logging
parser = argparse.ArgumentParser()
parser.add_argument(
    '-d', '--debug',
    help="Print debugging statements",
    action="store_const", dest="loglevel", const=logging.DEBUG,
    default=logging.WARNING,
)
parser.add_argument(
    '-v', '--verbose',
    help="Be verbose",
    action="store_const", dest="loglevel", const=logging.INFO,
)

args, _ = parser.parse_known_args()
logging.basicConfig(
    format="%(module)15s - %(levelname)-8s : %(message)s",
    level=args.loglevel
)
