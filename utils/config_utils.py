import configparser
import os
from utils import package_root_util


def parse_config():
    # 读取配置文件
    config = configparser.ConfigParser()

    root_path = package_root_util.root_path()
    config_path = os.path.join(root_path, 'config', 'config.ini')
    config.read(config_path, encoding='utf-8')
    # print(config.sections())  # This will print all the section names being read

    api_key = config.get('binance', 'api_key')
    api_key_salt = config.get('binance', 'api_key_salt')
    api_secret = config.get('binance', 'api_secret')
    api_secret_salt = config.get('binance', 'api_secret_salt')

    config_dict = dict()
    api_d = dict()
    api_d["api_key"] = api_key
    api_d["api_key_salt"] = api_key_salt
    api_d["api_secret"] = api_secret
    api_d["api_secret_salt"] = api_secret_salt
    config_dict["binance"] = api_d

    symbols_d = dict()
    coin_symbols = config.get('symbols', 'coin_symbols')
    symbols_d["coin_symbols"] = coin_symbols

    config_dict["symbols"] = coin_symbols

    buyer_limits_dict = transfer_section_to_dict(config, 'buy_limits')
    config_dict['buy_limits'] = buyer_limits_dict
    return config_dict


def get_symbols():
    config = parse_config()
    return config.get("symbols")

def get_buy_limits():
    config = parse_config()
    return config.get("buy_limits")

def transfer_section_to_dict(config, section) -> dict:
    return {key: config.get(section, key) for key in config[section]}


if __name__ == '__main__':
    parse_config()
