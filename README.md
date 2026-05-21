# Using LLMs Without API Keys

This project uses browser automation to access LLM web platforms without requiring API keys or billing setup.
Instead of official APIs, it automates a normal browser session and parses responses directly from the provider’s website.

Best suited for:

* Learning and experimentation
* AI chatbot prototypes
* Personal AI projects

Not suitable for large-scale production systems.

---

# Pros

* No API keys required
* No payment or billing setup
* Can support multiple providers
* Useful for rapid prototyping
* GUI debugging helps fix scraping issues

---

# Cons

* Higher latency than APIs
* Browser automation uses more RAM/CPU
* Website changes can break scraping
* Manual login may be required
* Limited control over model behavior

---

# How It Works

```text id="ppf5b"
Application
    ↓
Browser Automation
    ↓
LLM Web Platform
    ↓
Response Parsing
    ↓
API Response
```

Internal prompting forces the model to output plain text responses for easier parsing.
Better scraping/parsing logic can significantly improve reliability.

---

# Run Instructions

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Start Server

```bash
python main.py
```

The server will run locally on:

```text id="i6f2m"
http://localhost:8000
```

---

# API Usage

## Endpoint

```text id="6b58h"
POST /chat
```

## Request Body

```json
{
  "message": "Hello"
}
```

## Response

```json
{
  "response": "Hi! How can I help you?"
}
```

---

# Notes

* Login to the provider website may need to be done manually.
* Scraping selectors may require updates when provider UIs change.
* Currently only chatgpt is supported 
