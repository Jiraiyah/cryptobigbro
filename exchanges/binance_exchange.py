from binance.client import Client as BinanceClient
import pandas as pd
from datetime import datetime, timezone

from utils import candle_list_to_dataframe, timedelta

class BinanceExchange:
    def __init__(self):
        self._client = BinanceClient("", "")
        self._limit = 1000
    
    def fetch_ohlcv(self, timeframe, since, instrument):
        # Binance include the current (and unfinished) bar in the fetched data, we need to compute endTime to remove it
        n = datetime.now(timezone.utc)
        if timeframe == BinanceClient.KLINE_INTERVAL_1MONTH:
            # Special case for month because it has not fixed timedelta
            endTime = datetime(n.year, n.month, 1) - timedelta('1s')
        else:
            td = timedelta(timeframe)
            start_of_current_bar = int(n.timestamp() / td.total_seconds()) * td.total_seconds()
            endTime = datetime.fromtimestamp(start_of_current_bar, timezone.utc) - timedelta('1s')

        result = self._client.get_klines(
            symbol=instrument,
            interval=timeframe,
            limit=self._limit,
            startTime=int(since.timestamp() * 1000), # Binance wants timestamp in milliseconds,
            endTime=int(endTime.timestamp() * 1000)
        )

        candles = [
            {
                "open_datetime_utc": datetime.fromtimestamp(int(data[0] / 1000), timezone.utc),
                "close_datetime_utc":datetime.fromtimestamp(int(data[6] / 1000), timezone.utc),
                "open": data[1],
                "high":data[2],
                "low":data[3],
                "close":data[4],
                "volume": data[5],
                "quote_volume": data[7],
                "trade_count": data[8]
            } for data in result
        ]

        return candle_list_to_dataframe(candles)
    
    def get_timeframes(self):
        return [
            BinanceClient.KLINE_INTERVAL_1MONTH,
            BinanceClient.KLINE_INTERVAL_1WEEK,
            BinanceClient.KLINE_INTERVAL_3DAY,
            BinanceClient.KLINE_INTERVAL_1DAY,
            BinanceClient.KLINE_INTERVAL_12HOUR,
            BinanceClient.KLINE_INTERVAL_8HOUR,
            BinanceClient.KLINE_INTERVAL_6HOUR,
            BinanceClient.KLINE_INTERVAL_4HOUR,
            BinanceClient.KLINE_INTERVAL_2HOUR,
            BinanceClient.KLINE_INTERVAL_1HOUR,
            BinanceClient.KLINE_INTERVAL_30MINUTE,
            BinanceClient.KLINE_INTERVAL_15MINUTE,
            BinanceClient.KLINE_INTERVAL_5MINUTE,
            BinanceClient.KLINE_INTERVAL_3MINUTE,
            BinanceClient.KLINE_INTERVAL_1MINUTE
        ]
    
    def get_instruments(self):
        return [ 
            _["symbol"] for _ in self._client.get_products()["data"] 
        ]