"""Persistent memory system with semantic search"""

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
        conv_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation])
        
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
