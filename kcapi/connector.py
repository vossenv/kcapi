from datetime import datetime, timedelta

from kucoin.client import Trade


class KCConnector:

    def __init__(self, api_key, api_secret, api_passphrase):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.client = self.connect()

    def connect(self):
        return Trade(self.api_key, self.api_secret, self.api_passphrase)

    def get_orders(self, start_date, end_date=None) -> dict:

        orders = {}
        end_date = datetime.utcnow() if not end_date else end_date + timedelta(days=1)

        while True:
            if end_date - start_date < timedelta(weeks=1):
                orders.update(self.get_orders_delta(start_date, end_date))
                break
            else:
                orders.update(self.get_orders_delta(start_date))
            start_date += timedelta(weeks=1)

        return orders

    def get_orders_delta(self, start, end=None) -> dict:

        if end and (start - end) > timedelta(weeks=1):
            raise AssertionError("Order delta must be no longer than 1 week")

        orders = {}
        kwargs = {
            'tradeType': "TRADE",
            'pageSize': 500,
            'startAt': int(start.timestamp() * 1000),
            'currentPage': 1
        }

        if end:
            kwargs['endAt'] = int(end.timestamp() * 1000)

        while True:
            result = self.client.get_fill_list(**kwargs)
            for o in result['items']:
                oid = "{}-{}-{}".format(o['tradeId'], o['orderId'], o['counterOrderId'])
                orders[oid] = o
            if kwargs['currentPage'] == result['totalPage']:
                break
            print("Fetched page {}/{}".format(result['currentPage'], result['totalPage']))
            kwargs['currentPage'] += 1
        return orders
