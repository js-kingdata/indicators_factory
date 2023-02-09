<!--
 * @Author: suski shuciqi@gmail.com
 * @Date: 2023-02-08 14:03:11
 * @LastEditors: suski shuciqi@gmail.com
 * @LastEditTime: 2023-02-09 05:08:12
 * @FilePath: /indicators_factory_eth2/crawlers/indicators/spiders/eth2_staking_amount/Definition.md
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
-->
## Support Language (Required)

EN & CN

## Indicator Name (Required)

EN: ETH2.0 Staking Amount
CN：ETH2.0 锁仓异动监控

## Why Create This Indicator (Optional)

EN: Real-time monitoring of ETH2.0 locked positions. The latest number of locked positions is broadcasted regularly every day, as well as in case of large variances.

CN: 实时监控 ETH2.0 锁仓情况。每日定时播报最新锁仓数量，如有大额异动时也会及时播报。

## Indicator Category (Optional)

ETH2.0

## Free or VIP (Required)

Free

## Indicator Chain (Optional)

Eth

## Indicator Data Source (Optional)

https://ultrasound.money/

## Indicator Alert Frequency (Required)

8am(UTC+8), Daily

## Indicator Alert logic (Required)

1、Every day at 8am(UTC+8), the latest staking amount is nitification

## Indicator Alert Demo (Required)

EN

```
According to KingData monitoring, in the past {{interval}}, ETH2.0 staking amount raise {{amount_1}} ETH, current total staking amount is {{amount_2}} ETH, {{staking_ratio}} of total circulation.
```

CN

```
据 KingData 监控，过去 {{interval}}，ETH2.0 锁仓数额上涨 {{amount_1}} ETH，当前总锁仓量为 {{amount_2}} ETH，占总流通量比例为 {{staking_ratio}}。
```