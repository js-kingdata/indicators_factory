import json, time
import requests
import scrapy
from crawlers.utils import SpiderBase, rds
from jinja2 import Template
from crawlers.utils.group_alarm import catch_except
from crawlers.utils.humanize import humanize_float_en

class DexSwapAlert(SpiderBase):
    name = 'dex_swap_alert'

    binance_symbol_list = {}

    binance_url = 'https://api.binance.com/api/v3/ticker/price'

    uniswap_v3 = {
                    "project_name": 'uniswap_v3',
                    "query_url":'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3',
                    "query_latest_block": '''
                                            {
                                                swaps(
                                                    orderBy: transaction__blockNumber
                                                    orderDirection: asc
                                                    first: 1
                                                    where: {timestamp_gt: "%s"}
                                                ) {
                                                    transaction {
                                                        blockNumber
                                                    }
                                                }
                                            }''' % int(time.time()-600), # Subtract 600 seconds to ensure that the block is already confirm
                    "query_swaps": '''
                                    {
                                        swaps(
                                            where: {
                                                transaction_: {
                                                    blockNumber_gt: "%s", 
                                                    blockNumber_lte: "%s"
                                                }
                                            }
                                            orderBy: logIndex
                                            orderDirection: asc
                                        ) {
                                            logIndex
                                            token0 {
                                                symbol
                                            }
                                            token1 {
                                                symbol
                                            }
                                            amount0
                                            amount1
                                            transaction {
                                                id
                                                blockNumber
                                            }
                                            origin
                                        }
                                    }'''
                }
    
    dex_projects = [uniswap_v3]

    def parse_binance_symbol(self, symbol_json): # 获取行情数据，最终输出一个字典类型，key 为 symbol，value 为价格
        for symbol in symbol_json :
            if symbol['symbol'][-4:] == 'USDT':
                symbol['symbol'] = symbol['symbol'][:-4]
                self.binance_symbol_list[symbol['symbol']] = symbol['price']
        
        self.binance_symbol_list['WETH'] = self.binance_symbol_list['ETH']
        self.binance_symbol_list['WBTC'] = self.binance_symbol_list['BTC']


    @catch_except
    def start_requests(self):
        resp = requests.get(self.binance_url)
        self.parse_binance_symbol(json.loads(resp.text)) # 获取行情数据

        for dex in self.dex_projects :
            yield scrapy.Request(url=dex['query_url'], method='POST', 
                                body=json.dumps({"query": dex['query_latest_block']}),
                                callback=self.parse_blockNum,
                                cb_kwargs=dex)


    @catch_except
    def parse_blockNum(self, response, **dex): # 获取最新 blockNum，结合本地存储 blockNum，不断获取新数据
        current_blockNum = response.json()['data']['swaps'][0]['transaction']['blockNumber']
        # pre_blockNum = rds.get(f"{self.name}:{dex['project_name']}:blockNum")
        # rds.set(f"{self.name}:{dex['project_name']}:blockNum", current_blockNum, 60 * 60)

        pre_blockNum = 16814041
        current_blockNum = 16814042

        if not pre_blockNum:
            return
        
        print(f"开始爬取 {pre_blockNum}  -  {current_blockNum} 之间的 swap 数据")

        yield scrapy.Request(url=dex['query_url'], method='POST',
                            body=json.dumps({
                                "query": dex['query_swaps'] % (pre_blockNum, current_blockNum)
                            }),
                            callback=self.parse_swaps,
                            cb_kwargs={"project_name": dex['project_name']})


    @catch_except
    def parse_swaps(self, response, **dex): # 解析 swaps 数据
        swaps = response.json()['data']['swaps']

        swap_dic = {} # swaps 处理后的字典，key 为 tx_id, value 为 swap 字段
        swap_filter_dic = {}

        print(f"一共爬取到 {len(swaps)} 条数据")
        for swap in swaps :
            # 根据币种类型，处理交易 type，分为：alt_coin_trade 和
            trade_type = 'alt_coin_trade'
            mainstream_coin = ('WBTC', 'WETH', 'USDT', 'USDC', 'DAI', 'BUSD')
            if (swap['token0']['symbol'] in mainstream_coin) and (swap['token1']['symbol'] in mainstream_coin):
                trade_type = 'mainstream_coin_trade'

            # dex 里面到代币，名称没有换回来
            if swap['token0']['symbol'] == 'LUNA':
                swap['token0']['symbol'] = 'LUNC'
            if swap['token1']['symbol'] == 'LUNA':
                swap['token1']['symbol'] = 'LUNC'

            tx_id = swap['transaction']['id']
            if tx_id in swap_dic.keys(): # 如果当前 tx_id 已经存在过，则进行头尾相接，合成一个 swap
                if float(swap_dic[tx_id]['amount0']) < 0 : # amount<0 则代表需要拼接的 swap 中一定有一个数值绝对值相同并且 >0，则需要找到这个新 swap 中对应的另一个 symbol 的内容，进行替换
                    if float(swap['amount0']) > 0 and float(swap_dic[tx_id]['amount0']) == -float(swap['amount0']):
                        swap_dic[tx_id]['amount0'] = swap['amount1']
                        swap_dic[tx_id]['symbol0'] = swap['token1']['symbol']
                    elif float(swap['amount1']) > 0 and float(swap_dic[tx_id]['amount0']) == -float(swap['amount1']):
                        swap_dic[tx_id]['amount0'] = swap['amount0']
                        swap_dic[tx_id]['symbol0'] = swap['token0']['symbol']
                else :
                    if float(swap['amount0']) > 0 and float(swap_dic[tx_id]['amount1']) == -float(swap['amount0']):
                        swap_dic[tx_id]['amount1'] = swap['amount1']
                        swap_dic[tx_id]['symbol1'] = swap['token1']['symbol']
                    elif float(swap['amount1']) > 0 and float(swap_dic[tx_id]['amount1']) == -float(swap['amount1']):
                        swap_dic[tx_id]['amount1'] = swap['amount0']
                        swap_dic[tx_id]['symbol1'] = swap['token0']['symbol']
            else : # 如果当前 tx_id 还未存在过，则添加进去
                swap_dic[tx_id] = {
                    'symbol0': swap['token0']['symbol'],
                    'amount0': swap['amount0'],
                    'symbol1': swap['token1']['symbol'],
                    'amount1': swap['amount1'],
                    'sender': swap['origin'],
                    'project_name': dex['project_name'],
                    'trade_type': trade_type,
                    'blockNumber': swap['transaction']['blockNumber']
                }
            
                filter_tag = swap['transaction']['blockNumber'] + '_' + swap['origin'] # 把同一个 blockNumber 里面，同一个 sender 执行了多笔交易的情况标记出来。这种不会是手动操作，肯定是调用了特殊合约 或者 批量发起
                
                if filter_tag in swap_filter_dic.keys() : # 增加一个过滤的 dic
                    swap_filter_dic[filter_tag] += 1
                else :
                    swap_filter_dic[filter_tag] = 0

        # swap 处理好之后，计算每个 swap 的 value
        for tx_id in swap_dic.keys() :
            
            filter_tag = swap_dic[tx_id]['blockNumber'] + '_' + swap_dic[tx_id]['sender']
            if swap_filter_dic[filter_tag] > 0 : # 如果是同一个 block 多笔的情况，进行过滤
                print("过滤："+tx_id)
                swap_dic[tx_id] = 'pass_swap'
                continue

            if swap_dic[tx_id]['symbol0'] in self.binance_symbol_list:
                swap_dic[tx_id]['value0'] = float(self.binance_symbol_list[swap_dic[tx_id]['symbol0']]) * float(swap_dic[tx_id]['amount0'])
                swap_dic[tx_id]['symbol0_price'] = float(self.binance_symbol_list[swap_dic[tx_id]['symbol0']])
            else :
                swap_dic[tx_id]['value0'] = 0
            
            if swap_dic[tx_id]['symbol1'] in self.binance_symbol_list:
                swap_dic[tx_id]['value1'] = float(self.binance_symbol_list[swap_dic[tx_id]['symbol1']]) * float(swap_dic[tx_id]['amount1'])
                swap_dic[tx_id]['symbol1_price'] = float(self.binance_symbol_list[swap_dic[tx_id]['symbol1']])
            else :
                swap_dic[tx_id]['value1'] = 0


            if swap_dic[tx_id]['value1'] > 0 and swap_dic[tx_id]['value0'] > 0 : # 如果两个 symbol 都有价值，则取最小值作为过滤条件
                swap_dic[tx_id]['value'] = round(abs(swap_dic[tx_id]['value1']) if abs(swap_dic[tx_id]['value1']) < abs(swap_dic[tx_id]['value0']) else abs(swap_dic[tx_id]['value0']), 2)
            else : # 如果不是两个 value 都有价值，则取大值做过滤条件
                swap_dic[tx_id]['value'] = round(abs(swap_dic[tx_id]['value1']) if abs(swap_dic[tx_id]['value1']) > abs(swap_dic[tx_id]['value0']) else abs(swap_dic[tx_id]['value0']), 2)

        self.alert_process(swap_dic)


    def alert_process(self, swap_dic) :
        for tx_id, swap in swap_dic.items():
            if swap == 'pass_swap' :
                continue

            swap['tx_id'] = tx_id
            # 交易 symbo，0 为买入 1 为卖出
            if float(swap['amount0']) > 0 :
                temp_amount = swap['amount0']
                temp_symbol = swap['symbol0']
                temp_price = swap.get('symbol0_price') or 0
                temp_value = swap.get('value0') or 0
                swap['amount0'] = abs(float(swap['amount1']))
                swap['symbol0'] = swap['symbol1']
                swap['symbol0_price'] = swap.get('symbol1_price') or 0
                swap['value0'] = swap['value1']
                swap['amount1'] = float(temp_amount)
                swap['symbol1'] = temp_symbol
                swap['symbol1_price'] = temp_price
                swap['value1'] = temp_value
            else :
                swap['amount0'] = abs(float(swap['amount0']))
                swap['amount1'] = float(swap['amount1'])

            # 根据交易类型做过滤
            if swap['trade_type'] == 'mainstream_coin_trade' and swap['value'] >= 3000000:  # 3000000
                self.foramt_swap(swap)
                # Tools.multilingual_information_flow_push(tmp_name='DEX_SWAP_TRACKER', params= swap, origin_url=f'https://etherscan.io/tx/{swap["tx_id"]}')

                print(Template(self.alert_en_template()).render(swap))
                print(Template(self.alert_cn_template()).render(swap))
            elif swap['trade_type'] == 'alt_coin_trade' and swap['value'] >= 300000: #300000
                self.foramt_swap(swap)
                # Tools.multilingual_information_flow_push(tmp_name='DEX_SWAP_TRACKER', params= swap, origin_url=f'https://etherscan.io/tx/{swap["tx_id"]}')

                print(Template(self.alert_en_template()).render(swap))
                print(Template(self.alert_cn_template()).render(swap))

    def foramt_swap(self, params):
        params['origin_value0'] = abs(params.get('value0') or 0)
        params['amount0'] = humanize_float_en(float(params['amount0']))
        params['value0'] = humanize_float_en(abs(float(params.get('value0') or 0)))
        params['symbol0_price'] = round(float(params.get('symbol0_price') or 0), 2) if params.get('symbol0_price') else None
        params['origin_value1'] = abs(params.get('value1') or 0)
        params['amount1'] = humanize_float_en(float(params['amount1']))
        params['value1'] = humanize_float_en(abs(float(params.get('value1') or 0)))
        params['symbol1_price'] = round(float(params.get('symbol1_price') or 0), 2) if params.get('symbol1_price') else None
        return params;

    def alert_en_template(self):
        return '''
According to KingData monitoring, {{amount1}} {{symbol1}}{% if origin_value1 > 1 %}(${{value1}}){% endif %} has just been swaped into {{amount0}} {{symbol0}}{% if origin_value0 > 1 %}(${{value0}}){% endif %}.
Sell/Quantity/Price: {{symbol1}} ｜ {{amount1}} | {% if symbol1_price %}${{symbol1_price}}{% else %}-{% endif %}
Buy/Quantity/Price: {{symbol0}} ｜ {{amount0}} | {% if symbol0_price %}${{symbol0_price}}{% else %}-{% endif %}
Account: {{sender}}
        '''
    
    def alert_cn_template(self):
        return '''
据 KingData 监控，刚刚 {{amount1}} {{symbol1}}{% if origin_value1 > 1 %}(${{value1}}){% endif %} 兑换成 {{amount0}} {{symbol0}}{% if origin_value0 > 1 %}(${{value0}}){% endif %}。
卖出币种/数量/价格：{{symbol1}} ｜ {{amount1}} | {% if symbol1_price %}${{symbol1_price}}{% else %}-{% endif %}
买入币种/数量/价格：{{symbol0}} ｜ {{amount0}} | {% if symbol0_price %}${{symbol0_price}}{% else %}-{% endif %}
交易用户：{{sender}}
        '''