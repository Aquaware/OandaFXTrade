import logging
from oandapyV20 import API
from oandapyV20.endpoints import accounts
from oandapyV20.endpoints.pricing import PricingInfo, PricingStream
from oandapyV20.exceptions import V20Error
from oandapyV20.endpoints import instruments, orders, trades
from model.Prices import Tick, Candle
import time

from datetime import datetime
import dateutil.parser

logger = logging.getLogger(__name__)

SHORT = 'short'
LONG = 'long'

CHECK_ORDER_TIMES = 60


class oandaClient(object):
    def __init__(self, account_id, access_key, enviroment='practice' ):
        self.account_id = account_id
        self.access_key = access_key
        self.client = API(access_token=access_key, environment=enviroment)

    def summary(self):
        req = accounts.AccountSummary(accountID=self.account_id)
        try:
            res = self.client.request(req)
        except V20Error as e:
            logger.error('in balance() ... {e}', e)
            return None
        return res

    def currentTick(self, currency):
        params = {'instruments': currency}
        req = PricingInfo(accountID=self.account_id, params=params)
        try:
            res = self.client.request(req)
            tick = Tick(None, None, None, None, None)
            tick.parse(res)
            tick.volume = self.currentVolume(currency)
        except V20Error as e:
            logger.error('in currentPrice() ... {e}', e)
            return None

    def currentVolume(self, currency):
        candles = self.candles(currency, 'M1', 1)
        if len(candles) == 1:
            return candles[0].volume
        else:
            return 0

    def candles(self, currency, timeframe, length):
        params = {'granularity': timeframe, 'count': length}
        req = instruments.InstrumentsCandles(instrument=currency, params=params)
        try:
            res = self.client.request(req)
            candles = Candle.parse(res)
            return candles
        except V20Error as e:
            logger.error('in candles() ... {e}', e)
            return None
        return res

    def streamTick(self, callback, currency):
        params = {'instruments': currency}
        req = PricingStream(accountID=self.account_id, params=params)
        try:
            for res in self.client.request(req):
                tick = Tick.parse(res)
                if tick is not None:
                    tick.volume = self.currentVolume(currency)
                    callback(tick)
                else:
                    print(res)
        except V20Error as e:
            logger.error('in candles() ... {e}', e)
        return

    def order(self, currency, units, side):
        if side == LONG:
            s = 1
        elif side == SHORT:
            s = -1
        else:
            return None
        order = {'type': 'MARKET', 'units':units * s, 'instrument': currency}
        param = {'order': order}
        req = orders.OrderCreate(accountID=self.account_id, data=param)
        try:
            res = self.client.request(req)
            logger.info(f'Response in order()... {res}', res)
        except V20Error as e:
            logger.error(f'Error in order() ... {e}', e)
            return None
        order_id = res['orderCreateTransaction']['id']

        for i in range(CHECK_ORDER_TIMES ):
            ret, state, filling_transaction_id = self.checkOrder(order_id)
            if ret:
                break
            time.sleep(1)

        if ret == False:
            logger.error(f'Error in order(), checkOrder ... Timeout')
            return None

        return self.position(filling_transaction_id)
        
    def checkOrder(self, order_id):
        req = orders.OrderDetails(accountID=self.account_id, orderID=order_id)
        try:
            res = self.client.request(req)
            logger.info(f'Response in checkOder()... {res}', res)
        except V20Error as e:
            logger.error(f'Error in checkOrder() ... {e}', e)
            return None

        state = res['order']['state']
        filling_transaction_id = res['order']['fillingTransactionID']
        if state == 'FILLED':
            r = True
        else:
            r = False
        return (r, state, filling_transaction_id)

    def position(self, trade_id):
        req = trades.TradeDetails(self.account_id, trade_id)
        try:
            res = self.client.request(req)
            logger.info(f'Response in position()... {res}', res)
            return res
        except V20Error as e:
            logger.error(f'Error in position() ... {e}', e)
            return None

    def closePosition(self, trade_id):
        req = trades.TradeClose(self.account_id, trade_id)
        try:
            res = self.client.request(req)
            logger.info(f'Response in closePosition()... {res}', res)
            return res
        except V20Error as e:
            logger.error(f'Error in closePosition() ... {e}', e)
            return None