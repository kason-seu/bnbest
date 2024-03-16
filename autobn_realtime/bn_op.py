from binance import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from my_loggers import binance_detail_logger
from my_loggers import binance_trade_logger
from my_loggers import binance_trade_condition_logger
import time
import math

detail_logger = binance_detail_logger.get_logger()
trade_logger = binance_trade_logger.get_logger()
trade_condition_logger = binance_trade_condition_logger.get_logger()


def buy_crypto_by_limit(client, symbol, quantity, price):
    try:
        # 获取服务器时间
        server_time = client.get_server_time()
        local_time = int(time.time() * 1000)
        time_diff = server_time['serverTime'] - local_time

        # 获取USDT余额
        usdt_balance = float(client.get_asset_balance(asset='USDT')['free'])
        trade_logger.info(f"USDT balance: {usdt_balance}")

        # 计算所需的USDT总量
        total_usdt_required = quantity * price

        # 判断条件：账户中的USDT余额是否足够
        if usdt_balance >= total_usdt_required:
            # 执行购买操作，使用调整后的时间戳
            params = {
                'symbol': symbol,
                'side': Client.SIDE_BUY,
                'type': Client.ORDER_TYPE_LIMIT,
                'timeInForce': Client.TIME_IN_FORCE_GTC,  # GTC - Good Till Cancel
                'quantity': quantity,
                'price': str(price),  # 价格需要转换为字符串
                'timestamp': int(time.time() * 1000) + time_diff
            }
            order = client.create_order(**params)
            trade_logger.info(f"Successfully placed a limit order: {order}")
        else:
            # 余额不足，记录日志
            trade_logger.warning(
                f"Insufficient USDT balance. Attempted to buy {symbol} but only have {usdt_balance} USDT.")
            print(f"Insufficient USDT balance to buy {symbol}.")

    except BinanceAPIException as api_error:
        trade_logger.error(f"Binance API Exception in buy_crypto: {api_error}")
        print(f"Binance API error occurred: {api_error}")
    except BinanceOrderException as order_error:
        trade_logger.error(f"Binance Order Exception in buy_crypto: {order_error}")
        print(f"Binance Order error occurred: {order_error}")
    except Exception as e:
        trade_logger.error(f"General error in buy_crypto: {e}")
        print(f"An error occurred: {e}")


def buy_crypto_by_market(client, symbol, amount_to_buy):
    try:
        # 获取服务器时间
        server_time = client.get_server_time()
        local_time = int(time.time() * 1000)
        time_diff = server_time['serverTime'] - local_time

        # 获取USDT余额
        usdt_balance = float(client.get_asset_balance(asset='USDT')['free'])
        trade_logger.info(f"USDT balance: {usdt_balance}")

        # 判断条件：账户中的USDT余额是否足够
        if usdt_balance >= amount_to_buy:
            # 执行购买操作，使用调整后的时间戳
            params = {
                'symbol': symbol,
                'side': Client.SIDE_BUY,
                'type': Client.ORDER_TYPE_MARKET,
                'quoteOrderQty': amount_to_buy,
                'timestamp': int(time.time() * 1000) + time_diff
            }
            order = client.create_order(**params)
            trade_logger.info(f"Successfully placed an order: {order}")
        else:
            # 余额不足，记录日志
            trade_logger.warning(
                f"Insufficient USDT balance. Attempted to buy {amount_to_buy} USDT worth of {symbol} but only have {usdt_balance} USDT.")
            print(f"Insufficient USDT balance to buy {symbol}.")

    except Exception as e:
        trade_logger.error(f"Error in buy_crypto: {e}")
        print(f"An error occurred: {e}")


def sell_crypto_by_limit(client, symbol, sell_ratio, sell_price):
    try:
        # 获取服务器时间
        server_time = client.get_server_time()
        local_time = int(time.time() * 1000)
        time_diff = server_time['serverTime'] - local_time

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
        trade_logger.info(f"{base_asset} 余额: {asset_balance} {base_asset}")

        # 计算要售卖的数量，并调整精度
        sell_amount = round(asset_balance * sell_ratio, step_size_precision)

        trade_logger.info(f"计划以 {sell_price} USDT的价格售卖: {sell_amount} {base_asset}")

        # 执行售卖操作，使用调整后的时间戳
        params = {
            'symbol': symbol,
            'side': Client.SIDE_SELL,
            'type': Client.ORDER_TYPE_LIMIT,
            'timeInForce': Client.TIME_IN_FORCE_GTC,  # 保证直到取消
            'quantity': sell_amount,
            'price': str(sell_price),
            'timestamp': int(time.time() * 1000) + time_diff
        }
        order = client.create_order(**params)
        trade_logger.info(f"Successfully placed a limit order: {order}")
        return order

    except BinanceAPIException as e:
        trade_logger.error(f"币安API异常: {e}")
        return None
    except Exception as e:
        trade_logger.error(f"执行交易过程中出现错误: {e}")
        return None


def sell_crypto_by_market(client, symbol, sell_ratio):
    try:
        # 获取服务器时间
        server_time = client.get_server_time()
        local_time = int(time.time() * 1000)
        time_diff = server_time['serverTime'] - local_time

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
        trade_logger.info(f"{base_asset} 余额: {asset_balance} {base_asset}")

        # 获取市场价格
        market_price = float(client.get_symbol_ticker(symbol=symbol)['price'])
        trade_logger.info(f"{symbol} 市场价格: {market_price} USDT")

        # 计算要售卖的数量，并调整精度
        sell_amount = round(asset_balance * sell_ratio, step_size_precision)
        sell_value = sell_amount * market_price
        trade_logger.info(f"计划售卖: {sell_amount} {base_asset}, 约合 {sell_value} USDT")

        # 执行售卖操作，使用调整后的时间戳
        params = {
            'symbol': symbol,
            'side': Client.SIDE_SELL,
            'type': Client.ORDER_TYPE_MARKET,
            'quantity': sell_amount,
            'timestamp': int(time.time() * 1000) + time_diff
        }
        order = client.create_order(**params)
        trade_logger.info(f"Successfully placed an order: {order}")
        return order

    except BinanceAPIException as e:
        trade_logger.error(f"币安API异常: {e}")
        return None
    except Exception as e:
        trade_logger.error(f"执行交易过程中出现错误: {e}")
        return None


def sell_crypto_by_usdt_market(client, symbol, usdt_amount):
    try:
        # 获取服务器时间
        server_time = client.get_server_time()
        local_time = int(time.time() * 1000)
        time_diff = server_time['serverTime'] - local_time

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
        trade_logger.info(f"{base_asset} 余额: {asset_balance} {base_asset}")

        # 获取市场价格
        market_price = float(client.get_symbol_ticker(symbol=symbol)['price'])
        trade_logger.info(f"{symbol} 市场价格: {market_price} USDT")

        # 计算可售卖的最大USDT值
        max_usdt_value = asset_balance * market_price

        if usdt_amount > max_usdt_value:
            trade_logger.info(f"请求售卖的USDT金额超过了可售卖的最大值。当前最大可售卖: {max_usdt_value} USDT")
            return None

        # 计算要售卖的币种数量，并调整精度
        sell_quantity = round(usdt_amount / market_price, step_size_precision)
        trade_logger.info(f"计划售卖: {usdt_amount} USDT, 约合 {sell_quantity} {base_asset}")

        # 执行售卖操作，使用调整后的时间戳
        params = {
            'symbol': symbol,
            'side': Client.SIDE_SELL,
            'type': Client.ORDER_TYPE_MARKET,
            'quantity': sell_quantity,
            'timestamp': int(time.time() * 1000) + time_diff
        }
        order = client.create_order(**params)
        trade_logger.info(f"Successfully placed an order: {order}")
        return order

    except BinanceAPIException as e:
        trade_logger.error(f"币安API异常: {e}")
        return None
    except Exception as e:
        trade_logger.error(f"执行交易过程中出现错误: {e}")
        return None


def sell_crypto_by_usdt_limit(client, symbol, usdt_amount, sell_price):
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
        trade_logger.info(f"{base_asset} 余额: {asset_balance}")

        # 计算要售卖的币种数量，并调整精度
        sell_quantity = round(usdt_amount / sell_price, step_size_precision)

        # 检查余额是否足够
        if sell_quantity > asset_balance:
            trade_logger.info(f"余额不足以售卖指定的USDT金额。")
            return None

        trade_logger.info(f"计划以 {sell_price} USDT的价格售卖: {sell_quantity} {base_asset}")

        # 执行售卖操作
        params = {
            'symbol': symbol,
            'side': Client.SIDE_SELL,
            'type': Client.ORDER_TYPE_LIMIT,
            'timeInForce': Client.TIME_IN_FORCE_GTC,  # 保证直到取消
            'quantity': sell_quantity,
            'price': str(sell_price)
        }
        order = client.create_order(**params)
        trade_logger.info(f"Successfully placed a limit order: {order}")
        return order

    except BinanceAPIException as e:
        trade_logger.error(f"币安API异常: {e}")
        return None
    except Exception as e:
        trade_logger.error(f"执行交易过程中出现错误: {e}")
        return None
