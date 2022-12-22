## Support Language (Required)

EN & CN

## Indicator Name (Required)

TVL change monitoring of TOP DeFi projects

## Why Create This Indicator (Optional)

A change in the TVL of a project often affects the price of the next Token of the project. So when the TVL changes, users want to know the first time

## Indicator Category (Optional)

DeFi

## Free or VIP (Required)

Free

## Indicator Chain (Optional)

None

## Indicator Data Source (Optional)

https://defillama.com/chains

## Indicator Alert Frequency (Required)

6pm Daily

## Indicator Alert logic (Required)

1、Project TVL > $100M

and

2、TVL 1d change > 20%(up or down) or TVL 7d changes > 50%(up or down) or TVL 7d changes > 100%(up or down)

## Indicator Alert Demo (Required)

EN

```
According to KingData monitoring, in the past {{interval}} days, {{project_name}}'s TVL {{% if interval_change > 0%}} increased {{% else %}} decreased {{% endif %}} {{ interval_change }}%.   

Project name: {{ project_name }}    
Category: {{ category }}   
Token: {{ symbol }}    
Official Website: {{ url }}   
Current TVL: {{ tvl }}   
TVL(24H%): {{ change_1d }}%   
TVL(7D%): {{ change_7d }}%   
TVL(30D%): {{ change_30d }}%   
```

CN

```
据 KingData 监控，过去 {{interval}} 天, {{project_name}} 的 TVL {{% if interval_change > 0%}}上涨{{% else %}}下跌{{% endif %}} {{ interval_change }}%。   

项目名称: {{ project_name }}   
项目类别: {{ category }}   
Token: {{ symbol }}   
官网链接: {{ url }}  
当前 TVL: {{ tvl }}    
TVL(24H%): {{ change_1d }}   
TVL(7D%): {{ change_7d }}   
TVL(30D%): {{ change_30d }}  
```

