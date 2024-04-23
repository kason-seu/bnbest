from datetime import datetime, timedelta


def is_between_8am_and_next_day_1230am():
    now = datetime.now()  # 获取当前时间
    start = now.replace(hour=8, minute=0, second=0, microsecond=0)  # 当天早上8点
    end = now.replace(hour=0, minute=30, second=0, microsecond=0) + timedelta(days=1)  # 下一天的凌晨0点30分

    # 检查当前时间是否在早上8点到下一天的午夜0点30分之间
    if start <= now < end:
        return True
    return False
