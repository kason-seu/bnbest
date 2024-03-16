import requests
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import datetime

# 定义获取数据的函数
from matplotlib.dates import date2num


def fetch_data():
    url = "https://fapi.binance.com/futures/data/globalLongShortAccountRatio"
    params = {'symbol': 'BTCUSDT', 'period': '5m', 'limit': 1}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]['longShortRatio']  # 返回多空持仓金额比
    return None

# 初始化数据列表和图表
fig, ax = plt.subplots()
x_data, y_data = [], []
line, = plt.plot_date(x_data, y_data, '-')

# 更新函数，用于动态绘图
def update(frame):
    ratio = fetch_data()  # 确保这里成功获取到了数据
    print(ratio)
    if ratio:  # 检查ratio是否成功获取
        now = datetime.datetime.now()
        x_data.append(date2num(now))  # 使用date2num转换日期时间为数值
        y_data.append(ratio)  # 现在ratio已经被定义
        # 移除超出24小时的旧数据
        while x_data and (now - datetime.datetime.fromordinal(int(x_data[0]))).total_seconds() > 86400:
            x_data.pop(0)
            y_data.pop(0)
        line.set_data(x_data, y_data)
        ax.relim()
        ax.autoscale_view()
        fig.autofmt_xdate()  # 自动调整日期显示格式

        plt.draw()
    else:
        # 如果没有获取到ratio，可以在这里打印一条消息或进行其他处理
        print("Failed to fetch new data.")

# 修改FuncAnimation调用
ani = FuncAnimation(fig, update, interval=300000, cache_frame_data=False)  # 关闭帧数据缓存

plt.show()
