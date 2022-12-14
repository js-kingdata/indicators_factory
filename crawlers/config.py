from environs import Env
from urllib.parse import urljoin

env = Env()

""" REDIS """
REDIS_URL = env.str('REDIS_URL', 'redis://127.0.0.1:6379/0')

"""账号密码token配置"""
DEEPL_AUTO_KEY = env.str('DEEPL_AUTO_KEY', '5aa68096-d3a1-0456-b0da-c0c73fdfa16d')  # deepl秘钥
KD_INTERNAL_TOKEN = env.str('KD_INTERNAL_TOKEN',
                            default='eyJpdiI6ImNpeUxlZXBrTk1UdFZnOTRKS1ROenc9PSIsInZhbHVlIjoiYnZ3NTJWeXY2YW45UnNDOFFxN21NYTRMZDhWemwyM2hGZmo5MlZrQ0dhQ09xNkJlU3h2bmtFMEdtZ0dXMlVxbyIsIm1iOGEwMWY0MTXmN2AIEq')


DEBUG = env.bool('DEBUG', False)
PROXY_URL = env.str('PROXY_URL', None)

TIME_OUT = 10
PROXY = ''



# """URL配置"""
KD_API_HOST = env.str('KD_API_HOST', default='http://kingdata.com')
KD_INTERNAL_API = f"{KD_API_HOST}/internal_api/v1"
