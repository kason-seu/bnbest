from unittest import TestCase
from utils import config_utils

class Test(TestCase):
    def test_parse_config(self):
        kwargs = config_utils.parse_config()
        print(f"{kwargs.get('binance').get('api_key')}")
