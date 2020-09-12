from functools import partial
import logging
import configparser

from utils import bool_from_str
from model.PriceDB import TableClass, TableClassWithTick
from oandaapi.oanda import oandaClient
from model.Prices import Tick, Candle

class Streaming(object):
    def __init__(self, currency):
        self.currency = currency
        self.timeframes = ['M1', 'M5', 'M10', 'M15', 'M30', 'H1', 'H4', 'H8', 'D1']
        self.setting()
        self.api = oandaClient(self.account, self.key)

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

    def streaming(self):
        callback = partial(self.store)
        self.api.streamTick(callback, self.currency)

    def store(self, tick: Tick):
        print(tick.time, tick.currency, tick.bid, tick.ask, tick.volume)
        for timeframe in self.timeframes:
            TableClassWithTick(self.currency, timeframe, tick)

# ------
stream = Streaming('USD_JPY')

