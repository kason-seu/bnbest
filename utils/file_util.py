import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import json

def save_data_to_json(today_midnight, symbol, data_list):
    # 创建文件夹
    today_str = today_midnight.strftime('%Y-%m-%d')
    folder_path = f"{today_str}"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # 保存数据到文本文件
    data_file_path = os.path.join(folder_path, f"{symbol}_price_change_data.json")
    with open(data_file_path, 'w') as file:
        json.dump(data_list, file, indent=4)

    print(f"Data saved to {data_file_path}")


def save_and_plot_image(today_midnight, times, percentage_changes, symbol):
    try:
        # 创建文件夹
        today_str = today_midnight.strftime('%Y-%m-%d')
        folder_path = f"{today_str}"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        plt.figure(figsize=(10, 6))

        # 将日期时间转换为Matplotlib理解的格式
        times = [mdates.date2num(time) for time in times]

        # 检查数据点的数量
        if len(times) > 1:
            plt.plot(times, percentage_changes, label=f"Price Change % of {symbol}")
        else:
            # 对于单个数据点，使用散点图
            plt.scatter(times, percentage_changes, label=f"Price Change % of {symbol}")

        plt.gcf().autofmt_xdate()
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

        if len(times) > 1:
            plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))

        plt.xlabel("Time")
        plt.ylabel("Percentage Change")
        plt.title(f"{symbol} Price Change Relative to Midnight")
        plt.legend()
        plt.grid(True)

        # 保存图像
        image_path = os.path.join(folder_path, f"{symbol}_price_change.png")
        plt.savefig(image_path)
        plt.close()
        print(f"Image saved to {image_path}")

    except Exception as e:
        print(f"An error occurred while saving or plotting the image: {e}")