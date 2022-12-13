import scrapy

from crawlers.utils import SpiderBase
from crawlers.utils.group_alarm import catch_except


class BtcArh999Spider(SpiderBase):
    name = 'idx-btc-arh999'
    url = 'https://fapi.coinglass.com/api/index/ahr999'

    def start_requests(self):
        yield scrapy.Request(url=self.url)

    @catch_except
    def parse(self, response, **kwargs):
        data = response.json()['data']
        Tools.multilingual_information_flow_push(
            tmp_name="BTC_ARH999",
            params={
                'arh_999': round(data[-1]['ahr999'], 2),
                'btc_price': data[-1]['value'],
                'change': round(((float(data[-1]['value']) - float(data[-2]['value'])) / float(data[-2]['value'])) * 100, 2)
            },
        )
