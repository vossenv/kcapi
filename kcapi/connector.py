import logging
from datetime import timedelta, datetime

from kucoin.client import Trade

from kcapi.util import utcnowloc


class KCConnector:

    def __init__(self, api_key, api_secret, api_passphrase, **kwargs):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.client = self.connect()
        self.logger = logging.getLogger("kc-connector")

    def connect(self):
        return Trade(self.api_key, self.api_secret, self.api_passphrase)

    def get_orders(self, start_date, end_date, pair=None) -> dict:

        if start_date > utcnowloc() or end_date > utcnowloc():
            raise AssertionError("Dates cannot be in the future")
        if start_date > end_date:
            raise AssertionError("Start date must be BEFORE end date")

        orders = {}
        end_date = end_date + timedelta(days=1)
        while True:
            if end_date - start_date < timedelta(weeks=1):
                orders.update(self.get_orders_delta(start_date, end_date, pair))
                break
            else:
                orders.update(self.get_orders_delta(start_date, start_date + timedelta(weeks=1), pair))
            start_date += timedelta(weeks=1)
            self.logger.info("Total items: {}".format(len(orders)))

        return {k: v for k, v in sorted(orders.items(), key=lambda x: x[1]['createdAt'], reverse=True)}

    def get_orders_delta(self, start, end, pair=None) -> dict:

        if start - end > timedelta(weeks=1):
            raise AssertionError("Order delta must be no longer than 1 week")

        orders = {}
        kwargs = {
            'tradeType': "TRADE",
            'pageSize': 500,
            'startAt': int(start.timestamp() * 1000),
            'endAt': int(end.timestamp() * 1000),
            'currentPage': 1
        }

        if pair:
            kwargs['symbol'] = pair

        while True:
            result = self.client.get_fill_list(**kwargs)
            if not result['items']:
                self.logger.info("No orders from {} - {}".format(start.date(), end.date()))
                break
            self.logger.info('Getting orders from {} - {}'.format(start.date(), end.date()))
            for o in result['items']:
                oid = "{}-{}-{}".format(o['tradeId'], o['orderId'], o['counterOrderId'])
                o['createdAt'] = datetime.fromtimestamp(int(o['createdAt'])/1000.0)
                o['uoid'] = oid
                orders[oid] = o
            self.logger.info("Fetched page {}/{}".format(result['currentPage'], result['totalPage']))
            if kwargs['currentPage'] == result['totalPage']:
                break
            kwargs['currentPage'] += 1
        return orders
