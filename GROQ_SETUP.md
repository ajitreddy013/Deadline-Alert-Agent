# Groq API Setup Guide for Deadline Reminder App

## What is Groq?

**Groq** is a cloud-based AI inference platform that provides **lightning-fast** LLM responses. It's perfect for the Deadline Reminder app because:

- 🚀 **Extremely Fast** - Up to 300 tokens/second inference speed
- 💰 **Generous Free Tier** - 14,400 requests per day (free forever)
- 🌐 **Cloud-Based** - Works on mobile apps (unlike local Ollama)
- 🤖 **Top Models** - Access to Llama 3.3 70B, Mixtral 8x7B, Gemma 2, and more

## Why Use Groq Instead of Ollama?

| Feature | Groq (Cloud) | Ollama (Local) |
|---------|-------------|----------------|
| Speed | ⚡ Very Fast | 🐌 Slower |
| Mobile Support | ✅ Yes | ❌ No (requires local server) |
| Setup | Easy (just API key) | Medium (install + download models) |
| Privacy | Sends data to cloud | 🔒 100% local |
| Cost | Free (14,400 req/day) | Free (uses your hardware) |
| Models | Llama 3.3 70B, Mixtral | Llama 3.2 1B (smaller) |

**Recommendation**: Use **Groq for mobile deployment** and **Ollama for local development** if privacy is important.

---

## Installation

### Step 1: Get Your Free Groq API Key

1. Visit [console.groq.com](https://console.groq.com)
2. Sign up for a free account (GitHub/Google login supported)
3. Navigate to **API Keys** section
4. Click **Create API Key**
5. Copy your API key (starts with `gsk_...`)

### Step 2: Configure the App

Add your API key to the environment file:

```bash
# Create .env file if it doesn't exist
cd backend
cp .env.example .env
```

Edit `.env` and add your Groq API key:

```bash
# LLM Configuration
GROQ_API_KEY=gsk_your_actual_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
LLM_PROVIDER=auto
```

### Step 3: Install Dependencies

```bash
pip install groq
# or
pip install -r requirements.txt
```

### Step 4: Restart the Backend

```bash
python app.py
```

---

## Using Groq Features

### 1. Check LLM Status

```bash
curl http://localhost:8000/llm/status
```

**Response when Groq is configured:**
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
    ...
  ]
}
```

### 2. Gmail Ingestion with AI

The app will **automatically use Groq** for better deadline extraction:

```bash
curl -X POST http://localhost:8000/ingest/gmail
```

Groq can understand complex deadline phrases like:
- "Registration closes by end of next week"
- "Submit before January ends"
- "Due Friday at 6pm EST"
- "Deadline is the last day of Q1"

### 3. Chat with Your Deadlines

```bash
curl -X POST "http://localhost:8000/chat?question=What%20deadlines%20do%20I%20have%20this%20week?"
```

**Example questions:**
- "What's my next deadline?"
- "Show me all Gmail deadlines"
- "What's due in the next 3 days?"
- "Do I have any urgent tasks?"
- "When is the hackathon registration?"

**Response:**
```json
{
  "answer": "You have 2 deadlines this week: Project submission on Jan 20 and Team meeting on Jan 17.",
  "provider": "groq",
  "context_tasks": 5
}
```

---

## Available Models

You can change the model in `.env`:

```bash
GROQ_MODEL=llama-3.3-70b-versatile  # Best quality, fast
# GROQ_MODEL=llama-3.1-8b-instant   # Faster, good quality
# GROQ_MODEL=mixtral-8x7b-32768     # Longer context window
# GROQ_MODEL=gemma2-9b-it           # Google's model
```

### Model Comparison

| Model | Speed | Quality | Best For |
|-------|-------|---------|----------|
| llama-3.3-70b-versatile | Fast | Excellent | General use (recommended) |
| llama-3.1-8b-instant | Very Fast | Good | Quick queries |
| mixtral-8x7b-32768 | Fast | Excellent | Long emails |
| gemma2-9b-it | Fast | Good | Alternative option |

---

## Automatic Fallback System

The app uses a **smart fallback system**:

```
1. Try Groq (if API key is set)
   ↓ fails
2. Try Ollama (if running locally)
   ↓ fails
3. Use Regex (always works)
```

This means:
- ✅ **Always works** - Even without API keys
- ✅ **Best quality when available** - Uses Groq when configured
- ✅ **Privacy option** - Can use Ollama for local-only processing
- ✅ **Zero config option** - Regex works out of the box

---

## Troubleshooting

### "Invalid API Key"

**Problem:** API key is incorrect or expired

**Solution:**
1. Double-check your API key at console.groq.com
2. Make sure it starts with `gsk_`
3. Ensure no extra spaces in `.env` file
4. Restart the backend after changing `.env`

### "Rate limit exceeded"

**Problem:** You've exceeded the free tier limit (14,400 requests/day)

**Solution:**
- The app will automatically fallback to Ollama or Regex
- Wait 24 hours for rate limit to reset
- Or consider Groq's paid tier for higher limits

### "Groq provider not available"

**Problem:** `groq` package not installed

**Solution:**
```bash
pip install groq
```

### "Using Ollama/Regex instead of Groq"

**Problem:** App is not using Groq even though it's configured

**Solution:**
1. Check if `GROQ_API_KEY` is set in `.env`
2. Make sure `.env` file is in the `backend/` directory
3. Verify API key is valid
4. Check logs for error messages

---

## Privacy & Security

### Is Groq Secure?

- ✅ Groq uses **TLS encryption** for all API calls
- ✅ Your API key is **private** and should never be shared
- ⚠️ Your emails **are sent to Groq's servers** for processing
- ⚠️ Groq may **store requests** for service improvement

### Should I Use Groq or Ollama?

| Use Case | Recommendation |
|----------|----------------|
| Mobile app deployment | **Groq** (Ollama won't work) |
| Sensitive/private emails | **Ollama** (100% local) |
| Best AI quality | **Groq** (larger models) |
| No internet access | **Ollama** (works offline) |
| Quick setup | **Groq** (just need API key) |

### Best Practice

For **maximum privacy**:
1. Use **Ollama locally** during development
2. Use **Groq** only for deployed mobile app
3. Add warning to users about cloud processing
4. Offer users a choice to disable AI features

---

## Cost & Limits

### Free Tier (Default)

- ✅ **14,400 requests per day** (600 per hour)
- ✅ **Forever free** - No credit card required
- ✅ **All models included**
- ✅ **No hidden fees**

For most users, this is **more than enough**!

**Example usage:**
- 100 emails/day with AI extraction = 100 requests
- 50 chat queries/day = 50 requests
- **Total: 150 requests/day** (well within free tier!)

### Paid Tier (Optional)

If you need more:
- Higher rate limits
- Priority support
- Enterprise features

Visit [groq.com/pricing](https://groq.com/pricing) for details.

---

## Comparison: Groq vs OpenAI vs Ollama

| Feature | Groq | OpenAI GPT-4 | Ollama |
|---------|------|-------------|--------|
| Free Tier | 14,400/day | Limited trial | Unlimited |
| Speed | ⚡⚡⚡ | ⚡ | ⚡⚡ |
| Privacy | Cloud | Cloud | 🔒 Local |
| Mobile Support | ✅ | ✅ | ❌ |
| Setup | Easy | Easy | Medium |
| Best Model | Llama 3.3 70B | GPT-4 | Llama 3.2 8B |

---

## Uninstalling

To stop using Groq:

```bash
# Remove from .env
GROQ_API_KEY=

# Or switch provider
LLM_PROVIDER=ollama  # or 'regex'
```

The app will automatically fall back to other providers.

---

## Next Steps

1. ✅ Get your [free Groq API key](https://console.groq.com)
2. ✅ Add it to `.env` file
3. ✅ Restart the backend
4. ✅ Test with `/llm/status` endpoint
5. ✅ Try chat queries!

**Need help?** Check out:
- [Groq Documentation](https://console.groq.com/docs)
- [OLLAMA_SETUP.md](./OLLAMA_SETUP.md) - For local LLM setup
- [README.md](./README.md) - Main project documentation

---

**The app works WITHOUT Groq** - it just uses simpler providers. Groq makes it smarter and faster! 🚀
