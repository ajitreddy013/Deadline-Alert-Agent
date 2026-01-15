"""
LLM Provider Abstraction Layer
Supports multiple LLM providers: Groq, Ollama, and Regex fallback
"""

import os
import json
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime

# Try importing optional dependencies
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("Info: groq package not installed. Groq provider unavailable.")

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    print("Info: ollama package not installed. Ollama provider unavailable.")


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def extract_deadlines(self, text: str) -> List[Dict]:
        """Extract deadlines from text"""
        pass
    
    @abstractmethod
    def chat(self, question: str, context: str) -> str:
        """Answer questions about deadlines"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available and working"""
        pass


class GroqProvider(LLMProvider):
    """Groq Cloud API Provider - Fast and free"""
    
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        super().__init__("groq")
        self.client = Groq(api_key=api_key)
        self.model = model
    
    def extract_deadlines(self, text: str) -> List[Dict]:
        """Extract deadlines using Groq API"""
        try:
            prompt = f"""Extract all deadlines and due dates from the following text. 
Return ONLY a valid JSON array of objects with this exact format:
[{{"task": "description", "date": "YYYY-MM-DD", "time": "HH:MM or null"}}]

If you find no deadlines, return an empty array: []

Text to analyze:
{text[:1000]}

JSON output:"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a deadline extraction assistant. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            # Extract JSON from response
            response_text = response.choices[0].message.content.strip()
            
            # Try to find JSON array in response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                deadlines = json.loads(json_match.group())
                return deadlines if isinstance(deadlines, list) else []
            
            return []
            
        except Exception as e:
            print(f"Groq extraction failed: {e}")
            raise  # Re-raise to trigger fallback
    
    def chat(self, question: str, context: str) -> str:
        """Answer questions using Groq API"""
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            current_day = datetime.now().strftime("%A")
            
            prompt = f"""You are DeadlineAI, an intelligent assistant specializing in deadline management and productivity.

Today is {current_day}, {current_date}.

AVAILABLE DEADLINES:
{context}

USER QUESTION: {question}

INSTRUCTIONS:
1. PRIMARY FOCUS: Deadlines & Time Management
   - If the question is about deadlines/tasks/schedules, provide detailed, actionable insights
   - Calculate time remaining, prioritize urgent items, suggest planning strategies
   - Be proactive: mention upcoming deadlines even if not directly asked

2. GENERAL QUESTIONS: Brief but Helpful
   - For non-deadline questions, answer briefly and professionally
   - Then gently redirect to deadline-related features
   - Example: "The capital of France is Paris. By the way, you have 2 deadlines this week - would you like me to review them?"

3. RESPONSE STYLE:
   - Friendly, professional, and concise (2-3 sentences max for general questions)
   - Use emojis sparingly for urgency: ⚠️ (urgent), ✅ (completed), 📅 (upcoming)
   - Always calculate from today's date ({current_date})
   - Group deadlines by: Overdue, This Week, Next Week, Later

4. SMART INSIGHTS:
   - Identify overdue tasks automatically
   - Suggest priorities based on urgency
   - Mention conflicts (multiple deadlines same day)
   - Provide time management tips when relevant

RESPOND NOW:"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are DeadlineAI, a friendly and intelligent deadline management assistant. Be helpful, concise, and proactive."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=400
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Groq chat failed: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if Groq is available"""
        if not GROQ_AVAILABLE:
            return False
        try:
            # Simple test to see if API key is valid
            self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            return True
        except:
            return False


class OllamaProvider(LLMProvider):
    """Ollama Local Provider - Privacy-focused local models"""
    
    def __init__(self, model: str = "llama3.2:1b"):
        super().__init__("ollama")
        self.model = model
    
    def extract_deadlines(self, text: str) -> List[Dict]:
        """Extract deadlines using Ollama"""
        try:
            prompt = f"""Extract all deadlines and due dates from the following text. 
Return ONLY a valid JSON array of objects with this exact format:
[{{"task": "description", "date": "YYYY-MM-DD", "time": "HH:MM or null"}}]

If you find no deadlines, return an empty array: []

Text to analyze:
{text[:1000]}

JSON output:"""

            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": 0.1,
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
            
            return []
            
        except Exception as e:
            print(f"Ollama extraction failed: {e}")
            raise
    
    def chat(self, question: str, context: str) -> str:
        """Answer questions using Ollama"""
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            prompt = f"""You are a helpful assistant for deadline management. Today's date is {current_date}.

{context}

User question: {question}

Provide a concise, helpful answer. If asking about deadlines this week/month, calculate from today's date.
If there are no relevant deadlines, say so clearly.

Answer:"""

            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": 0.3,
                    "num_predict": 200,
                }
            )
            
            return response['response'].strip()
            
        except Exception as e:
            print(f"Ollama chat failed: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        if not OLLAMA_AVAILABLE:
            return False
        try:
            ollama.list()
            return True
        except:
            return False


class RegexProvider(LLMProvider):
    """Regex Fallback Provider - Always available, basic pattern matching"""
    
    def __init__(self):
        super().__init__("regex")
    
    def extract_deadlines(self, text: str) -> List[Dict]:
        """Extract deadlines using regex patterns"""
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
    
    def chat(self, question: str, context: str) -> str:
        """Simple keyword-based responses"""
        question_lower = question.lower()
        
        if not context or "No deadlines" in context:
            return "You don't have any deadlines in the system yet."
        
        if "next" in question_lower:
            return "To see your next deadline, please check the task list. (Note: Install Ollama or configure Groq for smarter responses)"
        
        if "week" in question_lower:
            return "To filter deadlines by week, please use the app filters. (Note: Install Ollama or configure Groq for AI-powered chat)"
        
        return f"Here are your current deadlines:\n{context}\n\n(Note: Install Ollama or configure Groq API for AI-powered responses)"
    
    def is_available(self) -> bool:
        """Regex is always available"""
        return True


def get_llm_provider(provider_preference: str = "auto") -> LLMProvider:
    """
    Factory function to get the best available LLM provider
    
    Priority (when provider_preference='auto'):
    1. Groq (if API key configured)
    2. Ollama (if running locally)
    3. Regex (always available)
    """
    
    # If specific provider requested
    if provider_preference == "groq":
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        if not GROQ_AVAILABLE:
            raise ImportError("groq package not installed. Run: pip install groq")
        return GroqProvider(api_key=api_key, model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))
    
    elif provider_preference == "ollama":
        if not OLLAMA_AVAILABLE:
            raise ImportError("ollama package not installed. Run: pip install ollama")
        return OllamaProvider(model=os.getenv("OLLAMA_MODEL", "llama3.2:1b"))
    
    elif provider_preference == "regex":
        return RegexProvider()
    
    # Auto mode: try providers in order
    # 1. Try Groq
    api_key = os.getenv("GROQ_API_KEY")
    if api_key and GROQ_AVAILABLE:
        try:
            provider = GroqProvider(api_key=api_key, model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))
            if provider.is_available():
                print("Using Groq provider")
                return provider
        except Exception as e:
            print(f"Groq provider initialization failed: {e}")
    
    # 2. Try Ollama
    if OLLAMA_AVAILABLE:
        try:
            provider = OllamaProvider(model=os.getenv("OLLAMA_MODEL", "llama3.2:1b"))
            if provider.is_available():
                print("Using Ollama provider")
                return provider
        except Exception as e:
            print(f"Ollama provider initialization failed: {e}")
    
    # 3. Fallback to Regex
    print("Using Regex fallback provider")
    return RegexProvider()


def check_all_providers() -> Dict:
    """Check availability of all providers"""
    status = {}
    
    # Check Groq
    api_key = os.getenv("GROQ_API_KEY")
    if api_key and GROQ_AVAILABLE:
        try:
            groq = GroqProvider(api_key=api_key)
            status["groq"] = {"available": groq.is_available(), "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")}
        except:
            status["groq"] = {"available": False, "reason": "Initialization failed"}
    else:
        status["groq"] = {"available": False, "reason": "API key not set" if not api_key else "Package not installed"}
    
    # Check Ollama
    if OLLAMA_AVAILABLE:
        try:
            ollama_provider = OllamaProvider()
            status["ollama"] = {"available": ollama_provider.is_available(), "model": os.getenv("OLLAMA_MODEL", "llama3.2:1b")}
        except:
            status["ollama"] = {"available": False, "reason": "Not running"}
    else:
        status["ollama"] = {"available": False, "reason": "Package not installed"}
    
    # Regex is always available
    status["regex"] = {"available": True, "model": "pattern-matching"}
    
    return status


if __name__ == "__main__":
    # Test the provider system
    print("Testing LLM Provider System\n")
    
    # Check all providers
    print("Provider Status:")
    print(json.dumps(check_all_providers(), indent=2))
    
    # Get default provider
    print("\nGetting default provider...")
    provider = get_llm_provider()
    print(f"Active provider: {provider.name}")
    
    # Test extraction
    test_text = """
    Important: Assignment due on January 20, 2024 at 11:59 PM.
    The hackathon registration deadline is 2024-01-25.
    Please submit your project by 15/02/2024.
    """
    
    print("\nTesting deadline extraction...")
    deadlines = provider.extract_deadlines(test_text)
    print(json.dumps(deadlines, indent=2))
