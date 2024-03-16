from autobn_realtime import bnutils
class KlineData:
    def __init__(self, event_type, event_time, symbol, start_time, end_time, open_price, close_price, high_price, low_price, volume, number_of_trades, is_kline_closed):
        self.event_type = event_type  # 事件类型
        self.event_time = bnutils.time_int_str(event_time)  # 事件时间
        self.symbol = symbol  # 交易对，如BTC/USDT

        self.start_time = bnutils.time_int_str(start_time)  # K线的开始时间

        self.end_time = bnutils.time_int_str(end_time)  # K线的结束时间
        self.open_price = float(open_price)  # 开盘价
        self.close_price = float(close_price)  # 收盘价
        self.high_price = float(high_price)  # 最高价
        self.low_price = float(low_price)  # 最低价
        self.volume = float(volume)  # 成交量
        self.number_of_trades = float(number_of_trades)  # 成交笔数
        self.is_kline_closed = is_kline_closed  # 本K线是否完结（即本时间段是否结束）

    def __str__(self):
        # 返回一个格式化的字符串，描述K线数据
        return f"KlineData(symbol={self.symbol}, event_time={self.event_time}, start_time={self.start_time}, open_price={self.open_price}, " \
               f"close_price={self.close_price}, high_price={self.high_price}, low_price={self.low_price}, volume={self.volume}, " \
               f"number_of_trades={self.number_of_trades}, is_kline_closed={self.is_kline_closed}, end_time={self.end_time})"
