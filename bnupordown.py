import websocket
import json
from autobn_realtime.dingding_robot import send_dingtalk_message

from my_loggers import upordown_logger
logger = upordown_logger.get_logger()
def on_message(ws, message):
    message = json.loads(message)
    # 检查是否为24小时价格统计数据
    if 'e' in message and message['e'] == '24hrTicker' and 'P' in message and 's' in message:
        coin = message['s']
        price_change_percent = float(message['P'])
        if price_change_percent <= -0.01:  # 检测是否下跌超过10%
            alert_message = f"警告！{coin} 24小时涨跌幅已达 {message['P']}%"
            send_dingtalk_message(alert_message)

        if price_change_percent <= -0.01:  # 检测是否下跌超过10%
            alert_message = f"警告！{coin} 24小时涨跌幅已达 {message['P']}%"
            logger.info(alert_message)

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")
    print("Close status code:", close_status_code)
    print("Close message:", close_msg)

def on_open(ws):
    # 订阅比特币和以太坊对美元的交易对
    ws.send(json.dumps({'method': 'SUBSCRIBE', 'params': ['btcusdt@ticker', 'ethusdt@ticker', 'pepeusdt@ticker', 'arkmusdt@ticker', 'wldusdt@ticker'], 'id': 1}))

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
