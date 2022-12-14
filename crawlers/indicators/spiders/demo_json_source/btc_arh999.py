import scrapy

from crawlers.utils import SpiderBase, Tools
from crawlers.utils.group_alarm import catch_except
from jinja2 import Template


class BtcArh999Spider(SpiderBase):
    name = 'idx-btc-arh999'
    url = 'https://fapi.coinglass.com/api/index/ahr999'

    def start_requests(self):
        yield scrapy.Request(url=self.url)

    @catch_except
    def parse(self, response, **kwargs):
        data = response.json()['data']
        params = {
            'arh_999': round(data[-1]['ahr999'], 2),
            'btc_price': data[-1]['value'],
            'change': round(((float(data[-1]['value']) - float(data[-2]['value'])) / float(data[-2]['value'])) * 100, 2)
        }
        print(Template(self.alert_en_template()).render(params))
        print(Template(self.alert_cn_template()).render(params))

    # must be declare
    def alert_en_template(self):
        return """The current BTC ahr999 (AHR Index) is {{arh_999}}. This spot is theoretically unsuitable for bottom fishing or long-term fixed investment. The current price of BTC is {{btc_price}}, and 24H  change is {{change}}. (The above content does not constitute investment advice and is for your reference only. Invest at your own risk.)
        """

    # must be declare
    def alert_cn_template(self):
        return """当前 BTC ahr999(九神指数)为 {{arh_999}}，理论上不宜买入抄底或定投 BTC。当前 BTC 现价 {{btc_price}}，24小时涨跌幅为 {{change}}。（以上内容仅供参考，非投资建议，风险自担。）
        """
