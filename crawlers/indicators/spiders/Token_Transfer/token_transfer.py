# -*- coding: utf-8 -*
import time
from crawlers.utils import SpiderBase
from crawlers.utils.get_address_tag import GetAddressTag
from crawlers.utils.redis_conn import rds
from crawlers.utils.group_alarm import catch_except
import orjson
from crawlers.utils.humanize import humanize_float_cn, humanize_float_en
from jinja2 import Template

# 每1分钟爬取一次
class WhaleAlertSpider(SpiderBase):
    name = 'whale_alert'
    allowed_domains = ['whale-alert.io'],
    redis_cache_cursor_key = 'whale_alert_at_'
    start_timestamp = int(time.time())
    cex_address_tag = {}
    user_address_tag = {}

    def __init__(self, *args, **kwargs):
        super(WhaleAlertSpider, self).__init__(*args, **kwargs)
        
        _get_cex_address_tag = GetAddressTag('cex')
        self.cex_address_tag = _get_cex_address_tag.get_tag_json()

        _get_user_address_tag = GetAddressTag('user')
        self.user_address_tag = _get_user_address_tag.get_tag_json()

        ts = int(time.time()) - 20 * 60
        self.start_urls = [
            'https://api.whale-alert.io/v1/transactions?api_key=ioR1YEJi29Iy1BHUE2vvZbSKNtbxbBKM&start=%i' % ts]

    @catch_except
    def parse(self, response):
        body = orjson.loads(response.text)
        messages = 'success'
        if body['result'] != "success":
            code = 1
            messages = "whale 数据爬取失败，原因如下: " + body
            self.logger.info(messages)
        else:
            txes = body["transactions"]
            self.logger.info(f'本次抓取数量：{len(txes)}')
            for i in txes:
                if not (i and i.get('from') and i.get('to')) :
                    return
                else :
                    self.assign_address_tag(i, 'from')
                    self.assign_address_tag(i, 'to')

                i['amount_cn'] = humanize_float_cn(i['amount'])
                i['amount_en'] = humanize_float_en(i['amount'])
                i['amount_usd_cn'] = humanize_float_cn(i['amount_usd'])
                i['amount_usd_en'] = humanize_float_en(i['amount_usd'])
                i['from_owner_cn'] = "未知钱包" if i['from']['owner'] == 'unknown' else i['from']['owner'] 
                i['from_owner_en'] = "Unknown Wallet" if i['from']['owner'] == 'unknown' else i['from']['owner']
                i['to_owner_cn'] = "未知钱包" if i['to']['owner'] == 'unknown' else i['to']['owner']
                i['to_owner_en'] = "Unknown Wallet" if i['to']['owner'] == 'unknown' else i['to']['owner']

                # Filter intra-exchange transfers
                if i['from']['owner_type'] == 'exchange' and i['to']['owner_type'] == 'exchange' and i['from']['owner'] == i['to']['owner']:
                    print('Filter intra-exchange transfers')
                    continue

                if i['from']['owner_type'] == 'exchange' or i['to']['owner_type'] == 'exchange' :
                    if i['symbol'] in ['btc', 'eth', 'usdt', 'usdc', 'busd']:
                        print('bitcoin transfer must over 1,000, eth transfer must over 10,000, stablecoin must over 30,000,000',i['symbol'], i['amount'])
                        if (i['symbol'] == 'btc' and i['amount'] < 1000) or (i['symbol'] == 'eth' and i['amount'] < 10000):
                            continue
                        elif i['amount_usd'] < 10000000 :
                            continue
                    else:
                        print('altcoin must over $5,000,000',i['symbol'], i['amount_usd'])
                        if i['amount_usd'] < 1000000 :
                            continue
                    print(Template(self.alert_exhange_transfer_en_template()).render(i))
                    print(Template(self.alert_exhange_transfer_cn_template()).render(i))
                else :
                    if i['symbol'] in ['btc', 'eth', 'usdt', 'usdc', 'busd']:
                        print('bitcoin transfer must over 1,000, eth transfer must over 10,000, stablecoin must over 30,000,000',i['symbol'], i['amount'])
                        if (i['symbol'] == 'btc' and i['amount'] < 1000) or (i['symbol'] == 'eth' and i['amount'] < 10000):
                            continue
                        elif i['amount_usd'] < 10000000 :
                            continue
                    else:
                        print('altcoin must over $500,000',i['symbol'], i['amount_usd'])
                        if i['amount_usd'] < 1000000 :
                            continue
                    print(Template(self.alert_whale_transfer_en_template()).render(i))
                    print(Template(self.alert_whale_transfer_cn_template()).render(i))

                # Avoid repeated notification
                # if rds.getex(self.name, f'{self.redis_cache_cursor_key}:{i["hash"]}'):
                #     continue                

                # rds.setex(self.name, f'{self.redis_cache_cursor_key}:{i["hash"]}', value=time.time(), ttl=60 * 60)


    def assign_address_tag(self, tx_obj, to_or_from):
        if tx_obj[to_or_from]['owner_type'] == 'unknown':
            if tx_obj[to_or_from]['address'] in self.cex_address_tag :
                if tx_obj['blockchain'] in self.cex_address_tag[tx_obj[to_or_from]['address']] :
                    tx_obj[to_or_from]['owner'] = self.cex_address_tag[tx_obj[to_or_from]['address']][tx_obj['blockchain']]
                    tx_obj[to_or_from]['owner_type'] = 'exchange'
                else :
                    tx_obj[to_or_from]['owner'] == 'unknown'
            elif tx_obj[to_or_from]['address'] in self.user_address_tag :
                if tx_obj['symbol'] in self.user_address_tag[tx_obj[to_or_from]['address']] :
                    tx_obj[to_or_from]['owner'] = self.user_address_tag[tx_obj[to_or_from]['address']][tx_obj['symbol']]
                    tx_obj[to_or_from]['owner_type'] = 'whale_user'
                else :
                    tx_obj[to_or_from]['owner'] == 'unknown'
        else :
            tx_obj[to_or_from]['owner'] == 'unknown'

    # exchange
    def alert_exhange_transfer_en_template(self):
        return """
According to KingData monitoring，{{amount_en}} #{{symbol | upper}} transferred from {{from_owner_en}}{% if from['owner_type'] == 'exchange' %} Exchange{% endif %}{% if from['owner_type'] == 'whale_user' %} Whale{% endif %} to {{to_owner_en}}{% if to['owner_type'] == 'exchange' %} Exchange {% endif %}{% if to['owner_type'] == 'whale_user' %} Whale{% endif %}. Total value: ${{amount_usd_en}}。
"""

    def alert_exhange_transfer_cn_template(self):
        return """
据 KingData 数据监控，{{amount_cn}}枚 {{symbol | upper}} 从 {{from_owner_cn}}{% if from['owner_type'] == 'exchange' %}交易所{% endif %}{% if from['owner_type'] == 'whale_user' %}大户{% endif %} 转入到 {{to_owner_cn}}{% if to['owner_type'] == 'exchange' %}交易所{% endif %}{% if to['owner_type'] == 'whale_user' %}大户{% endif %}，总价值 ${{amount_usd_cn}}。
"""

    # whale
    def alert_whale_transfer_en_template(self):
        return """
According to KingData monitoring，{{amount_en}} #{{symbol | upper}} transferred from {{from_owner_en}}{% if from['owner_type'] == 'whale_user' %} Whale{% endif %} to {{to_owner_en}}{% if to['owner_type'] == 'whale_user' %} Whale {% endif %}. Total value: ${{amount_usd_en}}。
"""

    def alert_whale_transfer_cn_template(self):
        return """
据 KingData 数据监控，{{amount_cn}}枚 {{symbol | upper}} 从 {{from_owner_cn}}{% if from['owner_type'] == 'whale_user' %}大户{% endif %} 转入到 {{to_owner_cn}}{% if to['owner_type'] == 'whale_user' %}大户{% endif %}，总价值 ${{amount_usd_cn}}。
"""

    def blockchain_url(self, params):
        blockchain = params['blockchain']
        hash = params['hash']
        if blockchain == 'bitcoin':
            return f'https://btc.com/{hash}'
        if blockchain == 'ethereum':
            return f'https://etherscan.io/tx/0x{hash}'
        if blockchain == 'ripple':
            return f'https://xrpscan.com/tx/{hash}'
        if blockchain == 'eos':
            return f'https://eosflare.io/tx/{hash}'
        if blockchain == 'tron':
            return f'https://tronscan.org/#/transaction/{hash}'
        if blockchain == 'binancechain':
            return f'https://binance.mintscan.io/txs/{hash}'
        return ''
