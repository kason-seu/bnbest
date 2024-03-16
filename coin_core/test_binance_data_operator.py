from unittest import TestCase
import binance_client
import binance_data_operator


class Test(TestCase):
    def test_buy_crypto(self):
        client = binance_client.get_binance_client()
        binance_data_operator.buy_crypto('ETHUSDT', 50, client)


class Test(TestCase):
    def test_sell_crypto_by_usdt(self):
        client = binance_client.get_binance_client()
        binance_data_operator.sell_crypto_by_usdt('BNBUSDT',50, client)
