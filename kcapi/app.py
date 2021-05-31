import os.path
import sys

import yaml

from kcapi.connector import KCConnector
from kcapi.data_processor import DataProcessor
from kcapi.util import init_logger, to_date, date_to_str, utcnowloc

try:
    cfg = sys.argv[1]
except:
    cfg = "config.yml"

with open(cfg) as f:
    conf = yaml.safe_load(f)

logger = init_logger(conf.get('log_level'))
conn = KCConnector(**conf)

start = to_date(conf['start_date'])
end = to_date(conf.get('end_date')) if conf.get('end_date') else utcnowloc()

orders = conn.get_orders(start, end)
d = DataProcessor(orders)

root = os.path.dirname(cfg)
folder = os.path.join(root, "output_{}_to_{}".format(date_to_str(start), date_to_str(end)))

d.to_csv_pairs(d.sort_by_pair(), folder=folder)
