import requests
import json

import time
from threading import Lock


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
                time.sleep(sleep_time)

            self.timestamps.append(time.time())  # 添加新的时间戳

# 初始化一个 RateLimiter 对象，每分钟最多10次调用
limiter = RateLimiter(max_calls=5, period=300)

# 钉钉机器人的Webhook URL
webhook_url = "https://oapi.dingtalk.com/robot/send?access_token=f4c5ef131c67548e699c5b2642503b4fcef14f3a23a032921e1ab32cfbbc5eb6"


def send_dingtalk_message(webhook_url = webhook_url, message=None):
    # 等待如果当前的调用频率超过了限制
    limiter.wait()
    # 构造请求数据
    headers = {"Content-Type": "application/json ;charset=utf-8"}
    data = {
        "msgtype": "text",  # 消息类型，此处为文本
        "text": {
            "content": "autobn---" + message  # 消息内容
        },
        "at": {
            "isAtAll": False  # 是否@所有人
        }
    }

    # 发送POST请求
    response = requests.post(webhook_url, data=json.dumps(data), headers=headers)
    # 打印响应结果
    print(response.text)

