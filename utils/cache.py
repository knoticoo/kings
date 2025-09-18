"""
Cache utilities for King's Choice Management App

Provides caching decorators and utilities for API responses.
"""

from datetime import datetime, timedelta
from functools import wraps

# Simple in-memory cache for API responses
api_cache = {}

def cache_response(timeout_seconds=30):
    """Decorator to cache API responses"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f"{f.__name__}_{str(args)}_{str(kwargs)}"
            now = datetime.now()
            
            # Check if cached response exists and is still valid
            if cache_key in api_cache:
                cached_data, timestamp = api_cache[cache_key]
                if now - timestamp < timedelta(seconds=timeout_seconds):
                    return cached_data
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            api_cache[cache_key] = (result, now)
            
            # Clean old cache entries
            for key in list(api_cache.keys()):
                if now - api_cache[key][1] > timedelta(seconds=timeout_seconds * 2):
                    del api_cache[key]
            
            return result
        return decorated_function
    return decorator