import scrapy
import re

from crawlers.utils import SpiderBase, Tools
from crawlers.utils.group_alarm import catch_except
from jinja2 import Template


def minimal_regularity(pattern, string):
    comp = re.compile(pattern, re.S)
    return re.findall(comp, string)


class BtcMVRVSpider(SpiderBase):
    name = 'idx-btc-mvrv'
    url = 'https://charts.woobull.com/bitcoin-mvrv-ratio/'

    def start_requests(self):
        # error_back method is defined in SpiderBase
        yield scrapy.Request(url=self.url, errback=self.error_back)

    # Exceptions must be handled, only need to be declared, and the processing logic system has been processed uniformly
    @catch_except
    def parse(self, response, **kwargs):
        string = response.text
        for pattern in ['mvrv = .*?}', 'y:.*?]', r'\[.*\]']:
            # Get the desired data from html
            string = minimal_regularity(pattern, string)[0]
        btc_mv_rv = eval(string)[-1]
        params = {
            'mv_rv': round(btc_mv_rv, 2)
        }
        print(Template(self.alert_en_template()).render(params))
        print(Template(self.alert_cn_template()).render(params))
        # Tools.multilingual_information_flow_push(
        #     tmp_name='exchange_notice',
        #     template_id=760,
        #     params=params
        # )

    # must be declare
    def alert_en_template(self):
        return """According to KingData monitoring, BTC current MVRV ratio is {{mv_rv}}，{% if mv_rv < 1 %}theoretically the price is at bottom, marking late stage bear market accumulations.{% endif %}{% if mv_rv > 3.7 %} theoretically the price is at top, signaling late stage bull cycles.{% endif %}{% if 1<= mv_rv <= 3.7 %}Theoretically, MVRV values over '3.7' indicated price top and values below '1' indicated price bottom.{% endif %}。
 (The above content is for your reference only and does not constitute investment advice. Invest at your own risk.)  """

    # must be declare
    def alert_cn_template(self):
        return """据 KingData 数据监控，BTC 当前 MVRV 比率为 {{mv_rv}}，{% if mv_rv < 1 %}理论上价格见底，市场处在熊市晚期积累阶段。{% endif %}{% if mv_rv > 3.7 %}理论上价格见顶，市场处在牛市后期。{% endif %}{% if 1<= mv_rv <= 3.7 %}理论上，MVRV > 3.7 是价格见顶信号，MVRV < 1 是价格见底信号。{% endif %} 。
（以上内容仅作参考，不构成投资建议，风险自担。）"""
