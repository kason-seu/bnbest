from datetime import datetime
from binance import Client
from binance.exceptions import BinanceAPIException
from utils import file_util
from my_loggers import binance_detail_logger
from my_loggers import binance_trade_logger
from my_loggers import binance_trade_condition_logger
import time
import math

class CryptoTraderSeller:
    def __init__(self, **kwargs):
        self.client = kwargs['client']
        # 配置文件里面都是字符串，我们需要把它变成数字
        self.buy_rate_below_condition = {key: float(kwargs['sell_rate_condition'][key]) for key in kwargs['sell_rate_condition']}
        self.detail_logger = binance_detail_logger.get_logger()
        self.trade_logger = binance_trade_logger.get_logger()
        self.trade_condition_logger = binance_trade_condition_logger.get_logger()


class CryptoTrader:
    def __init__(self, **kwargs):
        self.client = kwargs['client']
        # 配置文件里面都是字符串，我们需要把它变成数字
        self.buy_rate_below_condition = {key: float(kwargs['buy_rate_below_condition'][key]) for key in kwargs['buy_rate_below_condition']}
        self.sell_rate_condition = {key: float(kwargs['sell_rate_condition'][key]) for key in kwargs['sell_rate_condition']}
        self.detail_logger = binance_detail_logger.get_logger()
        self.trade_logger = binance_trade_logger.get_logger()
        self.trade_condition_logger = binance_trade_condition_logger.get_logger()


    def plot_save_fetch_data(self, symbol, interval, lookback, today_midnight=None, trade_counter=None):
        #logger = binance_detail_logger.get_logger()
        # 获取历史K线数据
        candles = self.client.get_historical_klines(symbol, interval, lookback, limit=500)

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
            self.detail_logger.info(
                "币种:{}, 开盘时间: {}, 开盘价: {}, 当前价: {}, 变化比例: {:.2f}%".format(symbol, open_time, midnight_price,
                                                                          close_price,
                                                                          percentage_change))
            # 添加JSON对象到数据列表
            data_list.append({
                "open_time": open_time.strftime('%Y-%m-%d %H:%M:%S'),
                "percentage_change": round(percentage_change, 2)
            })

        self.trade_condition_logger.info(
            f'check condition, whether should we start to buy percentage_change={percentage_change}, symbol={symbol}')
        # if percentage_change < -2 and (symbol == 'ETHUSDT' or symbol == 'BTCUSDT' or symbol == 'BNBUSDT'):
        buy_below_limit = self.buy_rate_below_condition[symbol]
        sell_below_limit = self.sell_rate_condition[symbol]
        self.trade_condition_logger.info(f'symbol = {symbol}, buy conditiion = {buy_below_limit}， sell condition= {sell_below_limit}')
        if (symbol == 'ETHUSDT' or symbol == 'BTCUSDT' or symbol == 'BNBUSDT'):
            if percentage_change < buy_below_limit:
                canBuy = trade_counter.buy_increment(symbol)
                if canBuy:
                    lock = trade_counter.acquire_buyer_lock()
                    with lock:
                        self.trade_condition_logger.info(f"获取锁,match rule, ready to buy {symbol}")
                        #self.buy_crypto(symbol, 50)
                        self.trade_condition_logger.info(f"购买{symbol}完毕,释放锁")
                        # 调整下一次的condition，需要翻倍才会执行购买
                        self.buy_rate_below_condition[symbol] = self.buy_rate_below_condition[symbol] * 2

            if percentage_change > sell_below_limit:
                self.trade_condition_logger.info(f"{symbol}满足售卖的基础条件{sell_below_limit},current{percentage_change}，开始执行判断，是否达到售卖的线")
                canSell = trade_counter.sell_increment(symbol)
                if canSell:
                    lock = trade_counter.acquire_buyer_lock()
                    with lock:
                        self.trade_condition_logger.info(f"获取锁,match rule, ready to sell {symbol}")
                        #self.sell_crypto_by_usdt(symbol, 100)
                        self.trade_condition_logger.info(f"售卖{symbol}完毕,释放锁")
                        # 调整下一次的condition，需要翻倍才会执行购买
                        self.sell_rate_condition[symbol] = self.sell_rate_condition[symbol] + 2

        if (symbol == 'PEPEUSDT'):
            if percentage_change < buy_below_limit:
                canBuy = trade_counter.buy_increment(symbol)
                if canBuy:
                    lock = trade_counter.acquire_buyer_lock()
                    with lock:
                        self.trade_condition_logger.info(f"获取锁,match rule, ready to buy{symbol}")
                        #self.buy_crypto(symbol, 50)
                        self.trade_condition_logger.info(f"购买{symbol}完毕,释放锁")
                        self.buy_rate_below_condition[symbol] = self.buy_rate_below_condition[symbol]-2
            if percentage_change > sell_below_limit:
                self.trade_condition_logger.info(f"{symbol}满足售卖的基础条件{sell_below_limit},current{percentage_change}，开始执行判断，是否达到售卖的线")
                canSell = trade_counter.sell_increment(symbol)
                if canSell:
                    lock = trade_counter.acquire_buyer_lock()
                    with lock:
                        self.trade_condition_logger.info(f"获取锁,match rule, ready to sell {symbol}")
                        #self.sell_crypto_by_usdt(symbol, 100)
                        self.trade_condition_logger.info(f"售卖{symbol}完毕,释放锁")
                        # 调整下一次的condition，需要翻倍才会执行购买
                        self.sell_rate_condition[symbol] = self.sell_rate_condition[symbol] + 2
        # 绘制曲线图
        file_util.save_and_plot_image(today_midnight, times, percentage_changes, symbol=symbol)
        file_util.save_data_to_json(today_midnight, symbol, data_list)
        return candles

    def buy_crypto(self, symbol, amount_to_buy):
        try:
            # 获取服务器时间
            server_time = self.client.get_server_time()
            local_time = int(time.time() * 1000)
            time_diff = server_time['serverTime'] - local_time

            # 获取USDT余额
            usdt_balance = float(self.client.get_asset_balance(asset='USDT')['free'])
            self.trade_logger.info(f"USDT balance: {usdt_balance}")

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
                order = self.client.create_order(**params)
                self.trade_logger.info(f"Successfully placed an order: {order}")
            else:
                # 余额不足，记录日志
                self.trade_logger.warning(
                    f"Insufficient USDT balance. Attempted to buy {amount_to_buy} USDT worth of {symbol} but only have {usdt_balance} USDT.")
                print(f"Insufficient USDT balance to buy {symbol}.")

        except Exception as e:
            self.trade_logger.error(f"Error in buy_crypto: {e}")
            print(f"An error occurred: {e}")

    def sell_crypto(self, symbol, sell_ratio):
        try:
            # 获取服务器时间
            server_time = self.client.get_server_time()
            local_time = int(time.time() * 1000)
            time_diff = server_time['serverTime'] - local_time

            # 获取交易对信息
            info = self.client.get_symbol_info(symbol)
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
            asset_balance = float(self.client.get_asset_balance(asset=base_asset)['free'])
            self.trade_logger.info(f"{base_asset} 余额: {asset_balance} {base_asset}")

            # 获取市场价格
            market_price = float(self.client.get_symbol_ticker(symbol=symbol)['price'])
            self.trade_logger.info(f"{symbol} 市场价格: {market_price} USDT")

            # 计算要售卖的数量，并调整精度
            sell_amount = round(asset_balance * sell_ratio, step_size_precision)
            sell_value = sell_amount * market_price
            self.trade_logger.info(f"计划售卖: {sell_amount} {base_asset}, 约合 {sell_value} USDT")

            # 执行售卖操作，使用调整后的时间戳
            params = {
                'symbol': symbol,
                'side': Client.SIDE_SELL,
                'type': Client.ORDER_TYPE_MARKET,
                'quantity': sell_amount,
                'timestamp': int(time.time() * 1000) + time_diff
            }
            order = self.client.create_order(**params)
            self.trade_logger.info(f"Successfully placed an order: {order}")
            return order

        except BinanceAPIException as e:
            self.trade_logger.error(f"币安API异常: {e}")
            return None
        except Exception as e:
            self.trade_logger.error(f"执行交易过程中出现错误: {e}")
            return None

    def sell_crypto_by_usdt(self, symbol, usdt_amount):
        try:
            # 获取服务器时间
            server_time = self.client.get_server_time()
            local_time = int(time.time() * 1000)
            time_diff = server_time['serverTime'] - local_time

            # 获取要售卖的币种名称（如BTC）
            base_asset = symbol[:-4]

            # 获取交易对信息
            info = self.client.get_symbol_info(symbol)
            step_size = 0.0
            for f in info['filters']:
                if f['filterType'] == 'LOT_SIZE':
                    step_size = float(f['stepSize'])
                    break

            # 计算step_size的精度
            step_size_precision = int(round(-math.log(step_size, 10), 0))

            # 查询账户余额
            asset_balance = float(self.client.get_asset_balance(asset=base_asset)['free'])
            self.trade_logger.info(f"{base_asset} 余额: {asset_balance} {base_asset}")

            # 获取市场价格
            market_price = float(self.client.get_symbol_ticker(symbol=symbol)['price'])
            self.trade_logger.info(f"{symbol} 市场价格: {market_price} USDT")

            # 计算可售卖的最大USDT值
            max_usdt_value = asset_balance * market_price

            if usdt_amount > max_usdt_value:
                self.trade_logger.info(f"请求售卖的USDT金额超过了可售卖的最大值。当前最大可售卖: {max_usdt_value} USDT")
                return None

            # 计算要售卖的币种数量，并调整精度
            sell_quantity = round(usdt_amount / market_price, step_size_precision)
            self.trade_logger.info(f"计划售卖: {usdt_amount} USDT, 约合 {sell_quantity} {base_asset}")

            # 执行售卖操作，使用调整后的时间戳
            params = {
                'symbol': symbol,
                'side': Client.SIDE_SELL,
                'type': Client.ORDER_TYPE_MARKET,
                'quantity': sell_quantity,
                'timestamp': int(time.time() * 1000) + time_diff
            }
            order = self.client.create_order(**params)
            self.trade_logger.info(f"Successfully placed an order: {order}")
            return order

        except BinanceAPIException as e:
            self.trade_logger.error(f"币安API异常: {e}")
            return None
        except Exception as e:
            self.trade_logger.error(f"执行交易过程中出现错误: {e}")
            return None
