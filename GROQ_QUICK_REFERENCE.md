# Groq Integration - Quick Reference

## New API Endpoints

### 1. Check LLM Status
**GET** `/llm/status`

Check which LLM providers are available and get suggested questions.

```bash
curl http://localhost:8000/llm/status
```

**Response:**
```json
{
  "active_provider": "groq",
  "available_providers": {
    "groq": {
      "available": true,
      "model": "llama-3.3-70b-versatile"
    },
    "ollama": {
      "available": false,
      "reason": "Not running"
    },
    "regex": {
      "available": true,
      "model": "pattern-matching"
    }
  },
  "suggested_questions": [
    "What deadlines do I have this week?",
    "Show me all urgent deadlines",
    "When is my next deadline?",
    "What's due in January?",
    "Do I have any deadlines from Gmail?",
    "Summarize my upcoming tasks"
  ]
}
```

---

### 2. Chat with Deadlines
**POST** `/chat?question={query}`

Ask questions about your deadlines using AI.

```bash
curl -X POST "http://localhost:8000/chat?question=What%20are%20my%20deadlines%20this%20week"
```

**Response:**
```json
{
  "answer": "You have 2 deadlines this week: Project submission on Jan 20 and Team meeting on Jan 17.",
  "provider": "groq",
  "context_tasks": 5
}
```

---

## Environment Variables

Add to `.env` file:

```bash
# Groq API (Cloud - Recommended for mobile)
GROQ_API_KEY=gsk_your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Ollama (Local - Recommended for privacy)
OLLAMA_MODEL=llama3.2:1b

# Provider priority: auto, groq, ollama, or regex
LLM_PROVIDER=auto
```

---

## Quick Setup

### Option 1: Use Groq (Cloud)
```bash
# 1. Get free API key from console.groq.com
# 2. Add to .env
echo "GROQ_API_KEY=gsk_your_key" >> backend/.env

# 3. Install package (if not already)
cd backend
source venv/bin/activate
pip install groq

# 4. Restart backend
python app.py
```

### Option 2: Use Ollama (Local)
```bash
# 1. Install Ollama
brew install ollama

# 2. Download model
ollama pull llama3.2:1b

# 3. Start Ollama
ollama serve

# 4. Install package (if not already)
cd backend
source venv/bin/activate
pip install ollama

# 5. Restart backend
python app.py
```

### Option 3: Use Both (Recommended)
Set up both Groq and Ollama. The system will automatically:
- Use Groq when API key is set (best for mobile)
- Fall back to Ollama if Groq fails (privacy)
- Fall back to regex if both unavailable (always works)

---

## Testing

```bash
# Check provider status
curl http://localhost:8000/llm/status

# Test chat
curl -X POST "http://localhost:8000/chat?question=Hello"

# Test Gmail ingestion (now uses AI)
curl -X POST http://localhost:8000/ingest/gmail
```

---

## Documentation

- **[GROQ_SETUP.md](file:///Users/ajitreddy/Engineering/Projets/Deadline%20Reminder/GROQ_SETUP.md)** - Complete Groq setup guide
- **[OLLAMA_SETUP.md](file:///Users/ajitreddy/Engineering/Projets/Deadline%20Reminder/OLLAMA_SETUP.md)** - Ollama setup guide
- **[walkthrough.md](file:///Users/ajitreddy/.gemini/antigravity/brain/9978a667-7412-45db-bd94-3d58180d4d3f/walkthrough.md)** - Implementation walkthrough

---

## Provider Comparison

| Feature | Groq | Ollama | Regex |
|---------|------|--------|-------|
| **Speed** | ⚡⚡⚡ | ⚡⚡ | ⚡ |
| **Quality** | Excellent | Good | Basic |
| **Mobile** | ✅ Yes | ❌ No | ✅ Yes |
| **Privacy** | Cloud | 🔒 Local | 🔒 Local |
| **Setup** | Easy | Medium | None |
| **Cost** | Free* | Free | Free |

*14,400 requests/day on free tier
