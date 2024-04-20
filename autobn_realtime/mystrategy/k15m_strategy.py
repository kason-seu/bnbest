from my_loggers import k15_strategy_logger

logger = k15_strategy_logger.get_logger()
from autobn_realtime.dingding_robot import send_dingtalk_message
from coin_core import binance_client
from autobn_realtime import bn_op
from autobn_realtime import bnutils


class K15Strategy:

    def __init__(self, kline_data):
        self.kline_data = kline_data
        self.coins = {}
        self.client = binance_client.get_bn_client()

    def handle(self):

        open_price = self.kline_data.open_price
        close_price = self.kline_data.close_price
        event_time = self.kline_data.event_time
        coin = self.kline_data.symbol

        lower_ratio = (close_price - open_price) / open_price
        upper_ratio = (close_price - open_price) / open_price
        lower_ratio_percentage = "{:.3%}".format(lower_ratio)
        upper_ratio_percentage = "{:.3%}".format(upper_ratio)

        logger.info(
            f"coin={coin}, real_time={event_time}, open_price={open_price}, close_price={close_price}, "
            f"upper_ratio={upper_ratio_percentage}, lower_ratio={lower_ratio_percentage}")

        if (open_price > close_price) and (lower_ratio < -0.1):
            quantity = bnutils.get_quantity(close_price, 10)
            logger.info(
                f"触发了下界条件是lower_ratio < -0.1,这是向下插强针了,启动购买操作,coin={coin}, real_time={event_time}, "
                f"lower_ratio={lower_ratio_percentage}, open_price={open_price}, close_price={close_price}, quantity={quantity}")
            # print(f"触发了下界条件是lower_ratio < -0.1,这是向下插强针了,启动购买操作,coin={coin}, real_time={event_time}, "
            #     f"lower_ratio={lower_ratio_percentage}, open_price={open_price}, close_price={close_price}, quantity={quantity}")
            #bn_op.buy_crypto_by_limit(client=self.client, symbol=coin, quantity=quantity, price=close_price)
            send_dingtalk_message(
                message=f"触发了下界条件是lower_ratio < -0.1,这是向下插强针了,启动购买操作,coin={coin}, real_time={event_time}, "
                        f"lower_ratio={lower_ratio_percentage}, open_price={open_price}, close_price={close_price}, 买的quantity={quantity}")

        if (open_price < close_price) and (upper_ratio > 0.1):
            logger.info(
                f"触发了上界条件是upper_ratio > 0.1,这是向上狂拉了,启动售卖操作,coin={coin}, real_time={event_time}, "
                f"upper_ratio={upper_ratio_percentage}, open_price={open_price}, close_price={close_price}")
            # print(f"触发了上界条件是upper_ratio > 0.05,这是向上狂拉了,启动售卖操作,coin={coin}, real_time={event_time}, "
            #     f"upper_ratio={upper_ratio_percentage}, open_price={open_price}, close_price={close_price}")
            #bn_op.sell_crypto_by_usdt_limit(client=self.client, symbol=coin, usdt_amount=10, sell_price=close_price)
            send_dingtalk_message(
                message=f"触发了上界条件是upper_ratio > 0.1,这是向上狂拉了,启动售卖操作,coin={coin}, real_time={event_time}, "
                f"upper_ratio={upper_ratio_percentage}, open_price={open_price}, close_price={close_price}")

        if (open_price > close_price) and (lower_ratio < -0.2):
            quantity = bnutils.get_quantity(close_price, 10)
            logger.info(
                f"触发了下界条件是lower_ratio < -0.2,这是向下插强针了,启动购买操作,coin={coin}, real_time={event_time}, "
                f"lower_ratio={lower_ratio_percentage}, open_price={open_price}, close_price={close_price}, quantity={quantity}")
            # print(f"触发了下界条件是lower_ratio < -0.1,这是向下插强针了,启动购买操作,coin={coin}, real_time={event_time}, "
            #     f"lower_ratio={lower_ratio_percentage}, open_price={open_price}, close_price={close_price}, quantity={quantity}")
            # bn_op.buy_crypto_by_limit(client=self.client, symbol=coin, quantity=quantity, price=close_price)
            send_dingtalk_message(
                message=f"触发了下界条件是lower_ratio < -0.2,这是向下插强针了,启动购买操作,coin={coin}, real_time={event_time}, "
                        f"lower_ratio={lower_ratio_percentage}, open_price={open_price}, close_price={close_price}, 买的quantity={quantity}")

        if (open_price < close_price) and (upper_ratio > 0.2):
            logger.info(
                f"触发了上界条件是upper_ratio > 0.2,这是向上狂拉了,启动售卖操作,coin={coin}, real_time={event_time}, "
                f"upper_ratio={upper_ratio_percentage}, open_price={open_price}, close_price={close_price}")
            # print(f"触发了上界条件是upper_ratio > 0.1,这是向上狂拉了,启动售卖操作,coin={coin}, real_time={event_time}, "
            #     f"upper_ratio={upper_ratio_percentage}, open_price={open_price}, close_price={close_price}")
            # bn_op.sell_crypto_by_usdt_limit(client=self.client, symbol=coin, usdt_amount=10, sell_price=close_price)
            send_dingtalk_message(
                message=f"触发了上界条件是upper_ratio > 0.2,这是向上狂拉了,启动售卖操作,coin={coin}, real_time={event_time}, "
                f"upper_ratio={upper_ratio_percentage}, open_price={open_price}, close_price={close_price}")

        if (open_price > close_price) and (lower_ratio < -0.15):
            quantity = bnutils.get_quantity(close_price, 10)
            logger.info(
                f"触发了下界条件是lower_ratio < -0.2,这是向下插强针了,启动购买操作,coin={coin}, real_time={event_time}, "
                f"lower_ratio={lower_ratio_percentage}, open_price={open_price}, close_price={close_price}, quantity={quantity}")
            send_dingtalk_message(
                message=f"触发了下界条件是lower_ratio < -0.15,这是向下插强针了,启动购买操作,coin={coin}, real_time={event_time}, "
                        f"lower_ratio={lower_ratio_percentage}, open_price={open_price}, close_price={close_price}, 买的quantity={quantity}")

        if (open_price < close_price) and (upper_ratio > 0.15):
            logger.info(
                f"触发了上界条件是upper_ratio > 0.2,这是向上狂拉了,启动售卖操作,coin={coin}, real_time={event_time}, "
                f"upper_ratio={upper_ratio_percentage}, open_price={open_price}, close_price={close_price}")
            send_dingtalk_message(
                message=f"触发了上界条件是upper_ratio > 0.2,这是向上狂拉了,启动售卖操作,coin={coin}, real_time={event_time}, "
                f"upper_ratio={upper_ratio_percentage}, open_price={open_price}, close_price={close_price}")