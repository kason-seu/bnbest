import threading

from my_loggers import binance_trade_condition_logger


class TradeCounter:
    def __init__(self, buy_limits_config: dict, sell_limits_config: dict):
        self.buy_value_by_key = {key: 0 for key in buy_limits_config.keys()}
        self.buy_limits_config = buy_limits_config
        self.buy_lock_by_key = {key: threading.Lock() for key in buy_limits_config.keys()}
        self.logger = binance_trade_condition_logger.get_logger()
        self.buy_lock = threading.Lock()
        self.sell_limits_config = {key: int(sell_limits_config[key]) for key in sell_limits_config}
        self.sell_value_by_key = {key: 0 for key in sell_limits_config.keys()}
        self.sell_lock_by_key = {key: threading.Lock() for key in sell_limits_config.keys()}

    def buy_increment(self, symbol) -> bool:
        # 确保每个symbol都有一个锁
        if symbol not in self.buy_lock_by_key:
            self.logger.error(f"{symbol}购买时配置文件里面没有配置该币对应的购买次数，不能购买")
            return False
        with self.buy_lock_by_key[symbol]:
            if self.buy_value_by_key.get(symbol) < int(self.buy_limits_config[symbol]):
                self.buy_value_by_key[symbol] = self.buy_value_by_key[symbol] + 1
                self.logger.info(
                    f"{symbol} 在购买限制条件{self.buy_limits_config[symbol]} 以下，可以执行购买: 当前值为 {self.buy_value_by_key[symbol]}")
                return True
            else:
                self.logger.error(f"{symbol}购买操作次数已达到上线{self.buy_limits_config[symbol]}，不再执行购买操作")
                return False

    def sell_increment(self, symbol) -> bool:
        # 确保每个symbol都有一个锁
        if symbol not in self.sell_lock_by_key:
            self.logger.error(f"{symbol}售卖配置文件里面没有配置该币对应的售卖次数，不能卖")
            return False
        with self.sell_lock_by_key[symbol]:
            if self.sell_value_by_key.get(symbol) < int(self.sell_limits_config[symbol]):
                self.sell_value_by_key[symbol] = self.sell_value_by_key[symbol] + 1
                self.logger.info(
                    f"{symbol} 在售卖限制条件{self.sell_limits_config[symbol]} 以下，可以执行售卖: 当前值为 {self.sell_value_by_key[symbol]}")
                return True
            else:
                self.logger.error(f"{symbol}售卖操作次数已达到上线{self.sell_limits_config[symbol]}，不再执行售卖操作")
                return False

    def acquire_buyer_lock(self):
        return self.buy_lock
