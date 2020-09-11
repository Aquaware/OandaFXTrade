# -*- coding: utf-8 -*-
import numpy as np
import configparser
from threading import Thread

from utils import bool_from_str
from oandaapi.oanda import oandaClient
from functools import partial
from datetime import datetime
from model.Prices import Tick
from model.PriceDB import TableClassWithTick
from Streaming import stream

class App(object):
    def __init__(self):
        self.setting()

    def setting(self):
        conf = configparser.ConfigParser()
        conf.read('./settings.ini')
        self.account = conf['oanda']['account_id']
        self.key = conf['oanda']['api_key']
        self.db_name = conf['db']['name']
        self.db_driver = conf['db']['driver']
        self.web_port = int(conf['web']['port'])
        self.trade_duration = conf['trading']['trade_duration'].lower()
        self.back_test = bool_from_str(conf['trading']['back_test'])
        self.use_percent = float(conf['trading']['use_percent'])
        self.past_period = int(conf['trading']['past_period'])
        self.stop_limit_percent = float(conf['trading']['stop_limit_percent'])
        self.num_ranking = int(conf['trading']['num_ranking'])
        return

    def test(self):
        client = oandaClient(self.account, self.key)
        res = client.summary()
        print(res['account']['currency'], res['account']['balance'])
        res = client.currentPrice('USD_JPY')
        prices = res['prices'][0]
        print(prices['bids'][0]['price'], prices['asks'][0]['price'])

        res = client.candles('USD_JPY', 'M5', 5)
        candles = res['candles']
        for candle in candles:
            print(candle)

    def test2(self):
        client = oandaClient(self.account, self.key)
        callback = partial(self.recievedTick)
        res = client.streamTick(callback, 'USD_JPY')

    def recievedTick(self, tick):
        print(tick.currency, tick.time, tick.bid, tick.ask, tick.volume)

    def test3(self):
        client = oandaClient(self.account, self.key)
        res = client.order('AUD_USD', 1000, 'short')
        print(res)

    def test4(self):
        client = oandaClient(self.account, self.key)
        res = client.closePosition('45')
        print(res)

    def test5(self):
        from model.PriceDB import OandaUsdJpyM5
        t = datetime(2020, 1, 1, 0, 0, 0)
        candle1 = OandaUsdJpyM5.get(t)
        print(candle1.open)
        candle1.open = 122.0
        candle1.save()
        candle2 = OandaUsdJpyM5.get(t)
        print(candle2.open)

    def test6(self):
        from model.PriceDB import OandaUsdJpyM5
        t = datetime(2020, 2, 2, 12, 30, 0)
        candle = OandaUsdJpyM5.create(t, [10, 20, 0, 30, 10])
        candle.save()
        candle2 = OandaUsdJpyM5.get(t)
        print(candle2.open)

    def test7(self):
        from model.PriceDB import OandaUsdJpyM5
        candles = OandaUsdJpyM5.allCandles()
        for candle in candles:
            print(candle.value)

    def test8(self):
        t1 = datetime(2020, 8, 10, 12, 10, 11)
        t2 = datetime(2020, 8, 10, 12, 10, 12)
        t3 = datetime(2020, 8, 10, 12, 11, 10)
        t4 = datetime(2020, 8, 10, 12, 20, 10)
        t5 = datetime(2020, 8, 10, 12, 22, 0)

        tick = Tick('usd_jpy', t5, 130.2, 140.1, 200)
        TableClassWithTick('usd_jpy', 'M5', tick)

    def test9(self):
        thread = Thread(target=stream.stream)
        thread.start()
        thread.join()

if __name__ == '__main__':
    app = App()
    app.test9()