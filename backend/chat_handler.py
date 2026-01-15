"""
Chat handler for deadline queries using LLM
Supports Groq (cloud), Ollama (local), and regex fallback
"""

from typing import List, Dict
from datetime import datetime
from llm_provider import get_llm_provider, check_all_providers

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

def chat_with_deadlines(question: str, tasks: List) -> Dict:
    """
    Chat interface to query deadlines using best available LLM provider
    
    Returns answer with provider information
    """
    provider = get_llm_provider()
    
    try:
        # Build context
        context = build_context_from_tasks(tasks)
        
        # Get answer from provider
        answer = provider.chat(question, context)
        
        return {
            "answer": answer,
            "provider": provider.name,
            "context_tasks": len(tasks)
        }
        
    except Exception as e:
        return {
            "answer": f"Error generating response: {str(e)}",
            "provider": "error",
            "context_tasks": len(tasks)
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

def get_llm_status() -> Dict:
    """Get status of all available LLM providers"""
    provider = get_llm_provider()
    all_providers = check_all_providers()
    
    return {
        "active_provider": provider.name,
        "available_providers": all_providers,
        "suggested_questions": suggest_questions()
    }

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
    
    # Check status
    print("LLM Status:")
    import json
    print(json.dumps(get_llm_status(), indent=2))
    
    # Test questions
    test_questions = [
        "What deadlines do I have?",
        "What's due this week?",
        "When is the hackathon?",
    ]
    
    for question in test_questions:
        print(f"\nQ: {question}")
        response = chat_with_deadlines(question, test_tasks)
        print(f"A ({response['provider']}): {response['answer']}")

