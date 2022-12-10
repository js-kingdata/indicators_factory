import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".."))

BOT_NAME = 'indicators'

SPIDER_MODULES = ['indicators.spiders']
NEWSPIDER_MODULE = 'indicators.spiders'

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS = 32

DOWNLOAD_DELAY = 1
DOWNLOAD_TIMEOUT = 15

CONCURRENT_REQUESTS_PER_DOMAIN = 16 
CONCURRENT_REQUESTS_PER_IP = 4  


AUTOTHROTTLE_MAX_DELAY = 30