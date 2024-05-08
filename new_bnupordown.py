import websocket
import json
import concurrent.futures
import queue
import requests
import time
from threading import Lock, Thread
from my_loggers import upordown_logger
from collections import deque

logger = upordown_logger.get_logger()


def create_bounded_queue(maxsize):
    return queue.Queue(maxsize=maxsize)


def add_to_queue(q, item):
    try:
        q.put_nowait(item)  # 使用put_nowait来避免阻塞
    except queue.Full:
        logger.info(f"Queue is full, item discarded: {item}")


q = create_bounded_queue(15)


def add_to_bound_queue(item):
    try:
        q.put_nowait(item)  # 使用put_nowait来避免阻塞
    except queue.Full:
        logger.info(f"Queue is full, item discarded: {item}")


class RateLimiter:
    def __init__(self, max_calls, period):
        """
        :param max_calls: 允许的最大调用次数
        :param period: 时间窗口（秒）
        """
        self.max_calls = max_calls
        self.period = period
        self.timestamps = deque()

    def allow_call(self):
        """
        检查是否允许当前调用
        :return: True 如果允许, False 如果不允许
        """
        current_time = time.time()

        # 移除时间窗口之外的旧时间戳
        while self.timestamps and self.timestamps[0] < current_time - self.period:
            self.timestamps.popleft()

        if len(self.timestamps) < self.max_calls:
            self.timestamps.append(current_time)
            return True
        else:
            return False


webhook_url = "https://oapi.dingtalk.com/robot/send?access_token" \
              "=f4c5ef131c67548e699c5b2642503b4fcef14f3a23a032921e1ab32cfbbc5eb6 "


def send_dingtalk_message(q, limiter):
    while True:
        try:
            message = q.get(timeout=10)  # 10秒超时
            if message is None:
                time.sleep(1)  # 等待队列有元素
                continue  # 接收到None时，线程结束

            if limiter.allow_call():
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
            else:
                logger.info(f"达到限流器上限，Denied call at: {time.strftime('%X')}")
        except queue.Empty:
            logger.info("队列为空，等待消息。")
            time.sleep(1)  # 等待队列有元素


def on_message(ws, message):
    message = json.loads(message)

    if 'e' in message and message['e'] == '24hrTicker' and 'P' in message and 's' in message:
        coin = message['s']
        price_change_percent = float(message['P'])

        if price_change_percent <= -20:
            alert_message = f"下跌警告下跌超过20%！{coin} 24小时涨跌幅已达 {price_change_percent}%"
            logger.info(alert_message)
            add_to_bound_queue(alert_message)  # 将消息放入队列
        elif price_change_percent <= -17:
            alert_message = f"下跌警告下跌超过15%！{coin} 24小时涨跌幅已达 {price_change_percent}%"
            logger.info(alert_message)
            add_to_bound_queue(alert_message)  # 将消息放入队列
        elif price_change_percent <= -15:
            alert_message = f"下跌警告下跌超过10%！{coin} 24小时涨跌幅已达 {price_change_percent}%"
            logger.info(alert_message)
            add_to_bound_queue(alert_message)  # 将消息放入队列
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
            add_to_bound_queue(alert_message)  # 将消息放入队列
        elif price_change_percent >= 25:
            alert_message = f"很棒666,上涨超过25%！{coin} 24小时涨跌幅已达 {price_change_percent}%"
            logger.info(alert_message)
            add_to_bound_queue(alert_message)  # 将消息放入队列
        elif price_change_percent >= 30:
            alert_message = f"很棒666,上涨超过28%！{coin} 24小时涨跌幅已达 {price_change_percent}%"
            logger.info(alert_message)
            add_to_bound_queue(alert_message)  # 将消息放入队列
        elif price_change_percent >= 35:
            alert_message = f"很棒666,上涨超过30%！{coin} 24小时涨跌幅已达 {price_change_percent}%"
            logger.info(alert_message)
            add_to_bound_queue(alert_message)  # 将消息放入队列


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
                                   'fetusdt@ticker', 'flokiusdt@ticker', 'solusdt@ticker',
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
