import redis

from cybernexvpn.cybernexvpn_bot import config

r = redis.Redis(host=config.REDIS_HOST, port=6379, decode_responses=True)
