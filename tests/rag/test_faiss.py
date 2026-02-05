#!/usr/bin/env python3
"""
Test script to verify FAISS vector storage is working correctly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.rag import CodeEmbedder, FAISSVectorStore, ContextRetriever

def test_faiss():
    """Test FAISS vector storage functionality."""
    print("="*60)
    print("Testing FAISS Vector Storage")
    print("="*60)
    
    # Test 1: Load embedding model
    print("\n1. Loading embedding model...")
    try:
        embedder = CodeEmbedder(model_name="BAAI/bge-small-en-v1.5")
        dim = embedder.get_embedding_dimension()
        print(f"   ✅ Embedding model loaded successfully")
        print(f"   ✅ Embedding dimension: {dim}")
    except Exception as e:
        print(f"   ❌ Failed to load embedding model: {e}")
        return False
    
    # Test 2: Load existing index
    print("\n2. Loading existing FAISS index...")
    index_path = "/Users/jasonbelcher/Documents/code/ai-stack/src/.ai-stack-index"
    try:
        vector_store = FAISSVectorStore(index_type="Flat", dimension=dim)
        vector_store.load(index_path)
        size = vector_store.get_size()
        print(f"   ✅ Index loaded successfully")
        print(f"   ✅ Index contains {size} embeddings")
    except Exception as e:
        print(f"   ❌ Failed to load index: {e}")
        return False
    
    # Test 3: Generate query embedding
    print("\n3. Generating query embedding...")
    query = "What is the SimplifiedAIStackController class?"
    try:
        query_embedding = embedder.embed_text(query)
        print(f"   ✅ Query embedding generated successfully")
        print(f"   ✅ Embedding shape: {query_embedding.shape}")
    except Exception as e:
        print(f"   ❌ Failed to generate query embedding: {e}")
        return False
    
    # Test 4: Search the index
    print("\n4. Searching the index...")
    try:
        distances, results = vector_store.search(query_embedding, k=3)
        print(f"   ✅ Search completed successfully")
        print(f"   ✅ Found {len(results)} results")
        
        if results:
            print("\n   Top 3 results:")
            for i, result in enumerate(results, 1):
                file_path = result.get('file_path', 'unknown')
                start_line = result.get('start_line', 0)
                end_line = result.get('end_line', 0)
                distance = result.get('distance', 0)
                print(f"   {i}. {file_path} (lines {start_line}-{end_line}) - distance: {distance:.4f}")
        else:
            print("   ⚠️ No results found")
    except Exception as e:
        print(f"   ❌ Failed to search index: {e}")
        return False
    
    # Test 5: Test retriever
    print("\n5. Testing context retriever...")
    try:
        retriever = ContextRetriever(embedder, vector_store)
        context = retriever.retrieve_and_format(query, k=3)
        print(f"   ✅ Context retrieved successfully")
        print(f"   ✅ Context length: {len(context)} characters")
        
        if context:
            print(f"\n   First 200 characters of context:")
            print(f"   {context[:200]}...")
        else:
            print("   ⚠️ No context retrieved")
    except Exception as e:
        print(f"   ❌ Failed to retrieve context: {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ All FAISS tests passed!")
    print("="*60)
    return True

if __name__ == "__main__":
    success = test_faiss()
    sys.exit(0 if success else 1)