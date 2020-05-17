#!/usr/local/bin/python3

# Author: Zebing Lin (https://github.com/linzebing)
from yahoo_fin import stock_info as si
from datetime import datetime
from datetime import date
import math
import numpy as np
import time
import sys
import requests

total_money = float(input("your desired investing money: "))

if len(sys.argv) == 1:
    symbols = ['FNGU', 'TMF']
else:
    symbols = sys.argv[1].split(',')
    for i in range(len(symbols)):
        symbols[i] = symbols[i].strip().upper()

log_return_1_percentage_return_0 = 1
num_trading_days_per_year = 252
window_size = 20
date_format = "%Y-%m-%d"
end_timestamp = int(time.time())
start_timestamp = int(end_timestamp - (1.4 * (window_size + 1) + 4) * 86400)


def get_volatility_and_performance(symbol):
    download_url = "https://query1.finance.yahoo.com/v7/finance/download/{}?period1={}&period2={}&interval=1d&events=history&crumb=a7pcO//zvcW".format(
        symbol, start_timestamp, end_timestamp)
    lines = requests.get(download_url, cookies={'B': 'chjes25epq9b6&b=3&s=18'}).text.strip().split('\n')

    assert lines[0].split(',')[0] == 'Date'
    assert lines[0].split(',')[4] == 'Close'

    prices = []
    for line in lines[1:]:
        prices.append(float(line.split(',')[4]))

    prices.reverse()
    volatilities_in_window = []

    for i in range(window_size):
        volatility = (prices[i] / prices[i + 1])-1 if log_return_1_percentage_return_0 == 0 else math.log((prices[i] / prices[i + 1]))
        volatilities_in_window.append(volatility)

    most_recent_date = datetime.strptime(lines[-1].split(',')[0], date_format).date()
    assert (date.today() - most_recent_date).days <= 4, "today is {}, most recent trading day is {}".format(
       date.today(), most_recent_date)

    return np.std(volatilities_in_window, ddof=1) * np.sqrt(num_trading_days_per_year), prices[0] / prices[window_size] - 1.0

volatilities = []
performances = []
sum_inverse_volatility = 0.0
for symbol in symbols:
    volatility, performance = get_volatility_and_performance(symbol)
    sum_inverse_volatility += 1 / volatility
    volatilities.append(volatility)
    performances.append(performance)

print("Portfolio: {}, as of {} (window size is {} days)".format(str(symbols), date.today().strftime('%Y-%m-%d'),
                                                                window_size))
prices_shares = []
invested = 0
for i in range(len(symbols)):
    print('{} allocation ratio: {:.2f}% (anualized volatility: {:.2f}%, performance: {:.2f}%)'.format(symbols[i], float(
        100* 1 / volatilities[i] / sum_inverse_volatility ), float(volatilities[i] * 100), float(performances[i] * 100)))

    ratio = float(100* 1 / volatilities[i] / sum_inverse_volatility)
    portion = ratio * (total_money) /100
   # print('{} money portion: ${:.2f}'.format(symbols[i] ,portion ))

    price = si.get_live_price(symbols[i])
    share = int(portion/price)
    prices_shares.append({"stock":symbols[i],"price":round(price, 2),"shares hold":share})
    invested+= share*price
print(*prices_shares,sep='\n')
print("invested money: ",invested)