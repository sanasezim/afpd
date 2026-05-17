from cachetools import TTLCache

# Кэш на 20 минут
cache = TTLCache(maxsize=500, ttl=1200)