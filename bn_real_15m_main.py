import websocket
import json
from my_loggers import realtime_logger

from autobn_realtime.kline import KlineData
from autobn_realtime.mystrategy import k15m_strategy
logger = realtime_logger.get_logger()


def on_message(ws, message):
    #logger.info(f"Received Message:")
    message_json = json.loads(message)
    kline = message_json['k']

    kline_data = KlineData(
        event_type=message_json['e'],
        event_time=message_json['E'],
        symbol=message_json['s'],
        start_time=kline['t'],
        end_time=kline['T'],
        open_price=kline['o'],
        close_price=kline['c'],
        high_price=kline['h'],
        low_price=kline['l'],
        volume=kline['v'],
        number_of_trades=kline['n'],
        is_kline_closed=kline['x']
    )
    coin = kline_data.symbol
    logger.info(f"coin = {coin}, kline data = {kline_data}")
    print(f"coin = {coin}, kline data = {kline_data}")
    strategy = k15m_strategy.K15Strategy(kline_data)
    strategy.handle()

def on_error(ws, error):
    print("WebSocket Error:", error)


def on_close(ws, close_status_code, close_msg):
    logger.info(f"### closed ###")
    logger.info(f"Close status code: {close_status_code}")
    logger.info(f"Close message: {close_msg}")


def on_open(ws):
    logger.info(f"Opened connection")
    # 订阅BTC/USDT的1分钟K线数据
    param = {
        "method": "SUBSCRIBE",
        "params":
            [
                "ethusdt@kline_15m",
                "btcusdt@kline_15m",
                "pepeusdt@kline_15m",
                "flokiusdt@kline_15m",
                "wldusdt@kline_15m",
                "fetusdt@kline_15m",
                "arkmusdt@kline_15m"
            ],
        "id": 3
    }
    ws.send(json.dumps(param))


if __name__ == "__main__":
    #websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws/btcusdt@kline_15m",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
