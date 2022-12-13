import scrapy
import re

from crawlers.utils import SpiderBase
from crawlers.utils.group_alarm import catch_except


def minimal_regularity(pattern, string):
    comp = re.compile(pattern, re.S)
    return re.findall(comp, string)


class BtcMVRVSpider(SpiderBase):
    name = 'idx-btc-mvrv'
    url = 'https://charts.woobull.com/bitcoin-mvrv-ratio/'

    def start_requests(self):
        yield scrapy.Request(url=self.url, errback=self.error_back)

    @catch_except
    def parse(self, response, **kwargs):
        string = response.text
        for pattern in ['mvrv = .*?}', 'y:.*?]', r'\[.*\]']:
            string = minimal_regularity(pattern, string)[0]
        btc_mv_rv = eval(string)[-1]
        btc_market = get_coin_markets('BTC')
        Tools.multilingual_information_flow_push(
            tmp_name='BTC_MVRV',
            params={
                'mv_rv': round(btc_mv_rv, 2),
                'btc_price': btc_market['price'],
                'change_24h': round(btc_market['change24h'] * 100, 2)
            }
        )
