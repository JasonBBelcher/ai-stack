"""
Ultra-minimal test to isolate the issue
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

print("Starting ultra-minimal test...")

try:
    print("Testing capabilities import...")
    from capabilities import ModelCapabilities
    print("✓ capabilities imported")
    
    print("Testing basic dataclass...")
    caps = ModelCapabilities(
        context_length=32000,
        quantization_level="Q4_K_M",
        model_size=7000000000,
        memory_gb_estimate=5.0
    )
    print(f"✓ ModelCapabilities created: context={caps.context_length}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print("Test completed!")