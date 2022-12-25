import requests
import scrapy

from crawlers.config import DEBUG
from crawlers.utils.redis_conn import rds


class SpiderBase(scrapy.Spider):

    def error_back(self, failure):
        if DEBUG:
            print(f"Spider Error: {repr(failure)}")
            return

    def get_curent_price(self, coin, is_with_change_percent = False):
        data = requests.get(url=f'https://api.binance.com/api/v3/ticker/24hr?symbol={coin.upper()}USDT').json()
        if not data['lastPrice']:
            return False

        if is_with_change_percent:
            return {
                'current_price': float(data['lastPrice']),
                'change_24h': (float(data['lastPrice']) - float(data['openPrice'])) / float(data['openPrice']) * 100
            }
        else:
            return float(data['lastPrice'])