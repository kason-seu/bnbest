import websocket
import json
import concurrent.futures
import queue
import requests
import time
from threading import Lock, Thread
from my_loggers import upordown_logger

logger = upordown_logger.get_logger()
q = queue.Queue()


class RateLimiter:
    def __init__(self, max_calls, period):
        self.calls = max_calls
        self.period = period
        self.mtx = Lock()
        self.timestamps = []

    def wait(self):
        with self.mtx:
            current_time = time.time()
            # 清理超出时间窗口的时间戳
            self.timestamps = [t for t in self.timestamps if current_time - t < self.period]

            if len(self.timestamps) >= self.calls:
                earliest = self.timestamps[0]
                sleep_time = self.period - (current_time - earliest)
                #print(f"RateLimiter: Waiting for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)

            self.timestamps.append(time.time())  # 添加新的时间戳


webhook_url = "https://oapi.dingtalk.com/robot/send?access_token" \
              "=f4c5ef131c67548e699c5b2642503b4fcef14f3a23a032921e1ab32cfbbc5eb6 "


def send_dingtalk_message(q, limiter):
    while True:
        message = q.get()
        if message is None:
            break  # 接收到None时，线程结束

        limiter.wait()  # 等待符合频率限制

        headers = {"Content-Type": "application/json; charset=utf-8"}
        data = {
            "msgtype": "text",
            "text": {
                "content": "autobn---" + message  # 消息内容
            },
            "at": {
                "isAtAll": False
            }
        }
        response = requests.post(webhook_url, data=json.dumps(data), headers=headers)
        logger.info(f"钉钉通知发送状态：{response.text}")
        q.task_done()


def on_message(ws, message):
    message = json.loads(message)

    if 'e' in message and message['e'] == '24hrTicker' and 'P' in message and 's' in message:
        coin = message['s']
        price_change_percent = float(message['P'])

        if price_change_percent <= -20:
            alert_message = f"下跌警告下跌超过20%！{coin} 24小时涨跌幅已达 {price_change_percent}%"
            logger.info(alert_message)
            q.put(alert_message)  # 将消息放入队列
        elif price_change_percent <= -12:
            alert_message = f"下跌警告下跌超过12%！{coin} 24小时涨跌幅已达 {price_change_percent}%"
            logger.info(alert_message)
            q.put(alert_message)  # 将消息放入队列
        # elif price_change_percent <= -10:
        #     alert_message = f"下跌警告下跌超过20%！{coin} 24小时涨跌幅已达 {price_change_percent}%"
        #     logger.info(alert_message)
        #     q.put(alert_message)  # 将消息放入队列
        # elif price_change_percent <= -7:
        #     alert_message = f"下跌警告下跌超过7%！{coin} 24小时涨跌幅已达 {price_change_percent}%"
        #     logger.info(alert_message)
        #     q.put(alert_message)  # 将消息放入队列
        elif price_change_percent >= 20:
            alert_message = f"很棒666,上涨超过20%！{coin} 24小时涨跌幅已达 {price_change_percent}%"
            logger.info(alert_message)
            q.put(alert_message)  # 将消息放入队列
        elif price_change_percent >= 22:
            alert_message = f"很棒666,上涨超过15%！{coin} 24小时涨跌幅已达 {price_change_percent}%"
            logger.info(alert_message)
            q.put(alert_message)  # 将消息放入队列


def start_thread_pool(q):
    num_worker_threads = 1
    limiter = RateLimiter(15, 300)  # 20 calls per minute
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_worker_threads) as executor:
        for _ in range(num_worker_threads):
            executor.submit(send_dingtalk_message, q, limiter)


def on_error(ws, error):
    logger.error(f"Error: {error}")


def on_close(ws, close_status_code, close_msg):
    logger.info("### closed ###")
    logger.info(f"Close status code: {close_status_code}")
    logger.info(f"Close message: {close_msg}")


def on_open(ws):
    logger.info("WebSocket connection opened.")
    # 订阅多个交易对
    ws.send(json.dumps({'method': 'SUBSCRIBE',
                        'params': ['btcusdt@ticker', 'ethusdt@ticker', 'pepeusdt@ticker', 'arkmusdt@ticker',
                                   'wldusdt@ticker'], 'id': 111}))


if __name__ == "__main__":
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    # Use a separate thread to run the WebSocket client to avoid blocking the main thread
    thread = Thread(target=lambda: ws.run_forever())
    thread.start()
    start_thread_pool(q)  # 启动线程池
    thread.join()  # 等待WebSocket线程结束
