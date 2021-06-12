import logging
import time

from kcapi.connector import KCConnector


class Trailer():

    def __init__(self, config):

        self.connector = KCConnector(**config)

        self.trail_focus = config['trail_focus']
        self.sell_pairs = config['sell_pairs']
        self.trail_amt = float(config['trail_amt'])
        self.trail_target = float(config['trail_target'])
        self.logger = logging.getLogger("trailer")

    def run(self):

        high_price = 0
        self.connector.set_trade_currency_info(self.sell_pairs)

        while True:

            price = self.connector.get_price(self.trail_focus)

            high_price = price if price > high_price else high_price
            trailing_perc = (price - high_price) / high_price * 100
            total_perc = (price - self.trail_target) / self.trail_target * 100

            self.logger.info(
                "Price c/h/t: {}/{}/{}, trail_perc: {}, total_perc: {}".format(price, high_price, self.trail_target,
                                                                               trailing_perc, total_perc))

            if trailing_perc <= -self.trail_amt:
                self.logger.warning("Trail triggered - beginning sell {}".format(self.sell_pairs))

                orders = []
                for p in self.sell_pairs:
                    try:
                        self.logger.info("Selling {}".format(p))
                        orders.append(self.connector.market_sell(p, 10))
                    except Exception as e:
                        self.logger.error(e)

                for o in orders:
                    try:
                        info = self.connector.get_order(o)
                        rate = float(info['dealFunds']) / float(info['dealSize'])
                        self.logger.info("Order details: Sold {} {}, avg. price -> ${}, total -> ${}"
                                         .format(info['dealSize'], info['symbol'], rate, info['dealFunds']))
                    except Exception as e:
                        self.logger.error("Error getting order details for {}: {}".format(o, e))

                self.logger.warning("Trail complete - exit")
                break

            time.sleep(3)


