from binance.client import Client
import time
from coin_core import binance_data_operator
from coin_core import binance_client
import schedule
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from my_loggers import main_logger
from coin_core import trade_count
from utils import config_parser
from coin_core.binance_operator import CryptoTrader

config_parser = config_parser.ConfigParser()
client = binance_client.get_binance_client(**config_parser.get("binance"))
logger = main_logger.get_logger()


def binance_start():
    # 获取BTC/USDT的最新价格 2. 获取市场数据
    btc_price = client.get_symbol_ticker(symbol="BTCUSDT")
    print("BTC Price: ", btc_price)
    # 获取账户信息 3. 查看账户余额
    # 获取币安服务器时间并计算时间差
    server_time = client.get_server_time()
    time_diff = server_time['serverTime'] - int(time.time() * 1000)

    # 当您需要发送请求时（例如，获取账户信息），使用调整后的时间戳
    params = {
        'timestamp': int(time.time() * 1000) + time_diff,
        'recvWindow': 60000  # 增加到60000毫秒
    }
    account = client.get_account(**params)
    print(account)

    binance_data_operator.plot_save_fetch_data("BTCUSDT", Client.KLINE_INTERVAL_5MINUTE, "1 day ago UTC", client,
                                               today_midnight=None)


def fetch(**kwargs):

    trade_counter = kwargs['trade_counter']
    symbol = kwargs['symbol']
    logger.info(f"{datetime.now()}: 获取{symbol}的数据")
    # 获取特定币种的一天的K线数据

    binance_operator = kwargs['binance_operator']
    data = binance_operator.plot_save_fetch_data(symbol, Client.KLINE_INTERVAL_5MINUTE, "1 day ago UTC",
                                                      today_midnight=None, trade_counter=trade_counter)
    # data = binance_data_operator.plot_save_fetch_data(symbol, Client.KLINE_INTERVAL_5MINUTE, "1 day ago UTC", client,
    #                                                   today_midnight=None, buy_counter=buy_counter)
    return data


def analyze_trend(data):
    if len(data) < 2:
        print("没有足够的数据来分析趋势。")
        return

    # 使用简单的逻辑比较首尾K线的收盘价格来判断趋势
    first_close = float(data[0][4])
    last_close = float(data[-1][4])

    if last_close > first_close:
        return f"上涨趋势。首尾价格差：{last_close - first_close}"
    else:
        return f"下降趋势。首尾价格差：{last_close - first_close}"


def fetch_and_analyze(**kwargs):

    symbol = kwargs['symbol']
    data = fetch(**kwargs)
    trend = analyze_trend(data)
    logger.info(f"{datetime.now()}: {symbol} - {trend}")


def analysis_and_trade_job(*args, **kwargs):
    symbols_config = kwargs['symbols_config']

    symbols_configs = symbols_config.get('coin_symbols')
    symbols_configs_list = symbols_configs.split(',')
    logger.info(f'monitor and analysis symbols {symbols_configs_list}')
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_and_analyze, symbol=symbol, symbols_configs_list = symbols_configs_list, **kwargs) for symbol in
                   symbols_configs_list]  # 示例：分析BTC和ETH
        for future in futures:
            print(future.result())


if __name__ == '__main__':
    # binance_start()
    symbols_config = config_parser.get("symbols")
    buy_rate_below_condition = config_parser.get("buy_rate_below_condition")
    buy_limits_config = config_parser.get("buy_limits")

    sell_limits = config_parser.get("sell_limits")
    sell_rate_condition = config_parser.get("sell_rate_condition")

    trade_counter = trade_count.TradeCounter(buy_limits_config, sell_limits)
    binance_operator = CryptoTrader(client = client, buy_rate_below_condition = buy_rate_below_condition, sell_rate_condition = sell_rate_condition)
    analysis_and_trade_job(symbols_config = symbols_config, trade_counter = trade_counter, binance_operator = binance_operator)

    # 无限循环，以运行定时任务
    # 定时任务设置：每5分钟执行一次
    schedule.every(5).minutes.do(lambda: analysis_and_trade_job(symbols_config=symbols_config, trade_counter=trade_counter, binance_operator = binance_operator))
    while True:
        schedule.run_pending()
        time.sleep(10)
