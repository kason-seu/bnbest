import configparser
import os
from utils import package_root_util


class CaseSensitiveConfigParser(configparser.ConfigParser):
    def optionxform(self, optionstr):
        return optionstr  # 直接返回原始的选项字符串，不进行大小写转换


class ConfigParser:
    def __init__(self, filename='config.ini'):
        self.config = CaseSensitiveConfigParser()
        self.root_path = package_root_util.root_path()
        self.config_path = os.path.join(self.root_path, 'config', filename)
        self.config.read(self.config_path, encoding='utf-8')
        self.parsed_config = self._parse_config()



    def _parse_config(self):
        config_dict = dict()

        # Binance Config
        api_d = {
            "api_key": self.config.get('binance', 'api_key'),
            "api_key_salt": self.config.get('binance', 'api_key_salt'),
            "api_secret": self.config.get('binance', 'api_secret'),
            "api_secret_salt": self.config.get('binance', 'api_secret_salt')
        }
        config_dict["binance"] = api_d

        # Symbols Config
        symbols_d = {"coin_symbols": self.config.get('symbols', 'coin_symbols')}
        config_dict["symbols"] = symbols_d

        # Buy Limits
        buy_limits_dict = self._transfer_section_to_dict('buy_limits')
        config_dict['buy_limits'] = buy_limits_dict

        # 购买的condition, 低于某个比率就买
        buy_rate_below_condition = self._transfer_section_to_dict('buy_rate_below_condition')
        config_dict['buy_rate_below_condition'] = buy_rate_below_condition

        # 售卖的condition, 高于某个比率就卖

        sell_rate_condition = self._transfer_section_to_dict('sell_rate_condition')
        config_dict['sell_rate_condition'] = sell_rate_condition

        sell_limits = self._transfer_section_to_dict('sell_limits')
        config_dict['sell_limits'] = sell_limits
        return config_dict

    def _transfer_section_to_dict(self, section) -> dict:
        return {key: self.config.get(section, key) for key in self.config[section]}

    def get(self, section, option=None):
        if option:
            return self.parsed_config[section].get(option)
        return self.parsed_config.get(section)



# config_parser = ConfigParser()
#
# # 获取整个'symbols'部分
# symbols_config = config_parser.get('symbols')
# print(symbols_config)
#
# # 获取'buy_limits'部分
# buy_limits_config = config_parser.get('buy_limits')
# print(buy_limits_config)
#
# # 获取特定选项
# api_key = config_parser.get('binance', 'api_key')
# print(api_key)
