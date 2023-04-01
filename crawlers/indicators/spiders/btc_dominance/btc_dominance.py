import json

import scrapy
import time
import datetime
from crawlers.utils import SpiderBase, rds
from crawlers.utils.group_alarm import catch_except
from jinja2 import Template
from crawlers.utils.humanize import humanize_float_en


class BTCDominanceAlert(SpiderBase):
    name = 'btc_dominance_alert'
    start_url = "https://api.coingecko.com/api/v3/global"

    def start_requests(self):
        yield scrapy.Request(url=self.start_url)

    @catch_except
    def parse(self, response):
        data = response.json()['data']

        pre_btc_dominance = rds.getex(self.name, 'btc_dominance')

        btc_dominance = round(float(data['market_cap_percentage']['btc']), 2)

        if pre_btc_dominance is not None :
            btc_dominance_change = round(float(btc_dominance) - float(pre_btc_dominance), 4)
            params = {
                "btc_dominance": btc_dominance,
                "btc_dominance_change": btc_dominance_change
            }
            print(Template(self.alert_cn_template()).render(params))
        else :
            pass

        rds.setex(self.name, 'btc_dominance', str(btc_dominance), 60 * 60 * 25)


    # must be declare
    def alert_en_template(self):
        return """
        Today's BTC Dominance ratio is: {{btc_dominance}}%, the 24-hour dominance ratio{% if btc_dominance_change > 0 %} has risen by: {{btc_dominance}}%{% endif %}{% if btc_dominance_change < 0 %} has fallen by: {{btc_dominance}}%{% endif %}{% if btc_dominance_change == 0 %} remains unchanged. {% endif %}
        """

    # must be declare
    def alert_cn_template(self):
        return """
        据 KingData 数据监控：
        今日 BTC 市值占比为：{{btc_dominance}}%，24h 市值占比{% if btc_dominance_change > 0 %}上涨：{{btc_dominance}}%{% endif %}{% if btc_dominance_change < 0 %}下降：{{btc_dominance}}%{% endif %}{% if btc_dominance_change == 0 %}不变。{% endif %}
        """
    


'''
BTC 市值占比可以用来衡量当前市场热度和交易标的，是趋势交易的关键指标之一。该指标的使用需要结合大盘价格走势并且关注当前指标处于高位 OR 低位进行判断。

BTC Dominance can be used to measure the current market heat and trading targets, and is one of the key indicators for trend trading. The use of this indicator requires combining the trend of the overall market prices and paying attention to whether the current indicator is at a high or low level for judgment.
'''
