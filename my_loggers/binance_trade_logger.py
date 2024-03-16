import logging
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger('BinanceTradeLogger')
logger.setLevel(logging.INFO)

# 创建 TimedRotatingFileHandler
handler = TimedRotatingFileHandler('daily_binance_coin_data_trade.log', when="midnight", interval=1,
                                       backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
def get_logger():
    # 设置日志
    # logging.basicConfig(filename='binance_coin_data_analysis.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # 设置日志记录器
    return logger