"""
Chat handler for deadline queries using LLM
"""

import json
from typing import List, Dict, Optional
from datetime import datetime

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

def build_context_from_tasks(tasks: List) -> str:
    """Build context string from tasks for LLM"""
    if not tasks:
        return "No deadlines currently in the system."
    
    context_parts = []
    for task in tasks:
        task_str = f"- {task.summary}"
        if task.deadline:
            task_str += f" (Due: {task.deadline})"
        if task.source:
            task_str += f" [Source: {task.source}]"
        context_parts.append(task_str)
    
    return "Current deadlines:\n" + "\n".join(context_parts)

def chat_with_deadlines(question: str, tasks: List, model: str = "llama3.2:1b") -> Dict:
    """Chat interface to query deadlines"""
    
    if not OLLAMA_AVAILABLE:
        return {
            "answer": "Chat feature requires Ollama. Please install: pip install ollama",
            "source": "error"
        }
    
    try:
        # Build context
        context = build_context_from_tasks(tasks)
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Create prompt
        prompt = f"""You are a helpful assistant for deadline management. Today's date is {current_date}.

{context}

User question: {question}

Provide a concise, helpful answer. If asking about deadlines this week/month, calculate from today's date.
If there are no relevant deadlines, say so clearly.

Answer:"""

        response = ollama.generate(
            model=model,
            prompt=prompt,
            options={
                "temperature": 0.3,
                "num_predict": 200,
            }
        )
        
        return {
            "answer": response['response'].strip(),
            "source": "llm",
            "model": model,
            "context_tasks": len(tasks)
        }
        
    except Exception as e:
        return {
            "answer": f"Error generating response: {str(e)}",
            "source": "error"
        }

def suggest_questions() -> List[str]:
    """Suggest example questions users can ask"""
    return [
        "What deadlines do I have this week?",
        "Show me all urgent deadlines",
        "When is my next deadline?",
        "What's due in January?",
        "Do I have any deadlines from Gmail?",
        "Summarize my upcoming tasks"
    ]

if __name__ == "__main__":
    # Test the chat handler
    from dataclasses import dataclass
    
    @dataclass
    class MockTask:
        summary: str
        deadline: str
        source: str
    
    test_tasks = [
        MockTask("Project submission", "2024-01-20", "gmail"),
        MockTask("Hackathon registration", "2024-01-25 18:00", "gmail"),
        MockTask("Team meeting", "2024-01-17 10:00", "manual"),
    ]
    
    test_questions = [
        "What deadlines do I have?",
        "What's due this week?",
        "When is the hackathon?",
    ]
    
    for question in test_questions:
        print(f"\nQ: {question}")
        response = chat_with_deadlines(question, test_tasks)
        print(f"A: {response['answer']}")
