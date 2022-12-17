import scrapy

from crawlers.utils import SpiderBase
from jinja2 import Template
from crawlers.utils.group_alarm import catch_except


def process(data):
    '''
    1、Project TVL > $100M
    2、TVL 7d changes > 80%(up or down)
    '''
    alert_list = []
    for prot in data:
        if prot['tvlPrevWeek'] is None or prot['tvl'] <= 100000000:
            continue
        chg_pct = (prot['tvl'] / prot['tvlPrevWeek'] -1)* 100
        if abs(chg_pct) > 100:
            if prot['tvl'] > 1000000000:
                str_tvl = f"{round(prot['tvl']/1000000000)}B"
            elif prot['tvl'] > 1000000:
                str_tvl = f"{round(prot['tvl']/1000000)}M"
            alert_list.append({
                'name':prot['name'],
                'tvl': str_tvl,
                'tvl_chg_pct': f'+{round(chg_pct)}' if chg_pct >0 else str(round(chg_pct))
                })
    return alert_list


class TVLChange(SpiderBase):
    name = 'idx-tvl-change'

    #url = 'https://api.llama.fi/lite/protocols2'
    start_urls = ['https://api.llama.fi/lite/protocols2']

    #def start_requests(self):
    #    yield scrapy.Request(url=self.url, errback=self.error_back)

    @catch_except
    def parse(self, response, **kwargs):
        data = response.json()['protocols']
        data_iltered = process(data)
        if not data_iltered:
            return
        params = {
            'info': data_iltered
        }
        print(Template(self.alert_en_template()).render(params))
        print(Template(self.alert_cn_template()).render(params))
        print(params)


    def alert_en_template(self):
        return """
According to KingData monitoring, the projects whose TVL fluctuated by more than 80% in the past 7 days:{% for prot in info%}
{{prot.name}}: TVL: ${{prot.tvl}} (7d: {{prot.tvl_chg_pct}}%){% endfor %}
"""

    def alert_cn_template(self):
        return """
据 KingData 监控，过去 7天 TVL 波动超过 80% 的项目有{% for prot in info%}
{{prot.name}}: TVL: ${{prot.tvl}} (7d: {{prot.tvl_chg_pct}}%){% endfor %}
"""
