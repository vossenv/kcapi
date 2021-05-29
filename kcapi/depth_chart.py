import csv
import threading
import time

import matplotlib.pyplot as plt
import numpy as np
import requests
from matplotlib import ticker
from matplotlib.figure import Figure


def process(items):
    results = []
    total = 0
    total_usd = 0

    for n, i in enumerate(items):
        p = float(i[0])
        a = float(i[1])
        usd = a * p
        total += a
        total_usd += usd
        entry = {
            'price': p,
            'amnt': a,
            # 'usd': round(usd),
            'total': round(total),
            'increase': 0,
            'wall': False
            # 'total_usd': total_usd,
        }

        results.append(entry)

    for i, r in enumerate(results[1:]):
        r['increase'] = (r['total'] - results[i]['total'])
        r['wall'] = r['increase'] > 100000

    return results


def write(data, name):
    with open(name, 'w', newline='') as f:
        w = csv.DictWriter(f, data[0].keys())
        w.writeheader()
        for b in data:
            w.writerow(b)

# def write_all():
#     write(buys, 'buys.csv')
#     write(sells, 'sells.csv')
#     write([b for b in sells if b['wall']], 'sell_walls.csv')
#     write([b for b in buys if b['wall']], 'buy_walls.csv')




fig, ax = plt.subplots()
fig.set_figheight(5)
fig.set_figwidth(20)

f = Figure()
ax.set_yscale('log')
ax.set_title("BEPRO-USDT", color='#ffffff')
ax.set_xlabel('$ USDT', color='#ffffff')
ax.set_ylabel('Total BEPRO', color='#ffffff')

ax.set_facecolor('#1f1f1f')
fig.set_facecolor('#1f1f1f')


ax.tick_params(axis='x', colors='#ffffff', direction='in')
ax.tick_params(axis='y', colors='#ffffff', direction='in')

sp = '#999999'
ax.spines['bottom'].set_color(sp)
ax.spines['top'].set_color(sp)
ax.spines['right'].set_color(sp)
ax.spines['left'].set_color(sp)
# ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
plt.grid(color='k', linestyle='--')

center = 0.4
spread = 0.2
minp = center - spread
maxp = center + spread
plt.xlim(minp, maxp)
plt.ylim(bottom=1000, top=1e7)
start, end = ax.get_xlim()
#ax.xaxis.set_ticks(np.arange(start, end, 0.0001))


#- define your own locator based on ticker.LinearLocator
# class MyLocator(ticker.LinearLocator):
#    def tick_values(self, vmin, vmax):
#        "vmin and vmax are the axis limits, return the tick locations here"
#        return np.arange(vmin, vmax, 0.0001)
#
# #- initiate the locator and attach it to the current axis
# ML = MyLocator()
# ax.xaxis.set_major_locator(ML)

def get():
    x = requests.get('https://api.kucoin.com/api/v2/market/orderbook/level2?symbol=HORD-USDT')
    res = x.json()['data']
    buys = process(res['bids'])
    sells = process(res['asks'])

    # minp = 0.0113
    # maxp = 0.0125

    buy_depth = {b['price']: b['total'] for b in buys if b['price'] >= minp}
    sell_depth = {b['price']: b['total'] for b in sells if b['price'] <= maxp}

    return buy_depth.keys(), buy_depth.values(), sell_depth.keys(), sell_depth.values()


#plt.ion()

#bx, by, sx, sy = get()

def update():
    first = True
    #while True:
    bx, by, sx, sy = get()


    # plt.xlim(minp, maxp)
    # plt.ylim(1000, 10000000)
    #
    # start, end = ax.get_xlim()
    # ax.xaxis.set_ticks(np.arange(start, end, 0.0001))

    ax.fill_between(bx, by, color='#00c431')
    ax.fill_between(sx, sy, color='#eb3434')
    plt.show()

    #
    # if first:
    #     plt.show()
    #     first = False
        # else:
        #     plt.draw()

        # print('x')
        # time.sleep(5)
        #plt.clf()
update()

#fig.canvas.draw()

print()
