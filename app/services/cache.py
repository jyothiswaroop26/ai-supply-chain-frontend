"""
API Cache Module
Provides caching functionality for API responses to improve performance.
"""

import json
import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional, Any, Dict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class APICache:
    """Simple file-based cache for API responses."""
    
    def __init__(self, cache_dir: str = ".cache", ttl: int = 300):
        """
        Initialize the cache.
        
        Args:
            cache_dir: Directory to store cache files
            ttl: Time-to-live for cached items in seconds
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        self.ttl = ttl
        self.logger = logger
    
    def _get_cache_key(self, endpoint: str, params: Optional[Dict]) -> str:
        """Generate a cache key for an endpoint and parameters."""
        key_data = f"{endpoint}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the file path for a cache key."""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Any]:
        """
        Get a cached response.
        
        Args:
            endpoint: API endpoint
            params: Request parameters
            
        Returns:
            Cached data if found and not expired, None otherwise
        """
        try:
            cache_key = self._get_cache_key(endpoint, params)
            cache_path = self._get_cache_path(cache_key)
            
            if not cache_path.exists():
                return None
            
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache has expired
            cached_at = datetime.fromisoformat(cache_data['cached_at'])
            if datetime.now() - cached_at > timedelta(seconds=self.ttl):
                self.logger.debug(f"Cache expired for {endpoint}")
                cache_path.unlink()
                return None
            
            self.logger.debug(f"Cache hit for {endpoint}")
            return cache_data['data']
            
        except Exception as e:
            self.logger.error(f"Cache read error: {e}")
            return None
    
    def set(self, endpoint: str, data: Any, params: Optional[Dict] = None) -> bool:
        """
        Cache a response.
        
        Args:
            endpoint: API endpoint
            data: Data to cache
            params: Request parameters
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cache_key = self._get_cache_key(endpoint, params)
            cache_path = self._get_cache_path(cache_key)
            
            cache_data = {
                'endpoint': endpoint,
                'cached_at': datetime.now().isoformat(),
                'data': data
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f)
            
            self.logger.debug(f"Cached response for {endpoint}")
            return True
            
        except Exception as e:
            self.logger.error(f"Cache write error: {e}")
            return False
    
    def clear(self, endpoint: Optional[str] = None):
        """
        Clear cache entries.
        
        Args:
            endpoint: If provided, clear only cache for this endpoint
        """
        try:
            if endpoint:
                # Clear cache for specific endpoint
                for cache_file in self.cache_dir.glob("*.json"):
                    with open(cache_file, 'r') as f:
                        data = json.load(f)
                        if data['endpoint'] == endpoint:
                            cache_file.unlink()
                self.logger.info(f"Cleared cache for {endpoint}")
            else:
                # Clear all cache
                for cache_file in self.cache_dir.glob("*.json"):
                    cache_file.unlink()
                self.logger.info("Cleared all cache")
                
        except Exception as e:
            self.logger.error(f"Cache clear error: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            total_size = sum(f.stat().st_size for f in cache_files)
            
            return {
                'total_entries': len(cache_files),
                'total_size_kb': round(total_size / 1024, 2),
                'cache_dir': str(self.cache_dir),
                'ttl_seconds': self.ttl
            }
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {e}")
            return {}


class MemoryCache:
    """In-memory cache for API responses (fast but session-scoped)."""
    
    def __init__(self, ttl: int = 300):
        """
        Initialize the memory cache.
        
        Args:
            ttl: Time-to-live for cached items in seconds
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl
        self.logger = logger
    
    def _get_cache_key(self, endpoint: str, params: Optional[Dict]) -> str:
        """Generate a cache key for an endpoint and parameters."""
        key_data = f"{endpoint}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Any]:
        """
        Get a cached response.
        
        Args:
            endpoint: API endpoint
            params: Request parameters
            
        Returns:
            Cached data if found and not expired, None otherwise
        """
        cache_key = self._get_cache_key(endpoint, params)
        
        if cache_key not in self.cache:
            return None
        
        cached_at = self.cache[cache_key]['cached_at']
        if datetime.now() - cached_at > timedelta(seconds=self.ttl):
            del self.cache[cache_key]
            return None
        
        self.logger.debug(f"Memory cache hit for {endpoint}")
        return self.cache[cache_key]['data']
    
    def set(self, endpoint: str, data: Any, params: Optional[Dict] = None) -> bool:
        """
        Cache a response in memory.
        
        Args:
            endpoint: API endpoint
            data: Data to cache
            params: Request parameters
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cache_key = self._get_cache_key(endpoint, params)
            self.cache[cache_key] = {
                'endpoint': endpoint,
                'cached_at': datetime.now(),
                'data': data
            }
            self.logger.debug(f"Cached in memory for {endpoint}")
            return True
        except Exception as e:
            self.logger.error(f"Memory cache error: {e}")
            return False
    
    def clear(self, endpoint: Optional[str] = None):
        """
        Clear cache entries.
        
        Args:
            endpoint: If provided, clear only cache for this endpoint
        """
        if endpoint:
            keys_to_delete = [k for k, v in self.cache.items() if v['endpoint'] == endpoint]
            for k in keys_to_delete:
                del self.cache[k]
            self.logger.info(f"Cleared memory cache for {endpoint}")
        else:
            self.cache.clear()
            self.logger.info("Cleared all memory cache")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'total_entries': len(self.cache),
            'cache_type': 'memory'
        }
