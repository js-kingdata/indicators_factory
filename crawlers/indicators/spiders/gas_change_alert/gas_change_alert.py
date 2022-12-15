'''
Author: suski shuciqi@gmail.com
Date: 2022-12-11 06:23:40
LastEditors: suski shuciqi@gmail.com
LastEditTime: 2022-12-11 09:06:01
FilePath: /indicators_factory/crawlers/indicators/spiders/gas_change_alert/gas_change_alert.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import scrapy
import json
import os
from scrapy.http import JsonRequest
import time
from jinja2 import Template


class GasChangeAlertSpider(scrapy.Spider):
    name = 'gas_change_alert'
    allowed_domains = ['alchemy.com']
    start_urls = ['']
    gas_historical_data = {}

    def _readHistoricalData(self):
        with open(os.path.dirname(os.path.abspath(__file__)) + '/gas_historical_data.json', 'r') as f:
            self.gas_historical_data = json.load(f)
    
    def _writeHistoricalData(self):
        with open(os.path.dirname(os.path.abspath(__file__)) + '/gas_historical_data.json', 'w') as wf :
            json.dump(self.gas_historical_data, wf)

    def __init__(self, name=None, **kwargs):
        self._readHistoricalData()
        super().__init__(name, **kwargs)

    def start_requests(self):
        body = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "eth_gasPrice"
        }
        url = 'https://eth-mainnet.g.alchemy.com/v2/fKxV02otHQ0FBuYiMQrVR_6PubYUvXJV'
        yield JsonRequest(url, data=body, callback=self.parse)

    def parse(self, response):
        response_json = json.loads(response.body.decode())
        current_time = time.time()
        params = {
            "period_time_en": 'none',
            "period_time_cn": 'none',
            "change_percent": 'none',
            "current_gas": 'none'
        }

        if int(self.gas_historical_data['5min']['time']) + 6 * 60 < current_time :
            self.gas_historical_data['5min']['time'] = current_time
            self.gas_historical_data['5min']['gas'] = int(response_json['result'], 16)
        else :
            if self.gas_historical_data['5min']['gas'] * 1.1 < int(response_json['result'], 16) or self.gas_historical_data['5min']['gas'] * 0.9 > int(response_json['result'], 16) :
                print("播报 5 分钟模板")
                self.gas_historical_data['5min']['time'] = current_time
                self.gas_historical_data['5min']['gas'] = int(response_json['result'], 16)
                params['period_time_en'] = '5min'
                params['period_time_cn'] = '5 分钟'
                params['change_percent'] = round((int(response_json['result'], 16) - self.gas_historical_data['5min']['gas']) / self.gas_historical_data['5min']['gas'], 2) + '%'
                params['current_gas'] = int(response_json['result'], 16)


        if int(self.gas_historical_data['1hour']['time']) + 61 * 60 < current_time :
            self.gas_historical_data['1hour']['time'] = current_time
            self.gas_historical_data['1hour']['lowest_gas'] = int(response_json['result'], 16)
            self.gas_historical_data['1hour']['highest_gas'] = int(response_json['result'], 16)
        else :
            self.gas_historical_data['1hour']['time'] = current_time
            if (self.gas_historical_data['1hour']['highest_gas'] * 1.1 < int(response_json['result'], 16) or self.gas_historical_data['1hour']['lowest_gas'] * 0.9 > int(response_json['result'], 16)) and params['period_time_en'] == 'none':
                params['period_time_en'] = '1hour'
                params['period_time_cn'] = '1 小时'
                params['current_gas'] = int(response_json['result'], 16)
                if self.gas_historical_data['1hour']['highest_gas'] * 1.1 < int(response_json['result'], 16) :
                    params['change_percent'] = round((int(response_json['result'], 16) - self.gas_historical_data['1hour']['highest_gas']) / self.gas_historical_data['1hour']['highest_gas'], 2) + '%'
                else :
                    params['change_percent'] = round((int(response_json['result'], 16) - self.gas_historical_data['1hour']['lowest_gas']) / self.gas_historical_data['1hour']['lowest_gas'], 2) + '%'

            if self.gas_historical_data['1hour']['highest_gas'] < int(response_json['result'], 16) :
                self.gas_historical_data['1hour']['highest_gas'] = int(response_json['result'], 16)
            
            if self.gas_historical_data['1hour']['lowest_gas'] > int(response_json['result'], 16) :
                self.gas_historical_data['1hour']['lowest_gas'] = int(response_json['result'], 16)


        if int(self.gas_historical_data['1day']['time']) + 24* 61 * 60 < current_time :
            self.gas_historical_data['1day']['time'] = current_time
            self.gas_historical_data['1day']['lowest_gas'] = int(response_json['result'], 16)
            self.gas_historical_data['1day']['highest_gas'] = int(response_json['result'], 16)
        else :
            self.gas_historical_data['1day']['time'] = current_time
            if (self.gas_historical_data['1day']['highest_gas'] * 1.1 < int(response_json['result'], 16) or self.gas_historical_data['1day']['lowest_gas'] * 0.9 > int(response_json['result'], 16)) and params['period_time_en'] == 'none':
                params['period_time_en'] = '1day'
                params['period_time_cn'] = '1 天'
                params['current_gas'] = int(response_json['result'], 16)
                if self.gas_historical_data['1day']['highest_gas'] * 1.1 < int(response_json['result'], 16) :
                    params['change_percent'] = round((int(response_json['result'], 16) - self.gas_historical_data['1day']['highest_gas']) / self.gas_historical_data['1day']['highest_gas'], 2) + '%'
                else :
                    params['change_percent'] = round((int(response_json['result'], 16) - self.gas_historical_data['1day']['lowest_gas']) / self.gas_historical_data['1day']['lowest_gas'], 2) + '%'

            if self.gas_historical_data['1day']['highest_gas'] < int(response_json['result'], 16) :
                self.gas_historical_data['1day']['highest_gas'] = int(response_json['result'], 16)
            
            if self.gas_historical_data['1day']['lowest_gas'] > int(response_json['result'], 16) :
                self.gas_historical_data['1day']['lowest_gas'] = int(response_json['result'], 16)

        self._writeHistoricalData()

        if params['period_time_en'] != 'none':
            print("ETH gas change alert, gas change within {period_time_en} up to {change_percent}, the current gas is {current_gas} GWEI.".format(period_time_en=params['period_time_en'], change_percent=params['change_percent'], current_gas=params['change_percent']))
            print("ETH 链 Gas 异动提醒，{period_time_cn} 内 Gas 变化达 {change_percent}，当前 Gas 为 {current_gas} GWEI。".format(period_time_cn=params['period_time_cn'], change_percent=params['change_percent'], current_gas=params['change_percent']))

    def alert_en_template(self):
        return "ETH gas change alert, gas change within {{ period_time_en }} up to {{ change_percent }}, the current gas is {{ current_gas }} GWEI."

    def alert_cn_template(self):
        return "ETH 链 Gas 异动提醒，{{ period_time_cn }} 内 Gas 变化达 {{ change_percent }}，当前 Gas 为 {{ current_gas }} GWEI。"