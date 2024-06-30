from unittest import TestCase
from utils import config_utils
from utils import encode_decode_util
from binance import Client


class Test(TestCase):
    def test_parse_config(self):

        config = config_utils.parse_config()
        ak = encode_decode_util.decrypt_message(config.get('binance').get('api_key'),
                                                config.get('binance').get('api_key_salt'))
        akeys = encode_decode_util.decrypt_message(config.get('binance').get('api_secret'),
                                                   config.get('binance').get('api_secret_salt'))
        client = Client(ak, akeys, testnet=False, tld='com')
        print(client.API_URL)
        # 获取账户状态
        account_status = client.get_account_status()
        print("账户状态:", account_status)

        # 获取账户信息
        account_info = client.get_account()
        print("账户信息:", account_info)

        # 获取账户交易权限等详细信息
        account_api_trading_status = client.get_account_api_trading_status()
        print("API交易状态:", account_api_trading_status)