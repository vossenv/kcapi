import csv
import os
from datetime import timedelta


class DataProcessor:

    def __init__(self, orders):

        self.orders = orders

    def sort_by_pair(self):

        orders_by_pair = {}

        for i, o in self.orders.items():
            pair = o['symbol']
            if pair not in orders_by_pair:
                orders_by_pair[pair] = []
            orders_by_pair[pair].append(o)

        return orders_by_pair

    def to_time_accurate(self, orders):
        start = orders[-1]['createdAt']
        end = orders[0]['createdAt']
        hours = round((end - start).total_seconds() / 60)
        for h in range(hours):
            start += timedelta(minutes=1)
            orders.append({
                'side': 'sell',
                'funds': 0,
                'size': 0,
                'createdAt': start
            })
        return orders

    def summarize_pairs(self, orders_by_pair):

        data = {}

        for p, orders in orders_by_pair.items():

            coins = 0
            standing = 0
            fees = 0
            for o in orders:
                buy = o['side'] == 'buy'
                size = float(o['size'])
                funds = float(o['funds'])
                fee = float(o['fee'])
                coins += size if buy else -size
                standing += -funds if buy else funds
                fees += fee

            data[p] = {
                'pair': p,
                'coins': coins,
                'standing': standing,
                'fees': fees,
            }
        return data

    def to_csv_pairs(self, orders_by_pair, folder):

        os.makedirs(folder, exist_ok=True)
        for p, orders in orders_by_pair.items():
            # orders = self.to_time_accurate(orders)
            filename = os.path.join(folder, p + ".csv")
            with open(filename, "w", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=orders[0].keys())
                writer.writeheader()
                writer.writerows(orders)

    def to_csv_summary(self, summary, folder):

        os.makedirs(folder, exist_ok=True)
        filename = os.path.join(folder, "summary.csv")
        v = list(summary.values())
        with open(filename, "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=v[0].keys())
            writer.writeheader()
            writer.writerows(v)