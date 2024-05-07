import websocket
from my_loggers import k15_strategy_logger
from autobn_realtime.kline import KlineData
import json
import concurrent.futures
import queue
import time
from threading import Lock, Thread
import requests
from collections import deque
from utils import time_utils
logger = k15_strategy_logger.get_logger()


def create_bounded_queue(maxsize):
    return queue.Queue(maxsize=maxsize)


def add_to_queue(q, item):
    try:
        q.put_nowait(item)  # 使用put_nowait来避免阻塞
    except queue.Full:
        logger.info(f"Queue is full, item discarded: {item}")


q = create_bounded_queue(5)


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


def start_thread_pool(q):
    num_worker_threads = 1
    limiter = RateLimiter(5, 300)  # 20 calls per minute
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_worker_threads) as executor:
        for _ in range(num_worker_threads):
            executor.submit(send_dingtalk_message, q, limiter)


class K15Strategy:

    def __init__(self, kline_data):
        self.kline_data = kline_data
        self.coins = {}

    def handle(self):

        open_price = self.kline_data.open_price
        close_price = self.kline_data.close_price
        event_time = self.kline_data.event_time
        coin = self.kline_data.symbol

        lower_ratio = (close_price - open_price) / open_price
        upper_ratio = (close_price - open_price) / open_price
        lower_ratio_percentage = "{:.3%}".format(lower_ratio)
        upper_ratio_percentage = "{:.3%}".format(upper_ratio)

        logger.info(
            f"coin={coin}, real_time={event_time}, open_price={open_price}, close_price={close_price}, "
            f"upper_ratio={upper_ratio_percentage}, lower_ratio={lower_ratio_percentage}")

        if (open_price > close_price) and (lower_ratio < -0.05):
            logger.info(
                f"触发了下界条件是lower_ratio < -0.05,这是向下插强针了,启动购买操作,coin={coin}, real_time={event_time}, "
                f"lower_ratio={lower_ratio_percentage}, open_price={open_price}, close_price={close_price}")

            add_to_queue(q,
                         f"触发了下界条件是lower_ratio < -0.05,这是向下插强针了,启动购买操作,coin={coin}, real_time={event_time}, "
                         f"lower_ratio={lower_ratio_percentage}, open_price={open_price}, close_price={close_price}")

        if (open_price < close_price) and (upper_ratio > 0.05):
            logger.info(
                f"触发了上界条件是upper_ratio > 0.05,这是向上狂拉了,启动售卖操作,coin={coin}, real_time={event_time}, "
                f"upper_ratio={upper_ratio_percentage}, open_price={open_price}, close_price={close_price}")

            add_to_queue(q,
                         f"触发了上界条件是upper_ratio > 0.05,这是向上狂拉了,启动售卖操作,coin={coin}, real_time={event_time}, "
                         f"upper_ratio={upper_ratio_percentage}, open_price={open_price}, close_price={close_price}")

        if (open_price > close_price) and (lower_ratio < -0.035):
            logger.info(
                f"触发了下界条件是lower_ratio < -0.03,这是向下插强针了,启动购买操作,coin={coin}, real_time={event_time}, "
                f"lower_ratio={lower_ratio_percentage}, open_price={open_price}, close_price={close_price}")

            add_to_queue(q,
                         f"触发了下界条件是lower_ratio < -0.03,这是向下插强针了,启动购买操作,coin={coin}, real_time={event_time}, "
                         f"lower_ratio={lower_ratio_percentage}, open_price={open_price}, close_price={close_price}")

        if (open_price < close_price) and (upper_ratio > 0.035):
            logger.info(
                f"触发了上界条件是upper_ratio > 0.03,这是向上狂拉了,启动售卖操作,coin={coin}, real_time={event_time}, "
                f"upper_ratio={upper_ratio_percentage}, open_price={open_price}, close_price={close_price}")

            q.put(
                f"触发了上界条件是upper_ratio > 0.03,这是向上狂拉了,启动售卖操作,coin={coin}, real_time={event_time}, "
                f"upper_ratio={upper_ratio_percentage}, open_price={open_price}, close_price={close_price}")

        if (open_price > close_price) and (lower_ratio < -0.018):
            if time_utils.is_between_8am_and_next_day_1230am():
                logger.info(
                    f"触发了下界条件是lower_ratio < -0.011,这是向下插强针了,启动购买操作,coin={coin}, real_time={event_time}, "
                    f"lower_ratio={lower_ratio_percentage}, open_price={open_price}, close_price={close_price}")

                add_to_queue(q,
                             f"触发了下界条件是lower_ratio < -0.01,这是向下插强针了,启动购买操作,coin={coin}, real_time={event_time}, "
                             f"lower_ratio={lower_ratio_percentage}, open_price={open_price}, close_price={close_price}")

        if (open_price < close_price) and (upper_ratio > 0.018):
            if time_utils.is_between_8am_and_next_day_1230am():
                logger.info(
                    f"触发了上界条件是upper_ratio > 0.011,这是向上狂拉了,启动售卖操作,coin={coin}, real_time={event_time}, "
                    f"upper_ratio={upper_ratio_percentage}, open_price={open_price}, close_price={close_price}")

                q.put(
                    f"触发了上界条件是upper_ratio > 0.01,这是向上狂拉了,启动售卖操作,coin={coin}, real_time={event_time}, "
                    f"upper_ratio={upper_ratio_percentage}, open_price={open_price}, close_price={close_price}")

        if (open_price > close_price) and (lower_ratio < -0.08):
            logger.info(
                f"触发了下界条件是lower_ratio < -0.08,这是向下插强针了,启动购买操作,coin={coin}, real_time={event_time}, "
                f"lower_ratio={lower_ratio_percentage}, open_price={open_price}, close_price={close_price}")
            add_to_queue(q,
                         f"触发了下界条件是lower_ratio < -0.08,这是向下插强针了,启动购买操作,coin={coin}, real_time={event_time}, "
                         f"lower_ratio={lower_ratio_percentage}, open_price={open_price}, close_price={close_price}")

        if (open_price < close_price) and (upper_ratio > 0.08):
            logger.info(
                f"触发了上界条件是upper_ratio > 0.08,这是向上狂拉了,启动售卖操作,coin={coin}, real_time={event_time}, "
                f"upper_ratio={upper_ratio_percentage}, open_price={open_price}, close_price={close_price}")
            add_to_queue(q,
                         f"触发了上界条件是upper_ratio > 0.08,这是向上狂拉了,启动售卖操作,coin={coin}, real_time={event_time}, "
                         f"upper_ratio={upper_ratio_percentage}, open_price={open_price}, close_price={close_price}")


def on_message(ws, message):
    # logger.info(f"Received Message:")
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
    strategy = K15Strategy(kline_data)
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
                "arkmusdt@kline_15m",
                "solusdt@kline_15m"
            ],
        "id": 3
    }
    ws.send(json.dumps(param))


if __name__ == "__main__":
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws/btcusdt@kline_15m",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    # Use a separate thread to run the WebSocket client to avoid blocking the main thread
    thread = Thread(target=lambda: ws.run_forever())
    thread.start()
    start_thread_pool(q)  # 启动线程池
    thread.join()  # 等待WebSocket线程结束
