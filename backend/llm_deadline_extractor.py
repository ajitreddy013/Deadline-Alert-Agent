"""
LLM-based deadline extraction using Ollama
Falls back to regex if Ollama is unavailable
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Optional

# Try to import ollama
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Warning: ollama package not installed. Using regex fallback.")

def extract_deadlines_with_llm(text: str, model: str = "llama3.2:1b") -> List[Dict]:
    """Extract deadlines using local LLM via Ollama"""
    
    if not OLLAMA_AVAILABLE:
        return extract_deadlines_regex_fallback(text)
    
    try:
        prompt = f"""Extract all deadlines and due dates from the following text. 
Return ONLY a valid JSON array of objects with this exact format:
[{{"task": "description", "date": "YYYY-MM-DD", "time": "HH:MM or null"}}]

If you find no deadlines, return an empty array: []

Text to analyze:
{text[:1000]}

JSON output:"""

        response = ollama.generate(
            model=model,
            prompt=prompt,
            options={
                "temperature": 0.1,  # Low temperature for consistent extraction
                "num_predict": 500,
            }
        )
        
        # Extract JSON from response
        response_text = response['response'].strip()
        
        # Try to find JSON array in response
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            deadlines = json.loads(json_match.group())
            return deadlines if isinstance(deadlines, list) else []
        
        # If no JSON found, return empty
        return []
        
    except Exception as e:
        print(f"LLM extraction failed: {e}, falling back to regex")
        return extract_deadlines_regex_fallback(text)

def extract_deadlines_regex_fallback(text: str) -> List[Dict]:
    """Fallback regex-based extraction"""
    deadlines = []
    
    # Date patterns
    patterns = [
        (r'(\d{4}-\d{2}-\d{2})', '%Y-%m-%d'),  # 2024-01-15
        (r'(\d{1,2}/\d{1,2}/\d{4})', '%m/%d/%Y'),  # 01/15/2024
        (r'(\d{1,2}-\d{1,2}-\d{4})', '%m-%d-%Y'),  # 01-15-2024
        (r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* (\d{1,2}),? (\d{4})', None),  # January 15, 2024
    ]
    
    for pattern, date_format in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                date_str = ' '.join(str(m) for m in match)
            else:
                date_str = match
            
            deadlines.append({
                "task": "Extracted from email",
                "date": date_str,
                "time": None
            })
    
    return deadlines

def check_ollama_availability() -> Dict:
    """Check if Ollama is running and available"""
    if not OLLAMA_AVAILABLE:
        return {
            "available": False,
            "reason": "ollama package not installed",
            "install_command": "pip install ollama"
        }
    
    try:
        # Try to list models
        models = ollama.list()
        return {
            "available": True,
            "models": [m['name'] for m in models.get('models', [])],
            "recommended_model": "llama3.2:1b"
        }
    except Exception as e:
        return {
            "available": False,
            "reason": str(e),
            "suggestion": "Make sure Ollama is installed and running. Visit: https://ollama.ai"
        }

if __name__ == "__main__":
    # Test the extractor
    test_text = """
    Important: Assignment due on January 20, 2024 at 11:59 PM.
    The hackathon registration deadline is 2024-01-25.
    Please submit your project by 15/02/2024.
    """
    
    print("Checking Ollama availability...")
    status = check_ollama_availability()
    print(json.dumps(status, indent=2))
    
    print("\nExtracting deadlines...")
    deadlines = extract_deadlines_with_llm(test_text)
    print(json.dumps(deadlines, indent=2))
