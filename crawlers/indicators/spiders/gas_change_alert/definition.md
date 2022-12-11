<!--
 * @Author: suski shuciqi@gmail.com
 * @Date: 2022-12-11 05:41:13
 * @LastEditors: suski shuciqi@gmail.com
 * @LastEditTime: 2022-12-11 05:51:00
 * @FilePath: /indicators_factory/crawlers/indicators/spiders/gas_change_alert/definition.md
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
-->
## Support Language (Required)

EN & CN

## Indicator Name (Required)

- EN: Gas Change Alert
- CN: Gas 异动监控


## Why Create This Indicator (Optional)


## Indicator Category (Optional)


## Free or VIP (Required)

Free

## Indicator Chain (Optional)


## Indicator Data Source (Optional)


## Indicator Alert Frequency (Required)

5 min

## Indicator Alert logic (Required)

Monitor every 5 minutes and broadcast when gas rises/falls and meets the following conditions:
- 5 minutes with a 10% variation
- 1 hour with a variation of up to 30%
- 50% change within 1 day

## Indicator Alert Demo (Required)

- EN: ETH gas change alert, gas change within 5 minutes up to 14%, the current gas is 15 GWEI.
- CN: ETH 链 Gas 异动提醒，5 分钟内 Gas 变化达 14%，当前 Gas 为 15 GWEI。