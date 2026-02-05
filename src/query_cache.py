"""
Query Cache Manager - Caches queries and responses for improved performance
"""
import json
import hashlib
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import threading


@dataclass
class CacheEntry:
    """Represents a cached query entry"""
    query_hash: str
    query: str
    response: str
    model_used: str
    timestamp: float
    hit_count: int
    last_accessed: float
    metadata: Dict[str, Any]
    ttl_seconds: float
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired"""
        return time.time() - self.timestamp > self.ttl_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """Create from dictionary"""
        return cls(**data)


class QueryCache:
    """Manages query caching with expiration and eviction policies"""
    
    def __init__(self, 
                 cache_dir: str = "cache",
                 max_entries: int = 1000,
                 default_ttl: int = 3600,
                 enable_persistence: bool = True):
        """
        Initialize the query cache
        
        Args:
            cache_dir: Directory to store cache files
            max_entries: Maximum number of entries in memory cache
            default_ttl: Default time-to-live in seconds (1 hour)
            enable_persistence: Whether to persist cache to disk
        """
        self.cache_dir = Path(cache_dir)
        self.max_entries = max_entries
        self.default_ttl = default_ttl
        self.enable_persistence = enable_persistence
        
        # In-memory cache
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        
        # Statistics
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        
        # Create cache directory if needed
        if self.enable_persistence:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._load_from_disk()
    
    def _generate_hash(self, query: str, model: str = "", context: str = "") -> str:
        """
        Generate a unique hash for a query
        
        Args:
            query: The query string
            model: The model used (optional)
            context: Additional context (optional)
            
        Returns:
            SHA256 hash string
        """
        combined = f"{query}|{model}|{context}"
        return hashlib.sha256(combined.encode()).hexdigest()
    
    def get(self, 
            query: str, 
            model: str = "", 
            context: str = "") -> Optional[Dict[str, Any]]:
        """
        Retrieve a cached response
        
        Args:
            query: The query string
            model: The model used (optional)
            context: Additional context (optional)
            
        Returns:
            Cached response data or None if not found/expired
        """
        query_hash = self._generate_hash(query, model, context)
        
        with self._lock:
            if query_hash in self._cache:
                entry = self._cache[query_hash]
                
                # Check if expired
                if entry.is_expired():
                    del self._cache[query_hash]
                    self._misses += 1
                    return None
                
                # Update access statistics
                entry.hit_count += 1
                entry.last_accessed = time.time()
                self._hits += 1
                
                return {
                    "response": entry.response,
                    "model_used": entry.model_used,
                    "cached_at": datetime.fromtimestamp(entry.timestamp).isoformat(),
                    "hit_count": entry.hit_count,
                    "metadata": entry.metadata
                }
            
            self._misses += 1
            return None
    
    def set(self,
            query: str,
            response: str,
            model: str = "",
            context: str = "",
            metadata: Optional[Dict[str, Any]] = None,
            ttl: Optional[int] = None) -> bool:
        """
        Cache a query response
        
        Args:
            query: The query string
            response: The response to cache
            model: The model used
            context: Additional context
            metadata: Additional metadata to store
            ttl: Time-to-live in seconds (uses default if not specified)
            
        Returns:
            True if cached successfully
        """
        query_hash = self._generate_hash(query, model, context)
        ttl = ttl if ttl is not None else self.default_ttl
        
        entry = CacheEntry(
            query_hash=query_hash,
            query=query,
            response=response,
            model_used=model,
            timestamp=time.time(),
            hit_count=0,
            last_accessed=time.time(),
            metadata=metadata or {},
            ttl_seconds=ttl
        )
        
        with self._lock:
            # Evict entries if cache is full
            if len(self._cache) >= self.max_entries:
                self._evict_lru()
            
            self._cache[query_hash] = entry
            
            # Persist to disk if enabled
            if self.enable_persistence:
                self._save_to_disk()
            
            return True
    
    def _evict_lru(self):
        """Evict least recently used entries"""
        if not self._cache:
            return
        
        # Sort by last_accessed and remove oldest entries
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        # Remove 10% of entries
        num_to_evict = max(1, len(sorted_entries) // 10)
        for i in range(num_to_evict):
            query_hash = sorted_entries[i][0]
            del self._cache[query_hash]
            self._evictions += 1
    
    def invalidate(self, query: str, model: str = "", context: str = "") -> bool:
        """
        Invalidate a specific cache entry
        
        Args:
            query: The query string
            model: The model used
            context: Additional context
            
        Returns:
            True if entry was invalidated
        """
        query_hash = self._generate_hash(query, model, context)
        
        with self._lock:
            if query_hash in self._cache:
                del self._cache[query_hash]
                if self.enable_persistence:
                    self._save_to_disk()
                return True
            return False
    
    def clear(self):
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            self._evictions = 0
            
            if self.enable_persistence:
                self._save_to_disk()
    
    def cleanup_expired(self):
        """Remove all expired entries from cache"""
        with self._lock:
            expired_hashes = [
                hash_key for hash_key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for hash_key in expired_hashes:
                del self._cache[hash_key]
            
            if expired_hashes and self.enable_persistence:
                self._save_to_disk()
            
            return len(expired_hashes)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0
            
            return {
                "total_entries": len(self._cache),
                "hits": self._hits,
                "misses": self._misses,
                "evictions": self._evictions,
                "hit_rate": hit_rate,
                "max_entries": self.max_entries,
                "default_ttl": self.default_ttl
            }
    
    def get_entries(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get cache entries sorted by most recently accessed
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of cache entry dictionaries
        """
        with self._lock:
            sorted_entries = sorted(
                self._cache.values(),
                key=lambda x: x.last_accessed,
                reverse=True
            )
            
            return [
                {
                    "query": entry.query[:100] + "..." if len(entry.query) > 100 else entry.query,
                    "model_used": entry.model_used,
                    "cached_at": datetime.fromtimestamp(entry.timestamp).isoformat(),
                    "last_accessed": datetime.fromtimestamp(entry.last_accessed).isoformat(),
                    "hit_count": entry.hit_count,
                    "is_expired": entry.is_expired(),
                    "metadata": entry.metadata
                }
                for entry in sorted_entries[:limit]
            ]
    
    def _save_to_disk(self):
        """Save cache to disk"""
        cache_file = self.cache_dir / "query_cache.json"
        
        try:
            cache_data = {
                "entries": [entry.to_dict() for entry in self._cache.values()],
                "stats": {
                    "hits": self._hits,
                    "misses": self._misses,
                    "evictions": self._evictions
                }
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save cache to disk: {e}")
    
    def _load_from_disk(self):
        """Load cache from disk"""
        cache_file = self.cache_dir / "query_cache.json"
        
        if not cache_file.exists():
            return
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Load entries
            for entry_data in cache_data.get("entries", []):
                entry = CacheEntry.from_dict(entry_data)
                
                # Skip expired entries
                if not entry.is_expired():
                    self._cache[entry.query_hash] = entry
            
            # Load stats
            stats = cache_data.get("stats", {})
            self._hits = stats.get("hits", 0)
            self._misses = stats.get("misses", 0)
            self._evictions = stats.get("evictions", 0)
            
        except Exception as e:
            print(f"Warning: Failed to load cache from disk: {e}")


class ResponseCache:
    """Specialized cache for model responses with additional features"""
    
    def __init__(self, query_cache: QueryCache):
        """
        Initialize response cache
        
        Args:
            query_cache: The underlying query cache
        """
        self.cache = query_cache
    
    def cache_response(self,
                      query: str,
                      response: str,
                      model: str,
                      context: str = "",
                      response_time: float = 0.0,
                      tokens_used: int = 0,
                      metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Cache a model response with additional metadata
        
        Args:
            query: The query string
            response: The model response
            model: The model used
            context: Additional context
            response_time: Time taken to generate response
            tokens_used: Number of tokens used
            metadata: Additional metadata
            
        Returns:
            True if cached successfully
        """
        cache_metadata = {
            "response_time": response_time,
            "tokens_used": tokens_used,
            "cached_at": datetime.now().isoformat()
        }
        
        if metadata:
            cache_metadata.update(metadata)
        
        return self.cache.set(
            query=query,
            response=response,
            model=model,
            context=context,
            metadata=cache_metadata
        )
    
    def get_cached_response(self,
                           query: str,
                           model: str = "",
                           context: str = "") -> Optional[Dict[str, Any]]:
        """
        Get a cached response
        
        Args:
            query: The query string
            model: The model used
            context: Additional context
            
        Returns:
            Cached response data or None
        """
        return self.cache.get(query, model, context)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics from cached responses"""
        entries = self.cache.get_entries(limit=1000)
        
        total_response_time = 0
        total_tokens = 0
        response_count = 0
        
        for entry in entries:
            metadata = entry.get("metadata", {})
            if "response_time" in metadata:
                total_response_time += metadata["response_time"]
                response_count += 1
            if "tokens_used" in metadata:
                total_tokens += metadata["tokens_used"]
        
        return {
            "total_cached_responses": len(entries),
            "responses_with_timing": response_count,
            "average_response_time": total_response_time / response_count if response_count > 0 else 0,
            "total_tokens_cached": total_tokens,
            "average_tokens_per_response": total_tokens / len(entries) if entries else 0
        }