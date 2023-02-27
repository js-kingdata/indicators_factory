## Support Language (Required)

EN & CN

## Indicator Name (Required)

EN: GMX protocol positions monitor 
CN：【GMX 协议】大额开平仓监控

## Why Create This Indicator (Optional)

EN: Real-time monitoring of GMX protocol positions changes, timely notify of on-chain contract large order information.

CN: 实时监控 GMX 协议大额开平仓异动，及时播报链上合约大单信息。

## Indicator Category (Optional)

交易衍生品

## Free or VIP (Required)

前期限免，后期收费

## Indicator Chain (Optional)

Arbitrum

## Indicator Data Source (Optional)

读取原生智能合约

## Indicator Alert Frequency (Required)

1 min

## Indicator Alert logic (Required)

实时监控

## Indicator Alert Demo (Required)

EN
'''
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
'''

CN
'''
{% if type in ("increase_position", 'decrease_position') %}
据 KingData 监控，GMX 协议在 {{chain}} 上完成大额{% if type == "increase_position" %}开{% if isLong %}多{% else %}空{% endif %}仓{% else %}平{% if isLong %}多{% else %}空{% endif %}仓{% endif %}。
{% if type == "increase_position" %}开{% if isLong %}多{% else %}空{% endif %}仓{% else %}平{% if isLong %}多{% else %}空{% endif %}仓{% endif %}币种为：{{indexTokenName}}，合约价值为：{% if isLong %}{% if type == 'increase_position' %}+{% else %}-{% endif %}{% else %}{% if type == 'increase_position' %}-{% else %}+{% endif %}{% endif %}{{token_size}} {{indexTokenName}} (${{size_usd}}){% if type == "increase_position" %}，杠杆倍数为：{{leverage}}x。{% else %}。{% endif %}
{{indexTokenName}} 当前价格：${{price_usd}}
{% elif type == 'liquidate_position' %}
据 KingData 监控，GMX 协议在 {{chain}} 出现大额合约清算。
清算合约为：
合约方向：做{% if isLong %}多{% else %}空{% endif %}
合约价值：{{token_size}} {{indexTokenName}}（${{size_usd}}）
清算价格：${{price_usd}}
{% endif %}
'''