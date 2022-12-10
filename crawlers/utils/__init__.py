import arrow
import requests
import scrapy
from selenium import webdriver

from crawlers.config import KD_INTERNAL_API, KD_INTERNAL_TOKEN, template_name_id, DEBUG, PROXY_URL, EXECUTABLE_PATH
from crawlers.utils import digital_processing
from crawlers.utils.group_alarm import information_flow_synchronization
from crawlers.utils.redis_conn import rds


class SpiderBase(scrapy.Spider):

    def error_back(self, failure):
        if DEBUG:
            print(f"Spider Error: {repr(failure)}")
            return

    def get_curent_price(self, coin):
        data = requests.get(url=f'https://api.binance.com/api/v3/ticker/24hr?symbol={coin}USDT').json()
        return float(data['c'])