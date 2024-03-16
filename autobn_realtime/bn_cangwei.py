import numpy as np
import requests
from autobn_realtime import bnutils
from coin_core import binance_client
class TopLongShortPositionRatio:
    """
    全市场多空持仓人数比对象
    """
    def __init__(self, symbol, longShortPositionRatio, longPosition, shortPosition, timestamp):
        self.symbol = symbol                        # 交易对，例如 'BTCUSDT'
        self.longShortPositionRatio = longShortPositionRatio  # 多空持仓人数比
        self.longPosition = longPosition            # 多头持仓人数
        self.shortPosition = shortPosition          # 空头持仓人数
        self.timestamp = bnutils.time_int_str(timestamp)                  # 时间戳

    @classmethod
    def from_dict(cls, data):
        """
        从字典创建TopLongShortPositionRatio对象
        """
        return cls(
            symbol=data.get('symbol'),
            longShortPositionRatio=data.get('longShortRatio'),
            longPosition=data.get('longAccount'),
            shortPosition=data.get('shortAccount'),
            timestamp=data.get('timestamp')
        )

def fetch_top_long_short_position_ratio(symbol, period='5m', limit=1):
    """
    使用REST API获取全市场多空持仓人数比，并封装成对象
    :param symbol: 交易对，例如 'BTCUSDT'
    :param period: 数据间隔
    :param limit: 获取数据的数量
    :return: TopLongShortPositionRatio对象或None
    """
    api_url = "https://fapi.binance.com/futures/data/topLongShortPositionRatio"
    params = {'symbol': symbol, 'period': period, 'limit': limit}
    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data:
            return TopLongShortPositionRatio.from_dict(data[0])
    else:
        print(f"Error fetching data: {response.status_code}")
        return None


def fetch_top_long_short_position_ratioV2(symbol, period='5m', limit=1):
    """
    获取全市场多空持仓人数比
    :param symbol: 交易对，例如 'BTCUSDT'
    :param period: 数据间隔，可选值有 '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d'
    :param limit: 获取数据的数量，最大可为500
    :return: 包含多空比例的字典
    """
    api_url = "https://fapi.binance.com/futures/data/topLongShortPositionRatio"  # 注意：请根据需要调整URL
    params = {
        "symbol": symbol,
        "period": period,
        "limit": limit
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        # 返回最新的数据点
        if data:
            return data[0]
    else:
        print("Error:", response.status_code)
        return None

class GlobalLongShortAccountRatio:
    """
    全市场多空持仓金额比对象
    """

    def __init__(self, symbol, longShortRatio, longAccount, shortAccount, timestamp):
        self.symbol = symbol  # 交易对，例如 'BTCUSDT'
        self.longShortRatio = longShortRatio  # 多空持仓金额比
        self.longAccount = longAccount  # 多头账户的比例
        self.shortAccount = shortAccount  # 空头账户的比例
        self.timestamp = bnutils.time_int_str(timestamp)  # 时间戳

    @classmethod
    def from_dict(cls, data):
        """
        从字典创建GlobalLongShortAccountRatio对象
        """
        return cls(
            symbol=data.get('symbol'),
            longShortRatio=data.get('longShortRatio'),
            longAccount=data.get('longAccount'),
            shortAccount=data.get('shortAccount'),
            timestamp=data.get('timestamp')
        )


def fetch_global_long_short_account_ratio(symbol, period='5m', limit=1):
    """
    使用REST API获取全市场多空持仓金额比，并封装成对象
    :param symbol: 交易对，例如 'BTCUSDT'
    :param period: 数据间隔
    :param limit: 获取数据的数量
    :return: GlobalLongShortAccountRatio对象或None
    """
    url = "https://fapi.binance.com/futures/data/globalLongShortAccountRatio"
    params = {'symbol': symbol, 'period': period, 'limit': limit}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data:
            return GlobalLongShortAccountRatio.from_dict(data[0])
    else:
        print(f"Error fetching data: {response.status_code}")
        return None


if __name__ == '__main__':
    # 示例查询
    # 示例查询
    symbol = "BTCUSDT"
    ratio_object = fetch_global_long_short_account_ratio(symbol)
    if ratio_object:
        print(
            f"交易对: {ratio_object.symbol}, 多空持仓金额比: {ratio_object.longShortRatio}, "
            f"多头账户比例: {ratio_object.longAccount}, 空头账户比例: {ratio_object.shortAccount},"
            f" 时间戳: {ratio_object.timestamp}")

    ratio_object = fetch_top_long_short_position_ratio(symbol)
    if ratio_object:
        print(
            f"交易对: {ratio_object.symbol}, 多空持仓人数比: {ratio_object.longShortPositionRatio}, "
            f"多头持仓人数: {ratio_object.longPosition}, 空头持仓人数: {ratio_object.shortPosition}, "
            f"时间戳: {ratio_object.timestamp}")

    print(fetch_top_long_short_position_ratioV2(symbol))

