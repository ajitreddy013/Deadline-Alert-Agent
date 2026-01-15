"""
LLM-based deadline extraction with multi-provider support
Supports Groq (cloud), Ollama (local), and regex fallback
"""

import os
from typing import List, Dict
from llm_provider import get_llm_provider, check_all_providers

def extract_deadlines_with_llm(text: str) -> List[Dict]:
    """
    Extract deadlines using the best available LLM provider
    
    Priority:
    1. Groq (if API key configured)
    2. Ollama (if running locally)
    3. Regex (always available)
    """
    provider = get_llm_provider()
    
    try:
        deadlines = provider.extract_deadlines(text)
        print(f"Extracted {len(deadlines)} deadlines using {provider.name} provider")
        return deadlines
    except Exception as e:
        print(f"Deadline extraction failed with {provider.name}: {e}")
        # If primary provider fails, try regex fallback
        from llm_provider import RegexProvider
        fallback = RegexProvider()
        return fallback.extract_deadlines(text)

def check_llm_availability() -> Dict:
    """
    Check availability of all LLM providers
    Returns status for Groq, Ollama, and Regex
    """
    return check_all_providers()

# Legacy function names for backward compatibility
def extract_deadlines_regex_fallback(text: str) -> List[Dict]:
    """Legacy function - use RegexProvider directly"""
    from llm_provider import RegexProvider
    return RegexProvider().extract_deadlines(text)

def check_ollama_availability() -> Dict:
    """Legacy function - use check_all_providers() instead"""
    status = check_all_providers()
    return {
        "available": status.get("ollama", {}).get("available", False),
        "reason": status.get("ollama", {}).get("reason", "Unknown"),
        "models": [status.get("ollama", {}).get("model", "llama3.2:1b")] if status.get("ollama", {}).get("available") else []
    }

if __name__ == "__main__":
    # Test the extractor
    import json
    
    test_text = """
    Important: Assignment due on January 20, 2024 at 11:59 PM.
    The hackathon registration deadline is 2024-01-25.
    Please submit your project by 15/02/2024.
    """
    
    print("Checking LLM provider availability...")
    status = check_llm_availability()
    print(json.dumps(status, indent=2))
    
    print("\nExtracting deadlines...")
    deadlines = extract_deadlines_with_llm(test_text)
    print(json.dumps(deadlines, indent=2))
