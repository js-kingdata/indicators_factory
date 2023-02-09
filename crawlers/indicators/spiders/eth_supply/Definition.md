<!--
 * @Author: suski shuciqi@gmail.com
 * @Date: 2023-02-09 02:57:24
 * @LastEditors: suski shuciqi@gmail.com
 * @LastEditTime: 2023-02-09 05:06:57
 * @FilePath: /indicators_factory_eth2/crawlers/indicators/spiders/eth_supply/Definition.md
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
-->
## Support Language (Required)

EN & CN

## Indicator Name (Required)

EN: ETH Supply Amount
CN：ETH 供应量监控

## Why Create This Indicator (Optional)

EN: This indicator broadcasts the latest ETH supply chain, destruction, and deflation on a daily basis.

CN: 本指标每日播报 ETH 最新供应链、销毁量、通缩情况。

## Indicator Category (Optional)

ETH

## Free or VIP (Required)

Free

## Indicator Chain (Optional)

Eth

## Indicator Data Source (Optional)

https://ultrasound.money/

## Indicator Alert Frequency (Required)

8am(UTC+8), Daily

## Indicator Alert logic (Required)

1、Every day at 8am(UTC+8), the latest supply amount is nitification

## Indicator Alert Demo (Required)

EN

```
According to KingData monitoring, the annualized growth rate of ETH yesterday was {{inflation_rate}} ({{inflation_state_en}}). It has been {{consecutive_state_en}} consecutive days. Approximately {{change_amount}} were {{change_action_en}} yesterday, current total circulation amount is {{circulation_amount}}.
```

CN

```
据 KingData 监控，昨日 ETH 年化增长率为 {{inflation_rate}}（{{inflation_state_cn}}）。已连续 {{consecutive_state_cn}}。昨日共{{change_action_cn}}约：{{change_amount}}， 当前流通总量为：{{circulation_amount}}。
```