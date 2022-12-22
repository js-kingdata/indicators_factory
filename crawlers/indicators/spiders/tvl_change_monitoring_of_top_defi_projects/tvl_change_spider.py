import scrapy

from crawlers.utils import SpiderBase
from jinja2 import Template
from crawlers.utils.group_alarm import catch_except
from crawlers.utils.humanize import humanize_float_en


class TVLChange(SpiderBase):
    name = 'idx-tvl-change'

    start_urls = ['https://api.llama.fi/lite/protocols2']


    @catch_except
    def parse(self, response, **kwargs):
        data = response.json()['protocols']
        if not data or len(data) < 1:
            return
        for prot in data:
            self.process(prot)


    def process(self, prot):
        '''
        1、Project TVL > $100M
        2、TVL 1d change > 20%(up or down) or  TVL 7d changes > 50%(up or down) or TVL 7d changes > 100%(up or down)
        '''
        if prot['tvl'] <= 100000000:
            return
        change_1d = change_7d = change_30d = 0

        change_1d = (prot['tvl'] - prot['tvlPrevDay']) / prot['tvlPrevDay'] * 100 if prot['tvlPrevDay'] else 0
        change_7d = (prot['tvl'] - prot['tvlPrevWeek']) / prot['tvlPrevWeek'] * 100 if prot['tvlPrevWeek'] else 0
        change_30d = (prot['tvl'] - prot['tvlPrevMonth']) / prot['tvlPrevMonth'] * 100 if prot['tvlPrevMonth'] else 0
        params = {
            'project_name': prot['name'],
            'category': prot['category'],
            'symbol': prot['symbol'],
            'url': prot['url'],
            'tvl': humanize_float_en(prot['tvl']),
            'change_1d': round(change_1d),
            'change_7d': round(change_7d),
            'change_30d': round(change_30d),
        }
        if abs(change_1d) <= 20 and abs(change_7d) <= 50 and abs(change_30d) <= 100:
            return
        if abs(change_1d) > 20:
            params['interval'] = '1'
            params['interval_change'] = change_1d
        if abs(change_7d) > 50:
            params['interval'] = '7'
            params['interval_change'] = change_7d
        if abs(change_30d) > 100:
            params['interval'] = '30'
            params['interval_change'] = change_30d
        params['interval_change'] = round(params['interval_change'])
        print(Template(self.alert_en_template()).render(params))
        print(Template(self.alert_cn_template()).render(params))


    def alert_en_template(self):
        return """
According to KingData monitoring, in the past {{interval}} days, {{project_name}}'s TVL {% if interval_change > 0 %} increased {% else %} decreased {% endif %} {{ interval_change }}%.

Project name: {{ project_name }}
Category: {{ category }}
Token: {{ symbol }}
Official Website: {{ url }}
Current TVL: {{ tvl }}
TVL(24H%): {{ change_1d }}%
TVL(7D%): {{ change_7d }}%
TVL(30D%): {{ change_30d }}%
"""

    def alert_cn_template(self):
        return """
据 KingData 监控，过去 {{interval}} 天, {{project_name}} 的 TVL {% if interval_change > 0 %}上涨{% else %}下跌{% endif %} {{ interval_change }}%。

项目名称: {{ project_name }}
项目类别: {{ category }}
Token: {{ symbol }}
官网链接: {{ url }}
当前 TVL: {{ tvl }}
TVL(24H%): {{ change_1d }}% 
TVL(7D%): {{ change_7d }}%
TVL(30D%): {{ change_30d }}%
"""
