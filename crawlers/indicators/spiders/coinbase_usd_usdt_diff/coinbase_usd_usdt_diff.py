import json

import scrapy
import time
from datetime import datetime
from crawlers.utils import SpiderBase, rds
from crawlers.utils.group_alarm import catch_except
from jinja2 import Template
from crawlers.utils.humanize import humanize_float_en


class M0MoneyMonitor(SpiderBase):
    name = 'coinbase_usd_usdt_diff'
    start_urls = {
        'https://api.exchange.coinbase.com/products/BTC-USDT/ticker':'USDT', 
        'https://api.exchange.coinbase.com/products/BTC-USD/ticker':'USD'
    }
    params = {}

    def start_requests(self):
        for url in self.start_urls.keys() :
            yield scrapy.Request(url=url, cb_kwargs={'token_name':self.start_urls[url]})

    @catch_except
    def parse(self, response, **kwargs):
        data = response.json()
        token_name = kwargs['token_name']

        self.params[token_name + "_price"] = data['price']
        self.params[token_name + "_time"] = datetime.strptime(data['time'], '%Y-%m-%dT%H:%M:%S.%fZ').timestamp()

        print(self.params)

    def closed(self, reason):
        pre_alert_params = rds.getex(self.name, 'params')
        alert_params = {}

        alert_params['diff_price'] = round(float(self.params['USD_price']) - float(self.params['USDT_price']), 2)
        alert_params['diff_price_percent'] = round(alert_params['diff_price'] * 100 / float(self.params['USDT_price']), 4)
        alert_params['alert_timestamp'] = int(self.params['USD_time'])

        day_timestamp = 60 * 60 * 24

        if pre_alert_params is not None :
            pre_alert_params = json.loads(pre_alert_params.replace("'", '"'))
            percent_diff = 0
            
            if rds.getex(self.name, 'break_params') is not None : # 如果之前播报过突破文案，则本次和突破内容对比。否则和每日定时播报内容对比
                pre_break = json.loads(rds.getex(self.name, 'break_params').replace("'", '"'))
                percent_diff = float(alert_params['diff_price_percent']) - float(pre_break['diff_price_percent'])
            else :
                percent_diff = float(alert_params['diff_price_percent']) - float(pre_alert_params['diff_price_percent'])
            
            alert_params['direction'] = 1 if percent_diff >= 0 else 0
            if abs(percent_diff) > 1 : # 如果比上次播报再次波动 1% 以上，进行突破播报
                rds.setex(self.name, 'break_params', str(alert_params), int(pre_alert_params['alert_timestamp'] + day_timestamp - alert_params['alert_timestamp'])) # 突破参数保存，避免重复播报突破，到期时间和下方保持一致
                print(Template(self.breakup_alert_cn_template()).render(alert_params))
        
        else :
            rds.setex(self.name, 'params', str(alert_params), day_timestamp) # 设置一天的有效期，一天内的信息都会走上面的 if 判断。保证 else 的模块一天至少执行一次
            print(Template(self.alert_cn_template()).render(alert_params))

    def alert_cn_template(self):
        return """
        据 KingData 数据监控，Coinbase【BTCUSD - BTCUSDT】今日溢价数据如下
        溢价金额为：${{diff_price}}
        溢价率为：{{diff_price_percent}}%
        """
    
    def breakup_alert_cn_template(self):
        return """
        据 KingData 数据监控，Coinbase【BTCUSD - BTCUSDT】溢价短时突破{% if direction == 1 %}上涨{% else %}下跌{% endif %}。
        溢价金额为：${{diff_price}}
        溢价率为：{{diff_price_percent}}%
        """
    
    def alert_en_template(self):
        return """
        According to the data monitoring of KingData, the premium data of Coinbase 【BTCUSD - BTCUSDT】 today is as follows: 
        The premium amount is: ${{diff_price}} 
        The premium rate is: {{diff_price_percent}}%
        """
    
    def breakup_alert_en_template(self):
        return """
        According to the data monitoring of KingData, the premium of Coinbase 【BTCUSD - BTCUSDT】broke through {% if direction == 1 %}upward{% else %}downward{% endif %}. 
        The premium amount is: ${{diff_price}}
        The premium rate is: {{diff_price_percent}}%
        """