#!/usr/bin/env python3
"""
Test script for query cache functionality.
"""

import sys
import os
import time
import tempfile
import shutil

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from query_cache import QueryCache, ResponseCache

def test_basic_cache_operations():
    """Test basic cache get/set operations."""
    print("="*60)
    print("TEST 1: Basic Cache Operations")
    print("="*60)
    
    # Create a temporary cache directory
    with tempfile.TemporaryDirectory() as temp_dir:
        cache = QueryCache(cache_dir=temp_dir, enable_persistence=False)
        
        # Test cache miss
        result = cache.get("test query", model="test-model")
        assert result is None, "Cache should return None for non-existent query"
        print("  ✓ Cache miss works correctly")
        
        # Test cache set
        success = cache.set(
            query="test query",
            response="test response",
            model="test-model"
        )
        assert success, "Cache set should succeed"
        print("  ✓ Cache set works correctly")
        
        # Test cache hit
        result = cache.get("test query", model="test-model")
        assert result is not None, "Cache should return cached response"
        assert result["response"] == "test response", "Response should match"
        assert result["model_used"] == "test-model", "Model should match"
        print("  ✓ Cache hit works correctly")
        
        # Test cache statistics
        stats = cache.get_stats()
        assert stats["hits"] == 1, "Should have 1 hit"
        assert stats["misses"] == 1, "Should have 1 miss"
        assert stats["total_entries"] == 1, "Should have 1 entry"
        print(f"  ✓ Cache statistics: {stats}")
    
    print("\n✓ Basic cache operations working!")
    return True

def test_cache_expiration():
    """Test cache entry expiration."""
    print("\n" + "="*60)
    print("TEST 2: Cache Expiration")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        cache = QueryCache(cache_dir=temp_dir, default_ttl=1, enable_persistence=False)
        
        # Cache an entry with 1 second TTL
        cache.set(
            query="expiring query",
            response="expiring response",
            model="test-model"
        )
        
        # Should be available immediately
        result = cache.get("expiring query", model="test-model")
        assert result is not None, "Entry should be available immediately"
        print("  ✓ Entry available immediately after caching")
        
        # Wait for expiration
        time.sleep(1.5)
        
        # Should be expired now
        result = cache.get("expiring query", model="test-model")
        assert result is None, "Entry should be expired after TTL"
        print("  ✓ Entry expires after TTL")
        
        # Check statistics
        stats = cache.get_stats()
        assert stats["total_entries"] == 0, "Expired entries should be removed"
        print(f"  ✓ Expired entries removed: {stats}")
    
    print("\n✓ Cache expiration working!")
    return True

def test_cache_with_context():
    """Test cache with context differentiation."""
    print("\n" + "="*60)
    print("TEST 3: Cache with Context")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        cache = QueryCache(cache_dir=temp_dir, enable_persistence=False)
        
        # Cache same query with different contexts
        cache.set(
            query="test query",
            response="response for context A",
            model="test-model",
            context="context A"
        )
        
        cache.set(
            query="test query",
            response="response for context B",
            model="test-model",
            context="context B"
        )
        
        # Should get different responses based on context
        result_a = cache.get("test query", model="test-model", context="context A")
        result_b = cache.get("test query", model="test-model", context="context B")
        
        assert result_a["response"] == "response for context A", "Should get response for context A"
        assert result_b["response"] == "response for context B", "Should get response for context B"
        print("  ✓ Different contexts produce different cache entries")
        
        # Check statistics
        stats = cache.get_stats()
        assert stats["total_entries"] == 2, "Should have 2 entries"
        print(f"  ✓ Cache has 2 entries: {stats}")
    
    print("\n✓ Cache with context working!")
    return True

def test_cache_eviction():
    """Test cache eviction when full."""
    print("\n" + "="*60)
    print("TEST 4: Cache Eviction")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        cache = QueryCache(cache_dir=temp_dir, max_entries=5, enable_persistence=False)
        
        # Fill cache to capacity
        for i in range(5):
            cache.set(
                query=f"query {i}",
                response=f"response {i}",
                model="test-model"
            )
        
        stats = cache.get_stats()
        assert stats["total_entries"] == 5, "Should have 5 entries"
        print(f"  ✓ Cache filled to capacity: {stats['total_entries']} entries")
        
        # Add one more entry (should trigger eviction)
        cache.set(
            query="query 5",
            response="response 5",
            model="test-model"
        )
        
        stats = cache.get_stats()
        assert stats["total_entries"] <= 5, "Should not exceed max entries"
        assert stats["evictions"] > 0, "Should have evicted entries"
        print(f"  ✓ Cache eviction triggered: {stats['evictions']} evictions")
        print(f"  ✓ Cache size maintained: {stats['total_entries']} entries")
    
    print("\n✓ Cache eviction working!")
    return True

def test_cache_invalidation():
    """Test cache invalidation."""
    print("\n" + "="*60)
    print("TEST 5: Cache Invalidation")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        cache = QueryCache(cache_dir=temp_dir, enable_persistence=False)
        
        # Cache an entry
        cache.set(
            query="test query",
            response="test response",
            model="test-model"
        )
        
        # Verify it's cached
        result = cache.get("test query", model="test-model")
        assert result is not None, "Entry should be cached"
        print("  ✓ Entry cached successfully")
        
        # Invalidate the entry
        success = cache.invalidate("test query", model="test-model")
        assert success, "Invalidation should succeed"
        print("  ✓ Entry invalidated")
        
        # Verify it's gone
        result = cache.get("test query", model="test-model")
        assert result is None, "Entry should be removed after invalidation"
        print("  ✓ Entry removed after invalidation")
        
        # Test invalidating non-existent entry
        success = cache.invalidate("non-existent query")
        assert not success, "Invalidating non-existent entry should fail"
        print("  ✓ Invalidating non-existent entry returns False")
    
    print("\n✓ Cache invalidation working!")
    return True

def test_cache_cleanup():
    """Test cleanup of expired entries."""
    print("\n" + "="*60)
    print("TEST 6: Cache Cleanup")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        cache = QueryCache(cache_dir=temp_dir, default_ttl=1, enable_persistence=False)
        
        # Cache multiple entries with different TTLs
        cache.set("query 1", "response 1", "test-model", ttl=1)
        cache.set("query 2", "response 2", "test-model", ttl=2)
        cache.set("query 3", "response 3", "test-model", ttl=3)
        
        stats = cache.get_stats()
        assert stats["total_entries"] == 3, "Should have 3 entries"
        print(f"  ✓ Cached 3 entries")
        
        # Wait for first entry to expire
        time.sleep(1.5)
        
        # Cleanup expired entries
        expired_count = cache.cleanup_expired()
        assert expired_count == 1, "Should have cleaned up 1 expired entry"
        print(f"  ✓ Cleaned up {expired_count} expired entry")
        
        stats = cache.get_stats()
        assert stats["total_entries"] == 2, "Should have 2 entries remaining"
        print(f"  ✓ {stats['total_entries']} entries remaining")
    
    print("\n✓ Cache cleanup working!")
    return True

def test_cache_persistence():
    """Test cache persistence to disk."""
    print("\n" + "="*60)
    print("TEST 7: Cache Persistence")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create cache and add entries
        cache1 = QueryCache(cache_dir=temp_dir, enable_persistence=True)
        
        cache1.set(
            query="persistent query",
            response="persistent response",
            model="test-model",
            metadata={"key": "value"}
        )
        
        stats1 = cache1.get_stats()
        print(f"  ✓ First cache: {stats1['total_entries']} entry")
        
        # Create new cache instance (should load from disk)
        cache2 = QueryCache(cache_dir=temp_dir, enable_persistence=True)
        
        # Verify entry was loaded
        result = cache2.get("persistent query", model="test-model")
        assert result is not None, "Entry should be loaded from disk"
        assert result["response"] == "persistent response", "Response should match"
        assert result["metadata"]["key"] == "value", "Metadata should match"
        print("  ✓ Entry loaded from disk")
        
        stats2 = cache2.get_stats()
        assert stats2["total_entries"] == 1, "Should have 1 entry"
        print(f"  ✓ Second cache: {stats2['total_entries']} entry")
    
    print("\n✓ Cache persistence working!")
    return True

def test_response_cache():
    """Test ResponseCache wrapper."""
    print("\n" + "="*60)
    print("TEST 8: Response Cache")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        query_cache = QueryCache(cache_dir=temp_dir, enable_persistence=False)
        response_cache = ResponseCache(query_cache)
        
        # Cache a response with performance metadata
        response_cache.cache_response(
            query="test query",
            response="test response",
            model="test-model",
            response_time=1.5,
            tokens_used=100,
            metadata={"custom": "data"}
        )
        
        # Retrieve cached response
        result = response_cache.get_cached_response("test query", model="test-model")
        assert result is not None, "Should retrieve cached response"
        assert result["response"] == "test response", "Response should match"
        print("  ✓ Response cached and retrieved")
        
        # Check performance stats
        perf_stats = response_cache.get_performance_stats()
        assert perf_stats["total_cached_responses"] == 1, "Should have 1 response"
        assert perf_stats["average_response_time"] == 1.5, "Average time should match"
        assert perf_stats["total_tokens_cached"] == 100, "Total tokens should match"
        print(f"  ✓ Performance stats: {perf_stats}")
    
    print("\n✓ Response cache working!")
    return True

def test_cache_entries_list():
    """Test getting list of cache entries."""
    print("\n" + "="*60)
    print("TEST 9: Cache Entries List")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        cache = QueryCache(cache_dir=temp_dir, enable_persistence=False)
        
        # Add multiple entries
        for i in range(5):
            cache.set(
                query=f"query {i}",
                response=f"response {i}",
                model=f"model-{i % 2}"
            )
        
        # Get entries
        entries = cache.get_entries(limit=10)
        assert len(entries) == 5, "Should have 5 entries"
        print(f"  ✓ Retrieved {len(entries)} entries")
        
        # Check entry structure
        entry = entries[0]
        assert "query" in entry, "Entry should have query"
        assert "model_used" in entry, "Entry should have model_used"
        assert "cached_at" in entry, "Entry should have cached_at"
        assert "hit_count" in entry, "Entry should have hit_count"
        print("  ✓ Entries have correct structure")
        
        # Test limit
        entries_limited = cache.get_entries(limit=3)
        assert len(entries_limited) == 3, "Should respect limit"
        print(f"  ✓ Limit respected: {len(entries_limited)} entries")
    
    print("\n✓ Cache entries list working!")
    return True

def test_cache_clear():
    """Test clearing all cache entries."""
    print("\n" + "="*60)
    print("TEST 10: Cache Clear")
    print("="*60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        cache = QueryCache(cache_dir=temp_dir, enable_persistence=False)
        
        # Add entries
        for i in range(5):
            cache.set(f"query {i}", f"response {i}", "test-model")
        
        stats = cache.get_stats()
        assert stats["total_entries"] == 5, "Should have 5 entries"
        print(f"  ✓ Added {stats['total_entries']} entries")
        
        # Clear cache
        cache.clear()
        
        stats = cache.get_stats()
        assert stats["total_entries"] == 0, "Should have 0 entries after clear"
        assert stats["hits"] == 0, "Hits should be reset"
        assert stats["misses"] == 0, "Misses should be reset"
        print(f"  ✓ Cache cleared: {stats}")
    
    print("\n✓ Cache clear working!")
    return True

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("QUERY CACHE TEST SUITE")
    print("="*60)
    
    tests = [
        test_basic_cache_operations,
        test_cache_expiration,
        test_cache_with_context,
        test_cache_eviction,
        test_cache_invalidation,
        test_cache_cleanup,
        test_cache_persistence,
        test_response_cache,
        test_cache_entries_list,
        test_cache_clear,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"\n✗ {test.__name__} failed with error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test.__name__, False))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    failed = len(results) - passed
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if failed > 0:
        print(f"\n{failed} test(s) failed!")
        sys.exit(1)
    else:
        print("\n✓ All tests passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()