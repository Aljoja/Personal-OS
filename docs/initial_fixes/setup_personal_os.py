#!/usr/bin/env python3
"""
Personal OS Setup Script
========================
Run this single file to create your entire AI Operating System

Usage:
    python setup_personal_os.py

This will create a 'personal-os' folder with everything you need.
"""

import os
from pathlib import Path

# All project files embedded in this script
FILES = {
    "requirements.txt": """anthropic>=0.18.0
python-dotenv>=1.0.0
watchdog>=3.0.0
schedule>=1.2.0
chromadb>=0.4.0""",

    ".env.example": """ANTHROPIC_API_KEY=your_api_key_here
CLAUDE_MODEL=claude-sonnet-4-5-20250929
WATCHED_FOLDER=./files/watched""",

    ".gitignore": """.env
brain/*.db
brain/embeddings/
__pycache__/
*.pyc
logs/*.log
venv/
env/""",

    "README.md": """# Personal OS 🧠

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
""",

    "brain/__init__.py": '"""Brain module - memory and intelligence"""',

    "brain/memory.py": '''"""Persistent memory system with semantic search"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings


class Memory:
    """Persistent memory with semantic search"""
    
    def __init__(self, db_path: str = "brain/knowledge.db", 
                 embeddings_path: str = "brain/embeddings"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # SQLite for structured data
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_db()
        
        # ChromaDB for semantic search
        self.chroma_client = chromadb.Client(Settings(
            persist_directory=str(embeddings_path),
            anonymized_telemetry=False
        ))
        
        # Collections
        self.facts = self.chroma_client.get_or_create_collection("facts")
        self.conversations = self.chroma_client.get_or_create_collection("conversations")
        self.files = self.chroma_client.get_or_create_collection("files")
    
    def _init_db(self):
        """Initialize database tables"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity TEXT NOT NULL,
                fact TEXT NOT NULL,
                context TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                status TEXT DEFAULT 'active',
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal TEXT NOT NULL,
                deadline TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        
        self.conn.commit()
    
    def remember_fact(self, entity: str, fact: str, context: str = None) -> int:
        """Remember a fact about an entity"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO facts (entity, fact, context) VALUES (?, ?, ?)",
            (entity, fact, context)
        )
        self.conn.commit()
        fact_id = cursor.lastrowid
        
        # Add to vector DB
        self.facts.add(
            documents=[fact],
            metadatas=[{"entity": entity, "context": context or ""}],
            ids=[f"fact_{fact_id}"]
        )
        
        return fact_id
    
    def recall(self, query: str, n_results: int = 5) -> List[Dict]:
        """Semantic search across all memories"""
        results = self.facts.query(
            query_texts=[query],
            n_results=n_results
        )
        
        memories = []
        if results['documents'] and results['documents'][0]:
            for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
                memories.append({
                    'fact': doc,
                    'entity': metadata.get('entity'),
                    'context': metadata.get('context')
                })
        
        return memories
    
    def get_facts_about(self, entity: str) -> List[Dict]:
        """Get all facts about a specific entity"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM facts WHERE entity = ? ORDER BY created_at DESC",
            (entity,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def save_preference(self, key: str, value: str, description: str = None):
        """Save a user preference"""
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT OR REPLACE INTO preferences (key, value, description, updated_at) 
               VALUES (?, ?, ?, CURRENT_TIMESTAMP)""",
            (key, value, description)
        )
        self.conn.commit()
    
    def get_preference(self, key: str) -> Optional[str]:
        """Get a user preference"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM preferences WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row['value'] if row else None
    
    def save_conversation(self, conversation: List[Dict], topic: str = None):
        """Save a conversation"""
        conv_id = f"conv_{datetime.now().timestamp()}"
        conv_text = "\\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation])
        
        self.conversations.add(
            documents=[conv_text],
            metadatas=[{"topic": topic or "general", "timestamp": datetime.now().isoformat()}],
            ids=[conv_id]
        )
    
    def add_goal(self, goal: str, deadline: str = None):
        """Add a goal"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO goals (goal, deadline) VALUES (?, ?)",
            (goal, deadline)
        )
        self.conn.commit()
    
    def get_active_goals(self) -> List[Dict]:
        """Get active goals"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM goals WHERE status = 'active' ORDER BY created_at DESC"
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def index_file(self, filepath: str, content: str, summary: str = None):
        """Index a file for search"""
        file_id = f"file_{Path(filepath).name}_{datetime.now().timestamp()}"
        
        self.files.add(
            documents=[content],
            metadatas=[{
                "filepath": filepath,
                "summary": summary or "",
                "indexed_at": datetime.now().isoformat()
            }],
            ids=[file_id]
        )
    
    def search_files(self, query: str, n_results: int = 3) -> List[Dict]:
        """Search indexed files"""
        results = self.files.query(
            query_texts=[query],
            n_results=n_results
        )
        
        files = []
        if results['documents'] and results['documents'][0]:
            for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
                files.append({
                    'content': doc[:500] + "..." if len(doc) > 500 else doc,
                    'filepath': metadata.get('filepath'),
                    'summary': metadata.get('summary')
                })
        
        return files
''',

    "brain/claude_client.py": '''"""Enhanced Claude client with memory"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv
from typing import List, Dict
from .memory import Memory

load_dotenv()


class PersonalClaude:
    """Claude with memory and personality"""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")
        self.memory = Memory()
        
        self.base_system_prompt = """You are a personal AI operating system with persistent memory.

Your capabilities:
- Remember facts when user says "remember that..."
- Recall information when asked
- Apply saved preferences and styles
- Help organize thoughts and decisions
- Provide emotional support
- Maintain context across sessions

Be conversational, helpful, and proactive. You're a thought partner."""
    
    def chat(self, user_message: str, conversation_history: List[Dict] = None,
             include_memories: bool = True) -> str:
        """Chat with memory-augmented context"""
        
        system_prompt = self.base_system_prompt
        
        if include_memories:
            # Search for relevant memories
            memories = self.memory.recall(user_message, n_results=3)
            if memories:
                system_prompt += "\\n\\nRelevant memories:\\n"
                for mem in memories:
                    system_prompt += f"- {mem['entity']}: {mem['fact']}\\n"
            
            # Add active goals
            goals = self.memory.get_active_goals()
            if goals:
                system_prompt += "\\n\\nUser's active goals:\\n"
                for goal in goals[:3]:
                    system_prompt += f"- {goal['goal']}"
                    if goal['deadline']:
                        system_prompt += f" (deadline: {goal['deadline']})"
                    system_prompt += "\\n"
            
            # Add preferences
            writing_style = self.memory.get_preference("writing_style")
            if writing_style:
                system_prompt += f"\\n\\nUser's writing style: {writing_style}\\n"
        
        messages = conversation_history or []
        messages.append({"role": "user", "content": user_message})
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system_prompt,
            messages=messages
        )
        
        assistant_message = response.content[0].text
        self._process_memory_commands(user_message, assistant_message)
        
        return assistant_message
    
    def _process_memory_commands(self, user_msg: str, assistant_msg: str):
        """Extract memory commands from conversation"""
        user_lower = user_msg.lower()
        
        if "remember" in user_lower and ("that" in user_lower or ":" in user_msg):
            if "remember that" in user_lower:
                parts = user_msg.lower().split("remember that", 1)
                if len(parts) > 1:
                    fact = parts[1].strip()
                    entity = "general"
                    if " about " in fact:
                        entity = fact.split(" about ")[1].split()[0]
                    
                    self.memory.remember_fact(entity, fact, context=user_msg)
    
    def apply_writing_style(self, text: str) -> str:
        """Apply user's saved writing style"""
        style = self.memory.get_preference("writing_style")
        if not style:
            style = "casual, concise, active voice"
        
        prompt = f"Edit this text according to this style: {style}\\n\\nText:\\n{text}"
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def summarize_file(self, content: str, filename: str) -> str:
        """Summarize a file and index it"""
        prompt = f"Summarize this file ({filename}) in 2-3 sentences:\\n\\n{content[:5000]}"
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        summary = response.content[0].text
        self.memory.index_file(filename, content, summary)
        
        return summary
''',

    "automation/__init__.py": '"""Automation module"""',

    "automation/file_watcher.py": '''"""Watch folder and auto-process new files"""

import os
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from brain.claude_client import PersonalClaude


class FileHandler(FileSystemEventHandler):
    """Handle file events"""
    
    def __init__(self, claude: PersonalClaude):
        self.claude = claude
        self.processed = set()
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        filepath = event.src_path
        if filepath in self.processed:
            return
        
        time.sleep(1)
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if len(content.strip()) > 0:
                print(f"\\n📄 New file: {Path(filepath).name}")
                summary = self.claude.summarize_file(content, filepath)
                print(f"✅ Indexed:\\n{summary}\\n")
                
                self.processed.add(filepath)
        
        except Exception as e:
            print(f"Error processing {filepath}: {e}")


def start_watching(folder: str = "./files/watched"):
    """Start watching a folder"""
    folder_path = Path(folder)
    folder_path.mkdir(parents=True, exist_ok=True)
    
    print(f"👀 Watching: {folder_path.absolute()}")
    print("Drop files here - they'll be auto-indexed!\\n")
    
    claude = PersonalClaude()
    event_handler = FileHandler(claude)
    observer = Observer()
    observer.schedule(event_handler, str(folder_path), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    start_watching()
''',

    "automation/morning_routine.py": '''"""Morning routine automation"""

import schedule
import time
from datetime import datetime
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from brain.claude_client import PersonalClaude


def morning_routine():
    """Run morning routine"""
    print(f"\\n☀️ Good morning! ({datetime.now().strftime('%A, %B %d, %Y')})\\n")
    
    claude = PersonalClaude()
    
    prompt = """It's the start of a new day. Please:
1. Review my active goals
2. Suggest 3 priorities for today based on what you know about me
3. Give me a brief motivational message

Keep it concise and actionable."""
    
    response = claude.chat(prompt)
    print(response)
    print("\\n" + "="*60 + "\\n")


def schedule_routines():
    """Schedule automated routines"""
    schedule.every().day.at("08:00").do(morning_routine)
    
    print("⏰ Scheduled: Morning routine at 8:00 AM")
    print("Running scheduler... (Ctrl+C to stop)\\n")
    
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    schedule_routines()
''',

    "main.py": '''"""Main interactive interface for Personal OS"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from brain.claude_client import PersonalClaude
from brain.memory import Memory

load_dotenv()


class PersonalOS:
    """Main interface for Personal OS"""
    
    def __init__(self):
        self.claude = PersonalClaude()
        self.memory = Memory()
        self.conversation = []
    
    def run(self):
        """Run the interactive interface"""
        print("="*60)
        print("🧠 Personal OS - Your AI Operating System")
        print("="*60)
        print("\\nCommands:")
        print("  chat        - Natural conversation")
        print("  remember    - Manually save a fact")
        print("  recall      - Search your memories")
        print("  goals       - Manage goals")
        print("  style       - Set writing style")
        print("  edit        - Apply your style to text")
        print("  files       - Search indexed files")
        print("  clear       - Clear conversation")
        print("  quit        - Exit")
        print("\\nTip: Just type naturally - I'll remember important things!\\n")
        
        while True:
            try:
                user_input = input("\\n💭 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'quit':
                    print("\\n👋 Goodbye!")
                    break
                
                elif user_input.lower() == 'clear':
                    self.conversation = []
                    print("✅ Conversation cleared")
                    continue
                
                elif user_input.lower() == 'remember':
                    entity = input("About (entity): ").strip()
                    fact = input("Fact: ").strip()
                    self.memory.remember_fact(entity, fact)
                    print("✅ Remembered!")
                    continue
                
                elif user_input.lower() == 'recall':
                    query = input("Search for: ").strip()
                    memories = self.memory.recall(query)
                    if memories:
                        print("\\n📚 Found memories:")
                        for mem in memories:
                            print(f"  • {mem['entity']}: {mem['fact']}")
                    else:
                        print("No memories found")
                    continue
                
                elif user_input.lower() == 'goals':
                    self._manage_goals()
                    continue
                
                elif user_input.lower() == 'style':
                    style = input("Describe your writing style: ").strip()
                    self.memory.save_preference("writing_style", style)
                    print("✅ Style saved!")
                    continue
                
                elif user_input.lower() == 'edit':
                    text = input("Text to edit:\\n").strip()
                    edited = self.claude.apply_writing_style(text)
                    print(f"\\n✨ Edited:\\n{edited}")
                    continue
                
                elif user_input.lower() == 'files':
                    query = input("Search files for: ").strip()
                    files = self.memory.search_files(query)
                    if files:
                        print("\\n📁 Found files:")
                        for f in files:
                            print(f"\\n  File: {f['filepath']}")
                            print(f"  Summary: {f['summary']}")
                            print(f"  Preview: {f['content'][:200]}...")
                    else:
                        print("No files found")
                    continue
                
                # Default: natural conversation
                print("\\n🤖 Claude: ", end="", flush=True)
                
                response = self.claude.chat(user_input, self.conversation)
                print(response)
                
                # Update conversation history
                self.conversation.append({"role": "user", "content": user_input})
                self.conversation.append({"role": "assistant", "content": response})
                
                # Save conversation periodically
                if len(self.conversation) % 10 == 0:
                    self.memory.save_conversation(self.conversation)
            
            except KeyboardInterrupt:
                print("\\n\\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\\n❌ Error: {e}")
    
    def _manage_goals(self):
        """Manage goals submenu"""
        print("\\n🎯 Goals Management")
        print("1. View active goals")
        print("2. Add new goal")
        print("3. Back")
        
        choice = input("Choice: ").strip()
        
        if choice == '1':
            goals = self.memory.get_active_goals()
            if goals:
                print("\\nActive goals:")
                for goal in goals:
                    print(f"  • {goal['goal']}", end="")
                    if goal['deadline']:
                        print(f" (deadline: {goal['deadline']})", end="")
                    print()
            else:
                print("No active goals")
        
        elif choice == '2':
            goal = input("Goal: ").strip()
            deadline = input("Deadline (optional): ").strip() or None
            self.memory.add_goal(goal, deadline)
            print("✅ Goal added!")


def main():
    """Entry point"""
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY not found in .env file")
        print("Please create a .env file with your API key")
        return 1
    
    os_system = PersonalOS()
    os_system.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''
}

def create_project():
    """Create the entire Personal OS project"""
    base_dir = Path("personal-os")
    
    print("\\n" + "="*60)
    print("🚀 Creating Personal OS")
    print("="*60)
    print(f"\\n📁 Location: {base_dir.absolute()}\\n")
    
    # Create directory structure
    directories = [
        "brain",
        "automation",
        "prompts/saved",
        "files/watched",
        "logs"
    ]
    
    for dir_path in directories:
        full_path = base_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {dir_path}/")
    
    # Create all files
    for filepath, content in FILES.items():
        full_path = base_dir / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Created file: {filepath}")
    
    print("\\n" + "="*60)
    print("✨ Personal OS created successfully!")
    print("="*60)
    print("\\n📋 Next steps:\\n")
    print(f"1. cd {base_dir}")
    print("2. pip install -r requirements.txt")
    print("3. cp .env.example .env")
    print("4. Edit .env and add your ANTHROPIC_API_KEY")
    print("5. python main.py")
    print("\\n🎉 You're ready to build your AI Operating System!\\n")
    print("Need help? Check the README.md file\\n")

if __name__ == "__main__":
    try:
        create_project()
    except Exception as e:
        print(f"\\n❌ Error: {e}")
        print("Please report this issue if it persists.\\n")