# Ollama Setup Guide for Deadline Reminder App

## What is Ollama?

Ollama lets you run powerful AI models locally on your Mac for FREE. The Deadline Reminder app uses it for:
- **Better deadline extraction** from emails (understands "next Friday", "end of month", etc.)
- **Chat interface** to query your deadlines ("What's due this week?")

## Installation

### Step 1: Install Ollama

Visit [https://ollama.ai](https://ollama.ai) and download Ollama for Mac.

Or install via command line:
```bash
curl https://ollama.ai/install.sh | sh
```

### Step 2: Download a Model

We recommend the lightweight **Llama 3.2 1B** model (only ~1GB):

```bash
ollama pull llama3.2:1b
```

Other good options:
- `phi3:mini` - Microsoft's lightweight model (~2GB)
- `gemma2:2b` - Google's model (~1.6GB)
- `llama3.1:8b` - More powerful but larger (~4.7GB)

### Step 3: Verify Installation

```bash
ollama list
```

You should see your downloaded model(s).

### Step 4: Test Ollama

```bash
ollama run llama3.2:1b "Hello!"
```

If you see a response, Ollama is working!

## Using LLM Features in Deadline Reminder

### 1. Check LLM Status

```bash
curl http://localhost:8000/llm/status
```

Response when working:
```json
{
  "available": true,
  "models": ["llama3.2:1b"],
  "recommended_model": "llama3.2:1b",
  "suggested_questions": [...]
}
```

### 2. Test Gmail Ingestion with LLM

The app will automatically use LLM for better deadline extraction:

```bash
curl -X POST http://localhost:8000/ingest/gmail
```

The LLM will extract deadlines even from phrases like:
- "due by end of next week"
- "registration closes Friday at 6pm"
- "submit before January ends"

### 3. Chat with Your Deadlines

```bash
curl -X POST "http://localhost:8000/chat?question=What%20deadlines%20do%20I%20have%20this%20week?"
```

Example questions:
- "What's my next deadline?"
- "Show me all urgent tasks"
- "What's due in January?"
- "Do I have any Gmail deadlines?"
- "When is the hackathon registration?"

## Troubleshooting

### "Ollama not running"

Start Ollama:
```bash
ollama serve
```

(Ollama should auto-start on Mac after installation)

### "Model not found"

Download the model:
```bash
ollama pull llama3.2:1b
```

### "LLM extraction failed, using regex fallback"

This is normal! The app will fall back to regex patterns if Ollama isn't available. Your app still works, just with simpler deadline detection.

## Performance Tips

1. **Keep Ollama running** - It starts automatically on Mac
2. **Use smaller models first** - `llama3.2:1b` is perfect for this use case
3. **Upgrade if needed** - If you want better accuracy, try `llama3.1:8b`

## Uninstalling

If you want to remove Ollama:
```bash
brew uninstall ollama  # If installed via Homebrew
# Or manually delete from Applications
```

---

**The app works WITHOUT Ollama** - it just uses simpler deadline detection. Ollama makes it smarter!
