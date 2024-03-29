import scrapy

from crawlers.utils import SpiderBase, rds
from jinja2 import Template
from crawlers.utils.group_alarm import catch_except
import time
from crawlers.utils.humanize import humanize_float_en

class ETH2Staking(SpiderBase):
    name = 'eth2_staking'

    start_urls = ['https://ultrasound.money/api/fees/scarcity']

    @catch_except
    def parse(self, response, **kwargs):
        data = response.json()
        if not data or len(data) < 1 :
            return
        else :
            self.process(data)

    def process(self, data):
        staking_amount = int(data['engines']['staked']['amount'][:-1]) / 10**18
        staking_ratio = staking_amount * 10**18 / (int(data['ethSupply'][:-1]) +
                                                    int(data['engines']['locked']['amount']) -
                                                    int(data['engines']['burned']['amount'][:-1]))

        pre_staking_amount = rds.getex(self.name, 'staking_amount')
        pre_time = rds.getex(self.name, 'time')

        amount_1 = 0
        interval = 0

        if pre_staking_amount is None :
            # 第一次的时候，没有比较值，所以第一次暂时不播报
            return True;
        else :
            amount_1 = staking_amount - float(pre_staking_amount)

        rds.setex(self.name, 'staking_amount', str(staking_amount), 60 * 60 * 24 * 2)

        if pre_time is None :
            interval = '24H'
        else :
            interval = int(float(time.time())) - int(float(pre_time))
            interval = str(int(interval / (60 * 60)) + 1) + 'H'

        rds.setex(self.name, 'time', str(time.time()), 60 * 60 * 24 * 2)

        params = {
            "interval": interval,
            "direction": amount_1 > 0,
            "amount_1": humanize_float_en(round(amount_1, 2)),
            "amount_2": humanize_float_en(round(staking_amount, 2)),
            "staking_ratio": '%.2f%%' % (staking_ratio * 100)
        }

        print(Template(self.alert_en_template()).render(params))
        print(Template(self.alert_cn_template()).render(params))

    def alert_en_template(self):
        return "According to KingData monitoring, in the past {{interval}}, ETH2.0 staking amount {% if direction %}increased{% else %}reduced{% endif %} by {{amount_1}} ETH, current total staking amount is {{amount_2}} ETH, {{staking_ratio}} of total circulation."

    def alert_cn_template(self):
        return "据 KingData 监控，过去 {{interval}}，ETH2.0 锁仓数额{% if direction %}增加{% else %}减少{% endif %} {{amount_1}} ETH，当前总锁仓量为 {{amount_2}} ETH，占总流通量比例为 {{staking_ratio}}。"