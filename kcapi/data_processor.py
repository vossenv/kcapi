import csv
import os


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

    def to_csv_pairs(self, orders_by_pair, folder):

        os.makedirs(folder, exist_ok=True)

        for p, orders in orders_by_pair.items():
            filename = os.path.join(folder, p + ".csv")
            with open(filename, "w", newline='') as f:
                writer = csv.DictWriter(f, fieldnames=orders[0].keys())
                writer.writeheader()
                writer.writerows(orders)
