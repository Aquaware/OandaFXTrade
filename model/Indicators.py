import numpy as np

import logging
logger = logging.getLogger(__name__)




# ------

class Indicators(object):

    def __init__(self, candles):
        self.candles = candles
        closes = []
        for candle in self.candles:
            closes.append(candle.close)
        self.closes = closes
        self.length = len(closes)

    def sma(self, window):
        out = np.full(self.length, 0.0)
        if self.length < window:
            return out.tolist()
        for i in range(window - 1, len(self.closes)):
            d = self.closes[i - window + 1: i]
            out[i] = np.nanmean(d)
        return out.tolist()

