# KingData Open Platform

## Introduction

KingData is a platform focusing on data monitoring and broadcasting in the Web3. Currently, the platform has opened 500+ indicators for users to choose, covering various subdivisions, and is determined to become a necessary data monitoring platform for Web3 users. Let industry users not miss any data fluctuations that they care about.

In order to provide more valuable data change services to industry users, KingData has opened an open platform for indicator development. Any developer can easily write their favorite data change monitoring indicators according to the specifications of this open platform. 

KingData Open Platform are recipes to build high level indicators that users care about most, like large NFT Trade, large transfers of Token etc. Indicator write in _Python_.

Developers can set their own indicators to be VIP or Free.

### Free

Everyone can follow and use it for free. After following, they will automatically receive the data broadcast.

### VIP

1. Users need to pay to become a platform VIP before they can use follow. 
2. Developers of VIP indicators can get 50% revenue sharing from VIP indicators every month.

## How to develop an indicator

Steps to develop indicators on KingData:
1. Fork this repository. 
2. Add a new folder in /crawlers/indicators/spiders/ with the new indicator name. 
3. Write the indicator's description file in the new folder: definition.md. 
4. Create a new crawler file in this directory to realize the indicator requirement logic of definition.md. 
5. Write broadcast template to render the params that logic code return.
6. Test and submit the changes on your fork to the indicators repository as a Pull Request with a brief description of the changes you made. 
7. Waiting for someone to comment or merge your merge request. There is no need to have someone check your PR as it is regularly monitored. 
8. Once your PR is merged, please give the front-end team 24 hours to load your listing on the UI.

## Attention && FAQ

See [Attention && FAQ](https://open.kingdata.com/attention-and-and-faq)

## Indicator Development Tutorial

See [KingData Open Platform](https://open.kingdata.com/)

## Indicator Development Progress
Join [KingData Dework](https://app.dework.xyz/kingdata-17178)
