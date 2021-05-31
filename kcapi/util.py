import logging
import logging.config
import os
from datetime import datetime

import pytz as pytz
import yaml

from kcapi.resources import get_resource


def init_logger(level):
    if not os.path.exists("logs"):
        os.mkdir("logs")
    with open(get_resource("logger_config.yaml")) as cfg:
        data = yaml.safe_load(cfg)
        data['loggers']['']['level'] = level.upper() if level else 'INFO'
        logging.config.dictConfig(data)
        return logging.getLogger()

def utcnowloc():
    return localize(datetime.utcnow())

def localize(date_obj):
    return pytz.timezone("UTC").localize(date_obj)

def to_date(datestring):
    return localize(datetime.strptime(datestring, '%m/%d/%Y'))

def date_to_str(date):
    return datetime.strftime(date, '%Y-%m-%d')
