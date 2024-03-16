import requests

API_URL = "https://fapi.binance.com"

# 获取最新价格
def get_latest_price(symbol):
    url = f"{API_URL}/fapi/v1/ticker/price"
    params = {'symbol': symbol}
    response = requests.get(url, params=params)
    price = response.json().get('price')
    return float(price) if price else None

# 伪代码 - 实际上Binance API不直接提供这样的数据，需要你自己计算
def calculate_liquidation_ratio(symbol, latest_price):
    # 假设的逻辑来计算爆仓比例
    # 这里需要你根据实际的保证金和杠杆设置进行计算
    long_liquidation_ratio = 0.1  # 假设10%的多头仓位接近爆仓
    short_liquidation_ratio = 0.05  # 假设5%的空头仓位接近爆仓
    return long_liquidation_ratio, short_liquidation_ratio


if __name__ == '__main__':
    # 示例使用
    symbol = "BTCUSDT"
    latest_price = get_latest_price(symbol)
    if latest_price:
        print(f"Latest price for {symbol}: {latest_price}")
        long_liquidation_ratio, short_liquidation_ratio = calculate_liquidation_ratio(symbol, latest_price)
        print(f"Estimated long liquidation ratio: {long_liquidation_ratio}")
        print(f"Estimated short liquidation ratio: {short_liquidation_ratio}")
    else:
        print("Failed to fetch latest price.")
