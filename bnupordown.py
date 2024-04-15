import websocket
import json

def on_message(ws, message):
    message = json.loads(message)
    # 检查是否为24小时价格统计数据
    if 'e' in message and message['e'] == '24hrTicker':
        print(f"{message['s']} 24小时涨跌幅: {message['P']}%")

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")
    print("Close status code:", close_status_code)
    print("Close message:", close_msg)

def on_open(ws):
    # 订阅比特币和以太坊对美元的交易对
    ws.send(json.dumps({'method': 'SUBSCRIBE', 'params': ['btcusdt@ticker', 'ethusdt@ticker'], 'id': 1}))

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
