from django.core.cache import cache


def get_or_set_cache(key, callback, timeout=60):
    data = cache.get(key)
    if not data:
        data = callback()
        cache.set(key, data, timeout)
    return data
