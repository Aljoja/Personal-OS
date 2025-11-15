# Personal OS 🧠

Your AI operating system with memory, automation, and personalized assistance.

## Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure:**
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

3. **Run:**
```bash
python main.py
```

## Features

✅ **Persistent Memory**: Remembers facts, preferences, conversations  
✅ **Natural Language**: Just talk naturally, it learns about you  
✅ **File Watching**: Auto-indexes files dropped in watched folder  
✅ **Semantic Search**: Find anything you've told it  
✅ **Goal Tracking**: Set and track your goals  
✅ **Writing Style**: Save your style and apply it to any text  
✅ **Morning Routine**: Automated daily briefing

## Try These

**Natural conversation:**
```
You: Remember that notes_summary.md contains my main project ideas
You: What files did I tell you about?
You: Help me decide whether to move to Madrid
```

**Commands:**
```
remember    - Save a fact manually
recall      - Search your memories
goals       - Manage goals
style       - Set writing style
edit        - Apply style to text
files       - Search indexed files
```

## Running Services

**File watcher (auto-index files):**
```bash
python -m automation.file_watcher
```

**Morning routine scheduler:**
```bash
python -m automation.morning_routine
```

## Examples

### Save Writing Style
```
You: style
Describe your writing style: casual, max 150 words, active voice

You: edit
Text to edit: [paste your text]
✨ [Gets edited version]
```

### Auto-Index Files
Drop files into `files/watched/` and they're automatically summarized!

### Search Everything
```
You: recall madrid
📚 Found memories about madrid
```

## File Structure
```
personal-os/
├── brain/              # Memory & intelligence
│   ├── knowledge.db   # SQLite database
│   ├── embeddings/    # Vector DB
│   ├── memory.py      # Memory system
│   └── claude_client.py
├── files/
│   └── watched/       # Drop files here
├── automation/
│   ├── file_watcher.py
│   └── morning_routine.py
└── main.py            # Start here
```
