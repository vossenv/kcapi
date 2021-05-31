import logging
import logging.config
import os

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
