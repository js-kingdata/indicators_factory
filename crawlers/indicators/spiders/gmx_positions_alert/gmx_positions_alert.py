import json

import scrapy
import time
import datetime
from crawlers.utils import SpiderBase, rds
from crawlers.utils.group_alarm import catch_except
from jinja2 import Template
from crawlers.utils.humanize import humanize_float_en
import requests


class GmxSpider(SpiderBase):
    name = 'gmx_positions'

    arb_base_url = 'https://arb-mainnet.g.alchemy.com/v2/0S348eV1_NOus-eNlxalOiTz7RXRotXz'
    arb_contract_address = '0x489ee077994b6658eafa855c308275ead8097c4a'

    decrease_position_topic = '0x93d75d64d1f84fc6f430a64fc578bdd4c1e090e90ea2d51773e626d19de56d30'
    increase_position_topic = '0x2fe68525253654c21998f35787a8d0f361905ef647c854092430ab65f2f15022'
    liquidate_position_topic = '0x2e1f85a64a2f22cf2f0c42584e7c919ed4abe8d53675cff0f62bf1e95a1c676f'
    filter_topics = [increase_position_topic, decrease_position_topic, liquidate_position_topic]

    def start_requests(self):
        yield scrapy.Request(url=self.arb_base_url, method='POST', body=json.dumps({
            "id": 1,
            "jsonrpc": "2.0",
            "method": "eth_blockNumber"
        }), headers={
            "accept": "application/json",
            "content-type": "application/json"
        }, callback=self.parse_first)

    @catch_except
    def parse_first(self, response):
        block_number = response.json()['result']
        print(block_number)

        pre_block_number = rds.getex(self.name, 'block_number')
        rds.setex(self.name, 'block_number', block_number, ttl=60 * 60 * 24 * 2)

        if not pre_block_number:
            return

        pre_block_number = hex(int(pre_block_number, 16) + 1)
        print(pre_block_number, block_number)

        for topic in self.filter_topics:
            yield scrapy.Request(url=self.arb_base_url, method='POST', body=json.dumps({
                "id": 1,
                "jsonrpc": "2.0",
                "method": "eth_getLogs",
                "params": [
                    {
                        "address": [
                            self.arb_contract_address
                        ],
                        "fromBlock": pre_block_number,
                        "toBlock": block_number,
                        "topics": [
                            topic
                        ]
                    }
                ]
            }), headers = {
                "accept": "application/json",
                "content-type": "application/json"
            }, callback=self.parse_second)

    @catch_except
    def parse_second(self, response):
        result_list = response.json()['result']
        print('---------------------------------')
        for result in result_list :
            log_name = ''
            if result['topics'][0] == self.increase_position_topic:
                log_name = 'increase_position'
            elif result['topics'][0] == self.decrease_position_topic:
                log_name = 'decrease_position'
            elif result['topics'][0] == self.liquidate_position_topic:
                log_name = 'liquidate_position'

            parse_result = self.parse_log_data(log_name, result['data'][2:])
            parse_result['tx_hash'] = result['transactionHash']
            parse_result['size_usd'] =  humanize_float_en(parse_result['sizeDelta'] / (10 ** 30), 2)
            parse_result['price_usd'] =  round(parse_result['price'] / (10 ** 30), 2)
            parse_result['token_size'] = humanize_float_en(parse_result['sizeDelta'] / parse_result['price'], 2)
            if parse_result['collateralDelta'] != 0:
                parse_result['leverage'] = humanize_float_en(parse_result['sizeDelta'] / parse_result['collateralDelta'], 1)
            parse_result['chain'] = 'Arbitrum'

            if parse_result['indexTokenName'] in ('LINK', 'UNI') and parse_result['sizeDelta'] / parse_result['price'] > 10000 : # LINK / UNI need position token size over 10,000
                print(Template(self.alert_cn_template()).render(parse_result))
                print(Template(self.alert_en_template()).render(parse_result))
            elif parse_result['sizeDelta'] / (10 ** 30) > 300000 : # BTC / ETH need position usd size over $300,000
                print(Template(self.alert_cn_template()).render(parse_result))
                print(Template(self.alert_en_template()).render(parse_result))

    # parse log function
    def get_token_name(self, address):
        if address == 'f97f4df75117a78c1a5a0dbb814af92458539fb4' :
            return "LINK"
        elif address == '82af49447d8a07e3bd95bd0d56f35241523fbab1':
            return "WETH"
        elif address == 'ff970a61a04b1ca14834a43f5de4533ebddb5cc8':
            return "USDC"
        elif address == '2f2a2543b76a4166549f7aab2e75bef0aefc5b0f':
            return "WBTC"
        elif address == 'fa7f8980b0f1e64a2062791cc3b0871572f1f7f0':
            return "UNI"
        elif address == 'fd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9':
            return "USDT"
        elif address == 'da10009cbd5d07dd0cecc66161fc93d7c9000da1':
            return "DAI"
        elif address == '17fc002b466eec40dae837fc4be5c67993ddbd6f':
            return "FRAX"

    def get_item_value(self, data, index):
        return data[64 * index:64 * (index+1)]


    def parse_log_data(self, log_name, data):
        if log_name == 'increase_position' or log_name == 'decrease_position':
            return {
                'key': self.get_item_value(data, 0),
                'account': '0x' + self.get_item_value(data, 1)[24:],
                'collateralTokenName': self.get_token_name(self.get_item_value(data, 2)[24:]),
                'indexTokenName': self.get_token_name(self.get_item_value(data, 3)[24:]),
                'collateralDelta': int(self.get_item_value(data, 4), 16),
                'sizeDelta': int(self.get_item_value(data, 5), 16),
                'isLong': int(self.get_item_value(data, 6)),
                'price': int(self.get_item_value(data, 7), 16),
                'fee': int(self.get_item_value(data, 8), 16),
                'type': log_name
            }
        elif log_name == 'liquidate_position':
            return {
                'key': self.get_item_value(data, 0),
                'account': '0x' + self.get_item_value(data, 1)[24:],
                'collateralTokenName': self.get_token_name(self.get_item_value(data, 2)[24:]),
                'indexTokenName': self.get_token_name(self.get_item_value(data, 3)[24:]),
                'isLong': int(self.get_item_value(data, 4)),
                'sizeDelta': int(self.get_item_value(data, 5), 16),
                'collateralDelta': int(self.get_item_value(data, 6), 16),
                'price': int(self.get_item_value(data, 9), 16),
            }


    # alert function
    def alert_cn_template(self):
        return '''
        {% if type == 'increase_position' %}
        据 KingData 监控，GMX 协议在 {{chain}} 上新开 {{token_size}} {{indexTokenName}}(${{size_usd}}) {% if isLong %}多{% else %}空{% endif %}单。   
        开仓价格：${{price_usd}}
        杠杆倍数：{{leverage}}x
        开仓账户: {{account}}  
        TX ID: https://arbiscan.io/tx/{{tx_hash}}

        {% elif  type == "decrease_position" %}
        据 KingData 监控，GMX 协议在 {{chain}} 上平仓 {{token_size}} {{indexTokenName}}(${{size_usd}}) {% if isLong %}多{% else %}空{% endif %}单。   
        平仓价格：${{price_usd}}
        平仓账户: {{account}}                            
        TX ID: https://arbiscan.io/tx/{{tx_hash}}

        {% elif type == 'liquidate_position' %}
        据 KingData 监控，GMX 协议在 {{chain}} 链上 {{token_size}} {{indexTokenName}}(${{size_usd}}) {% if isLong %}多{% else %}空{% endif %}单被清算。
        清算价格：${{price_usd}}
        清算账户: {{account}} 
        TX ID: https://arbiscan.io/tx/{{tx_hash}}
        {% endif %}
        '''

    def alert_en_template(self):
        return '''
        {% if type in ("increase_position", 'decrease_position') %}
        According to KingData monitoring，GMX protocol on {{chain}} have {% if type == "increase_position" %}opened large {% if isLong %}long{% else %}short{% endif %} positions{% else %}closed large {% if isLong %}long{% else %}short{% endif %} positions{% endif %}.
        {% if type == "increase_position" %}Open {% if isLong %}long{% else %}short{% endif %} positions{% else %}Close {% if isLong %}long{% else %}short{% endif %} positions{% endif %} token is {{indexTokenName}}, positions size: {% if isLong %}{% if type == 'increase_position' %}+{% else %}-{% endif %}{% else %}{% if type == 'increase_position' %}-{% else %}+{% endif %}{% endif %}{{token_size}} {{indexTokenName}} (${{size_usd}}){% if type == "increase_position" %}, leverage is {{leverage}}x.{% else %}.{% endif %}
        {{indexTokenName}} current price: ${{price_usd}}
        {% elif type == 'liquidate_position' %}
        According to KingData monitoring, the GMX protocol on {{chain}} has been large liquidations.
        Liquidated info：
        Direction：{% if isLong %}Long{% else %}Short{% endif %}
        Position size: {{token_size}} {{indexTokenName}}（${{size_usd}}）
        Liquidated Price: ${{price_usd}}
        {% endif %}
        Account: {{account}}
        TX ID: https://arbiscan.io/tx/{{tx_hash}}
        '''