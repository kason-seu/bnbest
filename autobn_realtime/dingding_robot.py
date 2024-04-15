import requests
import json


# 钉钉机器人的Webhook URL
webhook_url = "https://oapi.dingtalk.com/robot/send?access_token=f4c5ef131c67548e699c5b2642503b4fcef14f3a23a032921e1ab32cfbbc5eb6"

@sleep_and_retry
@limits(calls=20, period=60)
def send_dingtalk_message(webhook_url = webhook_url, message=None):
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

