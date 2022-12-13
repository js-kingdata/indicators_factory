import arrow
import requests
import scrapy
from selenium import webdriver

from crawlers.config import DEBUG, PROXY_URL
from crawlers.utils.redis_conn import rds


class SpiderBase(scrapy.Spider):

    def error_back(self, failure):
        if DEBUG:
            print(f"Spider Error: {repr(failure)}")
            return

    def get_curent_price(self, coin):
        data = requests.get(url=f'https://api.binance.com/api/v3/ticker/24hr?symbol={coin}USDT').json()
        return float(data['c'])