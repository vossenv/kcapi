import sys
from datetime import datetime

import pytz as pytz
import yaml

from kcapi.connector import KCConnector
from kcapi.util import init_logger


def to_date(datestring):
    if datestring:
        return pytz.timezone("UTC").localize(datetime.strptime(datestring, '%m/%d/%Y'))
try:
    cfg = sys.argv[1]
except:
    cfg = "config.yml"

with open(cfg) as f:
    conf = yaml.safe_load(f)

logger = init_logger(conf['log_level'])
conn = KCConnector(**conf)

orders = conn.get_orders(to_date(conf['start_date']), to_date(conf['end_date']))

print()


