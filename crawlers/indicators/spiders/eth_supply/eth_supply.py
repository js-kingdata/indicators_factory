'''
Author: suski shuciqi@gmail.com
Date: 2023-02-09 02:57:41
LastEditors: suski shuciqi@gmail.com
LastEditTime: 2023-02-09 05:01:33
FilePath: /indicators_factory_eth2/crawlers/indicators/spiders/eth_supply/eth_supply.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import scrapy

from crawlers.utils import SpiderBase, rds
from jinja2 import Template
from crawlers.utils.group_alarm import catch_except
import time
from crawlers.utils.humanize import humanize_float_en

class ETH_Supply(SpiderBase):
    name = 'eth_supply'

    start_urls = ['https://ultrasound.money/api/v2/fees/supply-changes']

    @catch_except
    def parse(self, response, **kwargs):
        data = response.json()
        if not data or len(data) < 1 :
            return
        else :
            self.process(data)

    def process(self, data):
        circulation_amount = int(data['d1']['to_supply']) / 10 ** 18
        change_amount = int(data['d1']['change']) / 10 ** 18
        change_action_cn = '增发' if change_amount > 0 else '销毁'
        change_action_en = 'issued' if change_amount > 0 else 'burned'
        inflation_state_cn = '通胀状态' if change_amount > 0 else '通缩状态'
        inflation_state_en = 'inflation' if change_amount > 0 else 'deflation'
        inflation_rate = '%.4f%%' % (change_amount * 365 * 100 / circulation_amount)

        consecutive_state = rds.getex(self.name, 'consecutive_state')
        consecutive_day = 0 if rds.getex(self.name, 'consecutive_day') is None else int(rds.getex(self.name, 'consecutive_day'))

        if change_amount >= 0 :
            if consecutive_state is None :
                consecutive_day = 1
            elif consecutive_state == 'inflation' :
                consecutive_day += 1
            elif consecutive_state == 'deflation' :
                consecutive_day = 1
            consecutive_state = 'inflation'
        else :
            if consecutive_state is None :
                consecutive_day = 1
            elif consecutive_state == 'inflation' :
                consecutive_day = 1
            elif consecutive_state == 'deflation' :
                consecutive_day += 1
            consecutive_state = 'deflation'

        # 按照你这个逻辑，这个key 就不能让他失效，应该一直存在才行
        rds.setex(self.name, 'consecutive_state', consecutive_state)
        rds.setex(self.name, 'consecutive_day', str(consecutive_day))

        consecutive_state_cn, consecutive_state_en = self.consecutive_state_func(consecutive_state, str(consecutive_day))

        params = {
            'inflation_rate': inflation_rate,
            'inflation_state_cn': inflation_state_cn,
            'inflation_state_en': inflation_state_en,
            'consecutive_state_cn': consecutive_state_cn,
            'consecutive_state_en': consecutive_state_en,
            'circulation_amount': humanize_float_en(round(circulation_amount, 2)),
            'change_amount': format(float('%.2f' % change_amount), ','),
            'change_action_cn': change_action_cn,
            'change_action_en': change_action_en
        }

        print(Template(self.alert_en_template()).render(params))
        print(Template(self.alert_cn_template()).render(params))

    def consecutive_state_func(self, state, day) :
        if state == 'inflation' :
            return day+' 日通胀', 'inflation for ' + day
        else :
            return day+' 日通缩', 'deflation for ' + day

    def alert_en_template(self):
        return "According to KingData monitoring, the annualized growth rate of ETH yesterday was {{inflation_rate}} ({{inflation_state_en}}). It has been {{consecutive_state_en}} consecutive days. Approximately {{change_amount}}ETH were {{change_action_en}} yesterday, current total circulation amount is {{circulation_amount}}ETH."

    def alert_cn_template(self):
        return "据 KingData 监控，昨日 ETH 年化增长率为 {{inflation_rate}}（{{inflation_state_cn}}）。已连续 {{consecutive_state_cn}}。昨日共{{change_action_cn}}约：{{change_amount}} 枚ETH， 当前流通总量为：{{circulation_amount}} 枚ETH。"