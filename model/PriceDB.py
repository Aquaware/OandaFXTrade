import logging
import threading
from sqlalchemy import Column, DateTime, Float, Integer, create_engine, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import IntegrityError
from contextlib import contextmanager

dbfile = './db/fxdata.sql'
Base = declarative_base()
engine = create_engine('sqlite:///' + dbfile, connect_args={"check_same_thread": False})
Session = scoped_session(sessionmaker(bind=engine))
lock = threading.Lock()

def TableClass(currency, timeframe):
    timeframe = timeframe.upper()
    if currency.lower() == 'usd_jpy':
        if timeframe == 'M1':
            return OandaUsdJpyM1
        elif timeframe == 'M5':
            return OandaUsdJpyM5
        elif timeframe == 'M10':
            return OandaUsdJpyM10
        elif timeframe == 'M15':
            return OandaUsdJpyM15
        elif timeframe == 'M30':
            return OandaUsdJpyM30
        elif timeframe == 'H1':
            return OandaUsdJpyH1
        elif timeframe == 'H2':
            return OandaUsdJpyH2
        elif timeframe == 'H4':
            return OandaUsdJpyH4
        elif timeframe == 'H8':
            return OandaUsdJpyH8
        elif timeframe == 'D1':
            return OandaUsdJpyD1

def TableClassWithTick(currency, timeframe, tick):
    cls = TableClass(currency, timeframe)
    t = tick.roundTime(timeframe)
    candle = cls.get(t)
    price = tick.mid_price
    if candle is None:
        cls.create(t, [price, price, price, price, tick.volume])
        return True

    if candle.high <= price:
        candle.high = price
    elif candle.low >= price:
        candle.low = price
    candle.volume += tick.volume
    candle.close = price
    candle.save()
    return False


@contextmanager
def session_scope():
    session = Session()
    try:
        lock.acquire()
        yield session
        session.commit()
    except Exception as e:
        logging.error(f'Error session_scope() {e}', e)
        session.rollback()
        raise
    finally:
        #session.close()
        lock.release()

class PriceDB(object):
    time = Column(DateTime, primary_key=True, nullable=False)
    open = Column(Float)
    close = Column(Float)
    high = Column(Float)
    low = Column(Float)
    volume = Column(Integer)

    @classmethod
    def create(cls, time, ohlcv):
        candle = cls(time=time,
                     open=ohlcv[0],
                     high=ohlcv[1],
                     low=ohlcv[2],
                     close=ohlcv[3],
                     volume=ohlcv[4])
        try:
            with session_scope() as session:
               session.add(candle)
            return candle
        except IntegrityError:
            return False

    @classmethod
    def get(cls, time):
        with session_scope() as session:
            candle = session.query(cls).filter(
                cls.time == time).first()
        if candle is None:
            return None
        return candle

    def save(self):
        with session_scope() as session:
            session.add(self)

    @classmethod
    def allCandles(cls, max_length=100):
        with session_scope() as session:
            candles = session.query(cls).order_by(desc(cls.time)).limit(max_length).all()
        candles.reverse()
        return candles

    @property
    def value(self):
        return {'time':self.time, 'open': self.open, 'high': self.high, 'low': self.low, 'close':self.close, 'volume': self.volume}

class OandaUsdJpyM1(PriceDB, Base):
    __tablename__ = 'USD_JPY_M1'

class OandaUsdJpyM5(PriceDB, Base):
    __tablename__ = 'USD_JPY_M5'

class OandaUsdJpyM10(PriceDB, Base):
    __tablename__ = 'USD_JPY_M10'

class OandaUsdJpyM15(PriceDB, Base):
    __tablename__ = 'USD_JPY_M15'

class OandaUsdJpyM30(PriceDB, Base):
    __tablename__ = 'USD_JPY_M30'

class OandaUsdJpyH1(PriceDB, Base):
    __tablename__ = 'USD_JPY_H1'

class OandaUsdJpyH2(PriceDB, Base):
    __tablename__ = 'USD_JPY_H2'

class OandaUsdJpyH4(PriceDB, Base):
    __tablename__ = 'USD_JPY_H4'

class OandaUsdJpyH8(PriceDB, Base):
    __tablename__ = 'USD_JPY_H8'

class OandaUsdJpyD1(PriceDB, Base):
    __tablename__ = 'USD_JPY_D1'

def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == '__main__':
    init_db()