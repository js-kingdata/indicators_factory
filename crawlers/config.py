from environs import Env

env = Env()

""" REDIS """
REDIS_URL = env.str('REDIS_URL', 'redis://127.0.0.1:6379/0')

DEBUG = env.bool('DEBUG', False)
PROXY_URL = env.str('PROXY_URL', None)

TIME_OUT = 10
PROXY = ''
