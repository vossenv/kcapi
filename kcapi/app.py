import sys
from datetime import datetime

import pytz as pytz
import yaml

from kcapi.connector import KCConnector

try:
    cfg = sys.argv[1]
except:
    cfg = "config.yml"

with open(cfg) as f:
    conf = yaml.safe_load(f)

conn = KCConnector(**conf)

start_date = pytz.timezone("UTC").localize(datetime.strptime('3/14/2021', '%m/%d/%Y'))
end_date = pytz.timezone("UTC").localize(datetime.strptime('3/25/2021', '%m/%d/%Y'))

x = conn.get_orders(start_date, end_date)


print()
