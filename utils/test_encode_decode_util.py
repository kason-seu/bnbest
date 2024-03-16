from unittest import TestCase
from utils import encode_decode_util
from utils import config_utils

class Test(TestCase):
    def test_decode_message(self):
        kwargs = config_utils.parse_config()
        origin = encode_decode_util.decrypt_message(kwargs.get('binance').get('api_key'), kwargs.get('binance').get('api_key_salt'))
        print(origin)
