import arrow
import requests
import scrapy

from crawlers.config import DEBUG, PROXY_URL, KD_INTERNAL_TOKEN, KD_INTERNAL_API
from crawlers.utils.group_alarm import information_flow_synchronization
from crawlers.utils.redis_conn import rds


class SpiderBase(scrapy.Spider):

    def error_back(self, failure):
        if DEBUG:
            print(f"Spider Error: {repr(failure)}")
            return

    def get_curent_price(self, coin):
        data = requests.get(url=f'https://api.binance.com/api/v3/ticker/24hr?symbol={coin}USDT').json()
        return float(data['c'])


class Tools:
    """
    公共工具类
    代码中需要重复使用的函数
    """

    # @rds.thing_lock('proxy_pools')
    @classmethod
    def proxy_http(cls, proxy_url=PROXY_URL):
        proxy = rds.srandmember('proxy_pools')
        if proxy:
            proxy_url = str(proxy[0], encoding="utf-8")
        return {'http': proxy_url, 'https': proxy_url}

    @classmethod
    def now_timestamp_offset(cls, offset: float = 0, times: float = 1):
        """
        当前时间戳前后offset量的时间
        :param offset: 偏移量(s)
        :param times: 倍数
        :return: 偏移后的时间戳
        """
        return (arrow.now().timestamp() + offset) * times

    @classmethod
    def rate_of_change(cls, v1, v2, ndigits=6, times: int = 1):
        """
        计算变化率

        :param v1:旧值/初始值
        :param v2:新值/现值
        :param ndigits:保留的小数位
         :param times: 倍数
        :return:
        """
        return round(((v2 - v1) / v1) * times, ndigits)

    @classmethod
    def multilingual_information_flow_push(cls, tmp_name: str, params: dict, template_id: int, origin_url: str = '',
                                           image_urls: list = None, active=None):
        """
        信息流推送
        :param tmp_name: 模板名称
        :param params: 模板参数
        :param origin_url: 原文链接
        :param image_urls: 图片链接
        :param active: 已激活的语言类型
        :return: None
        """
        start = False
        print('指标 %s 发送预警内容：%s' % (template_id, params))
        if active is None:
            active = ['en', 'cn']
        response = requests.post(
            url=f'{KD_INTERNAL_API}/generic_post',
            json={
                'template_id': template_id,
                'active_en': 'en' in active,
                'active_cn': 'cn' in active,
                'origin_url': origin_url,
                'params': params,
                'image_urls': image_urls,
            },
            headers={'Authorization': f'Token {KD_INTERNAL_TOKEN}'}
        )
        start = (response.status_code == 200)
        information_flow_synchronization(
            tmp_name=tmp_name,
            chart_id=template_id,
            params=params,
            origin_url=origin_url,
            start=start
        )
