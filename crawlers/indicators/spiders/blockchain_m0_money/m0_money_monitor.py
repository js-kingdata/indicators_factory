import json

import scrapy
import time
import datetime
from crawlers.utils import SpiderBase, rds
from crawlers.utils.group_alarm import catch_except
from jinja2 import Template
from crawlers.utils.humanize import humanize_float_en


class M0MoneyMonitor(SpiderBase):
    name = 'm0_money_monitor'
    start_urls = {
        'https://stablecoins.llama.fi/stablecoincharts/all?stablecoin=1':'USDT', 
        'https://stablecoins.llama.fi/stablecoincharts/all?stablecoin=2':'USDC'
    }
    params = {}

    def start_requests(self):
        for url in self.start_urls.keys() :
            yield scrapy.Request(url=url, cb_kwargs={'token_name':self.start_urls[url]})

    @catch_except
    def parse(self, response, **kwargs):
        data = response.json()
        token_name = kwargs['token_name']

        self.params[token_name + "_totalCirculatingUSD"] = data[-1]['totalCirculatingUSD']['peggedUSD']
        self.params[token_name + "_24H_change"] = data[-1]['totalCirculatingUSD']['peggedUSD'] - data[-2]['totalCirculatingUSD']['peggedUSD']
        self.params[token_name + "_24H_change_percent"] = round(100 * self.params[token_name + "_24H_change"] / data[-2]['totalCirculatingUSD']['peggedUSD'], 2)
        self.params[token_name + "_7D_change"] = data[-1]['totalCirculatingUSD']['peggedUSD'] - data[-8]['totalCirculatingUSD']['peggedUSD']
        self.params[token_name + "_7D_change_percent"] = round(100 * self.params[token_name + "_7D_change"] / data[-8]['totalCirculatingUSD']['peggedUSD'], 2)
        self.params[token_name + "_30D_change"] = data[-1]['totalCirculatingUSD']['peggedUSD'] - data[-31]['totalCirculatingUSD']['peggedUSD']
        self.params[token_name + "_30D_change_percent"] = round(100 * self.params[token_name + "_30D_change"] / data[-31]['totalCirculatingUSD']['peggedUSD'], 2)

        print(self.params)

    def closed(self, reason):
        self.params['totalCirculatingUSD'] = humanize_float_en(self.params["USDT_totalCirculatingUSD"] + self.params["USDC_totalCirculatingUSD"], 2)
        self.params["change_24H"] = humanize_float_en(self.params["USDT_24H_change"] + self.params["USDC_24H_change"], 2)

        for key in ('USDT_totalCirculatingUSD', 'USDT_24H_change', 'USDT_7D_change', 'USDT_30D_change', 'USDC_totalCirculatingUSD', 'USDC_24H_change', 'USDC_7D_change', 'USDC_30D_change'):
            self.params[key] = humanize_float_en(self.params[key], 2)

        print(Template(self.alert_cn_template()).render(self.params))


    # must be declare
    def alert_en_template(self):
        return """
        According to the KingData data monitoring, today's M0 on the chain is: ${{totalCirculatingUSD}}, with a 24-hour change of: ${{change_24H}}.
        Detailed data is as follows:
        The total amount of USDT is: ${{USDT_totalCirculatingUSD}}.
        USDT change (24H/7D/30D): {{USDT_24H_change}} / {{USDT_7D_change}} / {{USDT_30D_change}}.
        USDT change rate (24H/7D/30D): {{USDT_24H_change_percent}}% / {{USDT_7D_change_percent}}% / {{USDT_30D_change_percent}}%.
        -----
        The total amount of USDC is: ${{USDC_totalCirculatingUSD}}.
        USDC change (24H/7D/30D): {{USDC_24H_change}} / {{USDC_7D_change}} / {{USDC_30D_change}}.
        USDC change rate (24H/7D/30D): {{USDC_24H_change_percent}}% / {{USDC_7D_change_percent}}% / {{USDC_30D_change_percent}}%.
        """

    # must be declare
    def alert_cn_template(self):
        return """
        据 KingData 数据监控，今日链上 M0 总量为：${{totalCirculatingUSD}}，24H 变化量为：${{change_24H}}
        详细数据如下：
        USDT 总量为：${{USDT_totalCirculatingUSD}}
        USDT 变化量（24H/7D/30D）：{{USDT_24H_change}} / {{USDT_7D_change}} / {{USDT_30D_change}} 
        USDT 变化率（24H/7D/30D）：{{USDT_24H_change_percent}}% / {{USDT_7D_change_percent}}% / {{USDT_30D_change_percent}}%
        -----
        USDC 总量为：${{USDC_totalCirculatingUSD}}
        USDC 变化量（24H/7D/30D）：{{USDC_24H_change}} / {{USDC_7D_change}} / {{USDC_30D_change}} 
        USDC 变化率（24H/7D/30D）：{{USDC_24H_change_percent}}% / {{USDC_7D_change_percent}}% / {{USDC_30D_change_percent}}%
        """
