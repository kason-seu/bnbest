from datetime import datetime

from binance import Client
from binance.exceptions import BinanceAPIException

from utils import file_util
from my_loggers import binance_detail_logger
from my_loggers import binance_trade_logger
import math


def plot_save_fetch_data(symbol, interval, lookback, client, today_midnight, buy_counter=None):
    logger = binance_detail_logger.get_logger()
    # 获取历史K线数据
    candles = client.get_historical_klines(symbol, interval, lookback, limit=1000)

    # 初始化数据列表
    times = []
    percentage_changes = []
    midnight_price = None
    midnight_time = None
    data_list = []
    percentage_change = None

    # 当前日期的凌晨时间
    if today_midnight is None:
        today_midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    # 处理数据
    for candle in candles:
        open_time = datetime.fromtimestamp(candle[0] / 1000)
        # 只保留属于当前日期的数据
        if open_time < today_midnight:
            continue
        open_price = float(candle[1])
        close_price = float(candle[4])

        if midnight_price is None:
            midnight_price = open_price

        if midnight_time is None:
            midnight_time = open_time

        percentage_change = ((close_price - midnight_price) / midnight_price) * 100
        times.append(open_time)
        percentage_changes.append(percentage_change)
        # print(f"开盘时间: {open_time}, 开盘价: {open_price}, 当前价: {close_price}, 变化比例: {percentage_change} '")
        logger.info(
            "币种:{}, 开盘时间: {}, 开盘价: {}, 当前价: {}, 变化比例: {:.2f}%".format(symbol, open_time, midnight_price, close_price,
                                                                      percentage_change))
        # 添加JSON对象到数据列表
        data_list.append({
            "open_time": open_time.strftime('%Y-%m-%d %H:%M:%S'),
            "percentage_change": round(percentage_change, 2)
        })

    logger.info(f'check condition, whether should we start to buy percentage_change={percentage_change}, symbol={symbol}')
    #if percentage_change < -2 and (symbol == 'ETHUSDT' or symbol == 'BTCUSDT' or symbol == 'BNBUSDT'):
    if (symbol == 'ETHUSDT' or symbol == 'BTCUSDT' or symbol == 'BNBUSDT'):
        canBuy = buy_counter.buy_increment(symbol)
        if canBuy:
            logger.info(f"match rule, ready to buy{symbol}")
            #buy_crypto(symbol, 50, client)

    #if percentage_change < -5 and (symbol == 'PEPEUSDT'):
    if (symbol == 'PEPEUSDT'):
        canBuy = buy_counter.buy_increment(symbol)
        if canBuy:
            logger.info(f"match rule, ready to buy{symbol}")
            #buy_crypto(symbol, 50, client)


    # 绘制曲线图
    file_util.save_and_plot_image(today_midnight, times, percentage_changes, symbol=symbol)
    file_util.save_data_to_json(today_midnight, symbol, data_list)
    return candles


def buy_crypto(symbol, amount_to_buy, client):
    # 设置日志
    # logging.basicConfig(filename='buy_crypto.log', level=logging.INFO,
    #                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = binance_trade_logger.get_logger()
    try:
        # 获取USDT余额
        usdt_balance = float(client.get_asset_balance(asset='USDT')['free'])
        logger.info(f"USDT balance: {usdt_balance}")

        # 判断条件：账户中的USDT余额是否足够
        if usdt_balance >= amount_to_buy:
            # 执行购买操作
            order = client.create_order(
                symbol=symbol,
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_MARKET,
                quoteOrderQty=amount_to_buy
            )
            logger.info(f"Successfully placed an order: {order}")
        else:
            # 余额不足，记录日志
            logger.warning(
                f"Insufficient USDT balance. Attempted to buy {amount_to_buy} USDT worth of {symbol} but only have {usdt_balance} USDT.")
            print(f"Insufficient USDT balance to buy {symbol}.")

    except Exception as e:
        logger.error(f"Error in buy_crypto: {e}")
        print(f"An error occurred: {e}")


def sell_crypto(symbol, sell_ratio, client):
    logger = binance_trade_logger.get_logger()

    try:
        # 获取交易对信息
        info = client.get_symbol_info(symbol)
        step_size = 0.0
        for f in info['filters']:
            if f['filterType'] == 'LOT_SIZE':
                step_size = float(f['stepSize'])
                break

        # 计算step_size的精度
        step_size_precision = int(round(-math.log(step_size, 10), 0))

        # 获取要售卖的币种名称（如BTC）
        base_asset = symbol[:-4]

        # 查询账户余额
        asset_balance = float(client.get_asset_balance(asset=base_asset)['free'])
        logger.info(f"{base_asset} 余额: {asset_balance} {base_asset}")

        # 获取市场价格
        market_price = float(client.get_symbol_ticker(symbol=symbol)['price'])
        logger.info(f"{symbol} 市场价格: {market_price} USDT")

        # 计算要售卖的数量，并调整精度
        sell_amount = round(asset_balance * sell_ratio, step_size_precision)
        sell_value = sell_amount * market_price
        logger.info(f"计划售卖: {sell_amount} {base_asset}, 约合 {sell_value} USDT")

        # 执行售卖操作
        order = client.create_order(
            symbol=symbol,
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,
            quantity=sell_amount
        )
        logger.info(f"Successfully placed an order: {order}")
        return order

    except BinanceAPIException as e:
        logger.error(f"币安API异常: {e}")
        return None
    except Exception as e:
        logger.error(f"执行交易过程中出现错误: {e}")
        return None


def sell_crypto_by_usdt(symbol, usdt_amount, client):
    logger = binance_trade_logger.get_logger()

    try:
        # 获取要售卖的币种名称（如BTC）
        base_asset = symbol[:-4]

        # 获取交易对信息
        info = client.get_symbol_info(symbol)
        step_size = 0.0
        for f in info['filters']:
            if f['filterType'] == 'LOT_SIZE':
                step_size = float(f['stepSize'])
                break

        # 计算step_size的精度
        step_size_precision = int(round(-math.log(step_size, 10), 0))

        # 查询账户余额
        asset_balance = float(client.get_asset_balance(asset=base_asset)['free'])
        logger.info(f"{base_asset} 余额: {asset_balance} {base_asset}")

        # 获取市场价格
        market_price = float(client.get_symbol_ticker(symbol=symbol)['price'])
        logger.info(f"{symbol} 市场价格: {market_price} USDT")

        # 计算可售卖的最大USDT值
        max_usdt_value = asset_balance * market_price

        if usdt_amount > max_usdt_value:
            logger.info(f"请求售卖的USDT金额超过了可售卖的最大值。当前最大可售卖: {max_usdt_value} USDT")
            return None

        # 计算要售卖的币种数量，并调整精度
        sell_quantity = round(usdt_amount / market_price, step_size_precision)
        logger.info(f"计划售卖: {usdt_amount} USDT, 约合 {sell_quantity} {base_asset}")

        # 执行售卖操作
        order = client.create_order(
            symbol=symbol,
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,
            quantity=sell_quantity
        )
        logger.info(f"Successfully placed an order: {order}")
        return order

    except BinanceAPIException as e:
        logger.error(f"币安API异常: {e}")
        return None
    except Exception as e:
        logger.error(f"执行交易过程中出现错误: {e}")
        return None

# 使用示例
# plot_price_change("BTCUSDT", Client.KLINE_INTERVAL_5MINUTE, "1 day ago UTC")

# 购买例子
# buy_crypto(api_key, api_secret, 'BTCUSDT', 100)  # 尝试用100 USDT购买BTC


# 售卖例子
# order = sell_crypto(api_key, api_secret, 'BTCUSDT', 0.5)  # 尝试售卖50%的BTC
# order = sell_crypto_by_usdt(api_key, api_secret, 'BTCUSDT', 100)  # 尝试售卖100 USDT等值的BTC
