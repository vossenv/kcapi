import logging
import math
from datetime import timedelta, datetime

from kucoin.client import Trade, Market, User

from kcapi.util import utcnowloc


class KCConnector:

    def __init__(self, api_key, api_secret, api_passphrase, **kwargs):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.trade_client = Trade(self.api_key, self.api_secret, self.api_passphrase)
        self.user_client = User(self.api_key, self.api_secret, self.api_passphrase)
        self.market_client = Market(url='https://api.kucoin.com')
        self.logger = logging.getLogger("kc-connector")
        self.pairs_info = {}

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

        return {k: v for k, v in sorted(orders.items(), key=lambda x: x[1]['createdAt'], reverse=False)}

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
            result = self.trade_client.get_fill_list(**kwargs)
            if not result['items']:
                self.logger.info("No orders from {} - {}".format(start.date(), end.date()))
                break
            self.logger.info('Getting orders from {} - {}'.format(start.date(), end.date()))
            for o in result['items']:
                oid = "{}-{}-{}".format(o['tradeId'], o['orderId'], o['counterOrderId'])
                o['createdAt'] = datetime.fromtimestamp(int(o['createdAt']) / 1000.0)
                o['uoid'] = oid
                orders[oid] = o
            self.logger.info("Fetched page {}/{}".format(result['currentPage'], result['totalPage']))
            if kwargs['currentPage'] == result['totalPage']:
                break
            kwargs['currentPage'] += 1
        return orders

    def get_price(self, ticker):
        data = self.market_client.get_ticker(ticker)
        return float(data['price'])

    def set_trade_currency_info(self, pairs):
        for pair in pairs:
            data = [p for p in self.market_client.get_symbol_list() if p['symbol'] == pair]
            if len(data) > 1:
                raise AssertionError("Found too many matches for pair {}: {}".format(pair, data))
            d = data[0]
            d['digits'] = len(d['baseIncrement'].split(".")[1])
            self.pairs_info[d['symbol']] = d

    def get_balance(self, pair):
        if not pair in self.pairs_info:
            self.set_trade_currency_info([pair])

        curr = pair.split("-")[0]
        accounts = [a for a in self.user_client.get_account_list() if a['currency'] == curr and a['type'] == 'trade']
        if len(accounts) > 1:
            raise AssertionError("Found too many accounts for pair {}: {}".format(pair, accounts))
        return float(accounts[0]['available'])

    def market_sell(self, pair, amt=100):

        size = amt * 0.01 * self.get_balance(pair)
        rounded = self.truncate(size, self.pairs_info[pair]['digits'])
        order_id = self.trade_client.create_market_order(pair, 'sell', size=rounded)
        self.logger.info("Placed market sell ({}) for {} at {}%: total amount: {}".format(order_id, pair, amt, rounded))

        return order_id['orderId']

    def truncate(self, f, n):
        return math.floor(f * 10 ** n) / 10 ** n

    def get_order(self, orderid):
        return self.trade_client.get_order_details(orderid)