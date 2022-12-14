import json

from crawlers.indicators.spiders.exchange_notice_monitoring import announcement_push, added_id_check
from crawlers.utils import SpiderBase, Tools
from zhconv import convert
import scrapy
from lxml import etree
import time
import datetime
from crawlers.utils.group_alarm import catch_except
from jinja2 import Template
from crawlers.utils.redis_conn import rds

class ExchangeNoticeMonitoring(SpiderBase):
    name = 'exchange_notice_monitoring'
    exchange_name = 'Binance'
    headers = {
        'lang': 'zh-CN',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko)",
        'referer': 'https://www.binance.com/zh-CN/support/announcement/c-49?navId=49',
    }

    def start_requests(self):
        binance_url = [
            'https://www.binance.com/bapi/composite/v1/public/cms/article/list/query?type=1&pageSize=5&pageNo=1',
        ]
        yield scrapy.Request(url=binance_url[0], headers=self.headers, callback=self.parse)

    @catch_except
    def parse(self, response):
        data = response.json()['data']
        # 解析逻辑
        for announcement_group in data['catalogs']:
            # 遍历所有文章，是否满足播报要求
            # 今天日期
            today = datetime.date.today()
            # 昨天时间
            yesterday = today - datetime.timedelta(days=1)
            # 昨天开始时间戳
            yesterday_start_time = int(time.mktime(time.strptime(str(yesterday), '%Y-%m-%d')))
            # 昨天结束时间戳
            yesterday_end_time = (int(time.mktime(time.strptime(str(today), '%Y-%m-%d'))) - 1)

            for announcement in announcement_group['articles']:
                if added_id_check(self.name, self.exchange_name, str(announcement['id']), 60 * 60 * 24 * 2):
                    continue
                if not (yesterday_start_time <= announcement['releaseDate'] // 1000 <= yesterday_end_time):
                    continue

                yield scrapy.Request(
                    url=f"https://www.binance.com/en/support/announcement/{announcement['code']}",
                    callback=self.detail_page_analysis,
                    errback=self.error_back,
                    headers=self.headers,
                    meta={
                        'new_values': {
                            'exchange': self.exchange_name,
                            'title': convert(announcement['title'], 'zh-cn'),
                            'code': announcement['code'],
                            'bulletin_id': announcement['id'],
                        }
                    }
                )


    @catch_except
    def detail_page_analysis(self, response):
        ori_data = etree.HTML(response.text)
        datas = json.loads(ori_data.xpath("//script[@id='__APP_DATA']/text()")[0])['routeProps']['debb'][
            'articleDetail']
        response.meta['new_values'].update({
            'body': self.dictionary_analysis(json.loads(datas['body'])),
            'timestamp': datas['publishDate'] // 1000
        })
        # 输出对象
        template = announcement_push(
            new_save=response.meta['new_values'],
            origin_url=response.url
        )
        # 渲染输出, 替换成推送
        print(Template(self.alert_cn_template()).render(template['params']['cn']))
        print(Template(self.alert_en_template()).render(template['params']['en']))

        print(template)
        # Tools.multilingual_information_flow_push(
        #     template_id=template['template_id'],
        #     origin_url=template['origin_url'],
        #     params=template['params']
        # )


    def dictionary_analysis(self, dic, delimiter: str = '\n'):
        """
        字典转文本（递归）
        :param dic:
        :param delimiter:
        :return:
        """
        if dic.get('tag', '') == 'figure':
            return '🪧 Table display is not currently supported'
        if 'child' in dic:
            return delimiter.join([self.dictionary_analysis(sub_d, '') for sub_d in dic['child']])
        return dic.get('text', '')

    # must be declare
    def alert_en_template(self):
        return """{{exchange_name}}: {{title}}
{{content}}
Original link: {{origin_url}}
"""

    # must be declare
    def alert_cn_template(self):
        return """{{exchange_name}}: {{title}}
{{content}}
原文链接: {{origin_url}}
"""
