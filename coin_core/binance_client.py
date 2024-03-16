from utils import encode_decode_util
from binance.client import Client
from utils import config_parser


def get_binance_client(**kwargs) -> Client:
    origin_api_key = encode_decode_util.decrypt_message(kwargs.get('api_key'), kwargs.get('api_key_salt'))
    origin_api_secret = encode_decode_util.decrypt_message(kwargs.get('api_secret'), kwargs.get('api_secret_salt'))
    client = Client(origin_api_key, origin_api_secret, requests_params={'timeout': 30})
    return client


def get_bn_client() -> Client:
    cfg = config_parser.ConfigParser()
    client = get_binance_client(**cfg.get("binance"))
    return client


if __name__ == '__main__':
    print(get_bn_client())
