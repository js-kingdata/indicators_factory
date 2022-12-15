from crawlers.utils import SpiderBase
from jinja2 import Template
from crawlers.utils.group_alarm import catch_except


def build_coin_info(data):
    return {
        'symbol': data['symbol'],
        'long_short_rate': round(data['longRate'] / data['shortRate'], 2),
        'long_rate': data['longRate'],
        'short_rate': data['shortRate'],
        'list': [{
            'exchange_name': exchange_info['exchangeName'],
            'long_rate': exchange_info['longRate'],
            'short_rate': exchange_info['shortRate']
        } for exchange_info in data['list'][:3]]
    }


class ContractPositionRatio(SpiderBase):
    name = 'idx-contract-position-ratio'

    start_urls = [
        'https://fapi.coinglass.com/api/futures/longShortRate?symbol=BTC&timeType=3',
        'https://fapi.coinglass.com/api/futures/longShortRate?symbol=ETH&timeType=3'
    ]

    @catch_except
    def parse(self, response, **kwargs):
        data = response.json()['data'][0]
        params = {
            'info': [build_coin_info(data)]
        }
        print(Template(self.alert_en_template()).render(params))
        print(Template(self.alert_cn_template()).render(params))

    # must be declare
    def alert_en_template(self):
        return """
According to KingData monitoring, {% for coin in info%}In the past 4 hours, {{coin.symbol}} Long/Short Ratio across network is {{coin.long_short_rate}}, with {{coin.long_rate}}% longs and  {{coin.short_rate}}% shorts. {%if coin.long_short_rate>1%}Longs outweigh shorts{% else %}Shorts outweigh Longs{% endif %}.
Among leading exchanges:{% for exchange in coin.list %}
{{exchange.exchange_name}}: long {{exchange.long_rate}}%, short {{exchange.short_rate}}%{% endfor %}
{% endfor %}
"""

    # must be declare
    def alert_cn_template(self):
        return """
据 KingData 数据监控，{% for coin in info%}最近4小时，{{coin.symbol}}全网合约多空比为 {{coin.long_short_rate}}，多单占比 {{coin.long_rate}}%，空单占比{{coin.short_rate}}%，{%if coin.long_short_rate>1%}看多人数大于看空人数{% else %}看空人数大于看多人数{% endif %}。
其中主流交易所：{% for exchange in coin.list %}
{{exchange.exchange_name}}：做多{{exchange.long_rate}}% 做空{{exchange.short_rate}}%{% endfor %}
{% endfor %}
"""
