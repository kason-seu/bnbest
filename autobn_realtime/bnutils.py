from datetime import datetime


def time_int_str(timestamp_ms) -> str:

    # 将毫秒转换为秒
    timestamp = timestamp_ms / 1000

    # 将时间戳转换为datetime对象
    datetime_obj = datetime.fromtimestamp(timestamp)

    # 将datetime对象格式化为指定的格式
    formatted_time = datetime_obj.strftime('%d.%m.%Y %H:%M:%S')

    return formatted_time


def get_quantity(price, total):
    return  total/price