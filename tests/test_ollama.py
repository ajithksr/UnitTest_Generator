import os
import sys
# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm_client import LLMClient

def test_ollama_generation():
    print("Testing Ollama Integration...")
    # Force Ollama for testing
    os.environ["LLM_PROVIDER"] = "ollama"
    os.environ["OLLAMA_MODEL"] = "qwen2.5-coder:7b"
    
    client = LLMClient()
    
    signature = "int add(int a, int b)"
    strategy = {
        'suggested_test_cases': ['Positive case: 1+2=3', 'Negative case: -1+1=0'],
        'mocks_needed': []
    }
    
    print(f"Generating test body for: {signature}")
    body = client.generate_test_body(signature, strategy)
    
    print("\n--- Generated Body ---")
    print(body)
    print("----------------------\n")
    
    if "EXPECT" in body or "ASSERT" in body:
        print("SUCCESS: Generated body contains GTest macros.")
    elif "// Error" in body:
        print(f"FAILURE: {body}")
    else:
        print("WARNING: Generated body might be empty or unexpected.")

if __name__ == "__main__":
    test_ollama_generation()
