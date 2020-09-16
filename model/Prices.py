from datetime import datetime, timedelta, timezone
import pytz
import dateutil.parser
from model.PriceDB import TableClass, TableClassWithTick

import logging
logger = logging.getLogger(__name__)


MINUTE = 'minute'
HOUR = 'hour'
DAY = 'day'
WEEK = 'week'

LOCAL_TIMEZONE = pytz.timezone('Asia/Tokyo')

def timeframeValue(timeframe):
    s1 = timeframe[0].lower()
    s2 = timeframe[1:]
    if s1 == 'm':
        unit = MINUTE
    elif s1 == 'h':
        unit = HOUR
    elif s1 == 'd':
        unit = DAY
    elif s1 == 'w':
        unit = WEEK
    return (int(s2), unit)

def gmt2Jst(gst_aware_time):
    t = gst_aware_time + timedelta(hours=9)
    jst_aware_time = t.astimezone(LOCAL_TIMEZONE)
    jst_naive_time = datetime.utcfromtimestamp(jst_aware_time.timestamp)
    return (jst_aware_time, jst_naive_time)

# ------

class CandleData(object):
    def __init__(self, currency, timeframe):
        self.currency = currency
        self.timeframe = timeframe
        self.table = TableClass(currency, timeframe)
        self.candles = []

    def loadData(self, limit=1000):
        self.candles = self.table.allCandles(limit)
        return self.candles

    @property
    def value(self):
        return {'currency': self.currency, 'timeframe': self.timeframe, 'candles': [c.value for c in self.candles]}

# -----

class Candle(object):
    def __init__(self, currency, timeframe, time, open, high, low, close, volume):
        self.currency = currency
        self.timeframe = timeframe
        self.time = time
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

    @property
    def value(self):
        return {
            'time': self.time,
            'open': self.open,
            'close': self.close,
            'high': self.high,
            'low': self.low,
            'volume': self.volume,
        }

    @classmethod
    def parse(self, response):
        currency = response['instrument']
        timeframe = response['granularity']
        list = response['candles']
        candles = []
        try:
            for l in list:
                time_str = l['time']
                time = dateutil.parser.parse(time_str)
                volume = l['volume']
                open = l['mid']['o']
                high = l['mid']['h']
                low = l['mid']['l']
                close = l['mid']['c']
                candle = Candle(currency, timeframe, time, open, high, low, close, volume)
                candles.append(candle)
            return candles
        except:
            return None

# ---------------------------

class Tick(object):
    def __init__(self, currency, time, bid, ask, volume):
        self.currency = currency
        self.time = time
        self.bid = bid
        self.ask = ask
        self.volume = volume

    @classmethod
    def parse(self, response):
        try:
            time_str = response['time']
            time = dateutil.parser.parse(time_str)
            currency = response['instrument']
            bid = float(response['bids'][0]['price'])
            ask = float(response['asks'][0]['price'])
            tick = Tick(currency, time, bid, ask, None)
            return tick
        except:
            return None

    @property
    def mid_price(self):
        return (self.bid + self.ask) / 2

    #@property
    #def time(self):
    #    return datetime.utcfromtimestamp(self.timestamp)

    def roundTime(self, timeframe):
        t0 = self.time
        value, unit = timeframeValue(timeframe)
        if unit == MINUTE:
            t = datetime(t0.year, t0.month, t0.day, t0.hour, (t0.minute // value) * value, tzinfo=timezone.utc)
            if t0 > t:
                t += timedelta(minutes=value)
        elif unit == HOUR:
            t = datetime(t0.year, t0.month, t0.day, (t0.hour // value) * value, tzinfo=timezone.utc)
            if t0 > t:
                t += timedelta(hours=value)
        elif unit == DAY:
            if value == 1:
                t = datetime(t0.year, t0.month, t0.day, tzinfo=timezone.utc)
            else:
                return None
        else:
            logger.warning('Error in roundTime()')
            return None
        return t

