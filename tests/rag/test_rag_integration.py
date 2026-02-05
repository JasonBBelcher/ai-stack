#!/usr/bin/env python3
"""
Test RAG Integration - Test the complete RAG system with intent routing.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.prompt_engineer import IntentRouter, IntentType
from src.enhanced_controller import SimplifiedAIStackController


def test_intent_classifier():
    """Test the intent classifier with various queries."""
    print("=" * 60)
    print("Testing Intent Classifier")
    print("=" * 60)
    
    router = IntentRouter()
    
    test_queries = [
        ("debug", "I'm getting a NameError when I run my code"),
        ("debug", "The function is throwing an exception"),
        ("debug", "Fix this bug in the code"),
        ("generate", "Create a new function to calculate fibonacci"),
        ("generate", "Write a class for user authentication"),
        ("generate", "Implement a REST API endpoint"),
        ("explain", "Explain how the SimplifiedAIStackController works"),
        ("explain", "What does the ContextRetriever do?"),
        ("explain", "How do I use the RAG system?"),
        ("general", "Hello, how are you?"),
        ("general", "What's the weather like?"),
    ]
    
    print("\nTesting intent classification:")
    for expected_intent, query in test_queries:
        intent = router.classify(query)
        intent_info = router.get_intent_info(query)
        
        status = "✅" if intent.value == expected_intent else "❌"
        print(f"{status} Query: {query[:50]}...")
        print(f"   Expected: {expected_intent}, Got: {intent.value}")
        print(f"   Confidence: {intent_info['confidence']:.2f}")
        print(f"   Template: {intent_info['suggested_template']}")
        print()
    
    print("✅ Intent classifier tests completed\n")


def test_rag_integration():
    """Test RAG integration with the controller."""
    print("=" * 60)
    print("Testing RAG Integration")
    print("=" * 60)
    
    # Use the ai-stack project itself for testing
    project_path = str(Path(__file__).parent)
    
    print(f"\nInitializing controller with project path: {project_path}")
    
    try:
        controller = SimplifiedAIStackController(project_path=project_path)
        
        # Check if RAG was initialized
        if controller.rag_retriever:
            print("✅ RAG retriever initialized successfully")
        else:
            print("⚠️ RAG retriever not initialized (index may not exist)")
            print("   Run 'python main.py --index --project-path .' to create an index")
            return
        
        # Test queries with different intents
        test_queries = [
            ("debug", "I'm getting an error in the enhanced_controller.py file"),
            ("generate", "Create a new function to validate model configurations"),
            ("explain", "Explain how the IntentRouter class works"),
        ]
        
        print("\nTesting RAG integration with different intents:")
        for expected_intent, query in test_queries:
            print(f"\n{'=' * 60}")
            print(f"Testing {expected_intent} intent")
            print(f"Query: {query}")
            print(f"{'=' * 60}")
            
            # Process the request
            result = controller.process_request(query)
            
            if result.success:
                print(f"✅ Request processed successfully")
                print(f"⏱️ Execution time: {result.execution_time:.2f}s")
                print(f"💾 Memory used: {result.memory_used:.2f}GB")
                
                # Print metadata
                if hasattr(result, 'metadata') and result.metadata:
                    print(f"\n📊 Metadata:")
                    print(f"   Intent: {result.metadata.get('intent', 'unknown')}")
                    print(f"   Confidence: {result.metadata.get('intent_confidence', 0):.2f}")
                    print(f"   RAG Used: {'Yes' if result.metadata.get('rag_used', False) else 'No'}")
                    if result.metadata.get('rag_used', False):
                        print(f"   RAG Context Length: {result.metadata.get('rag_context_length', 0)} characters")
                    print(f"   Template: {result.metadata.get('template_used', 'unknown')}")
                
                # Print output (truncated if too long)
                print(f"\n📝 Output:")
                output = result.output
                if len(output) > 500:
                    print(output[:500] + "\n... (truncated)")
                else:
                    print(output)
            else:
                print(f"❌ Request failed: {result.error}")
        
        print("\n✅ RAG integration tests completed\n")
        
    except Exception as e:
        print(f"❌ Error testing RAG integration: {e}")
        import traceback
        traceback.print_exc()


def test_rag_context_retrieval():
    """Test RAG context retrieval directly."""
    print("=" * 60)
    print("Testing RAG Context Retrieval")
    print("=" * 60)
    
    project_path = str(Path(__file__).parent)
    index_file = Path(project_path) / ".ai-stack" / "code_index.faiss"
    metadata_file = Path(project_path) / ".ai-stack" / "code_metadata.pkl"
    
    if not index_file.exists() or not metadata_file.exists():
        print(f"⚠️ RAG index not found at {index_file}")
        print("   Run 'python main.py --index --project-path .' to create an index")
        return
    
    try:
        from src.rag import ContextRetriever
        
        print(f"\nLoading RAG index from: {index_file}")
        retriever = ContextRetriever(
            index_path=str(index_file),
            metadata_path=str(metadata_file)
        )
        
        # Test queries
        test_queries = [
            "How does the IntentRouter work?",
            "What is the SimplifiedAIStackController?",
            "Explain the RAG system",
        ]
        
        print("\nTesting context retrieval:")
        for query in test_queries:
            print(f"\n{'=' * 60}")
            print(f"Query: {query}")
            print(f"{'=' * 60}")
            
            context = retriever.retrieve_and_format(query)
            
            if context:
                print(f"✅ Retrieved {len(context)} characters of context")
                print(f"\n📄 Context (first 500 chars):")
                print(context[:500] + "\n... (truncated)")
            else:
                print("⚠️ No context retrieved")
        
        print("\n✅ RAG context retrieval tests completed\n")
        
    except Exception as e:
        print(f"❌ Error testing RAG context retrieval: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("RAG Integration Test Suite")
    print("=" * 60 + "\n")
    
    # Test 1: Intent Classifier
    test_intent_classifier()
    
    # Test 2: RAG Context Retrieval
    test_rag_context_retrieval()
    
    # Test 3: RAG Integration with Controller
    test_rag_integration()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()