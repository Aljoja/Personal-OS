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
        # Use absolute paths to avoid issues with working directory
        self.db_path = Path(db_path).absolute()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # SQLite for structured data
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
        
        # ChromaDB for semantic search (PERSISTENT!)
        embeddings_path_str = str(Path(embeddings_path).absolute())
        Path(embeddings_path_str).mkdir(parents=True, exist_ok=True)
        
        try:
            self.chroma_client = chromadb.PersistentClient(path=embeddings_path_str)
            
            # Collections
            self.facts = self.chroma_client.get_or_create_collection("facts")
            self.conversations = self.chroma_client.get_or_create_collection("conversations")
            self.files = self.chroma_client.get_or_create_collection("files")
            self.chroma_available = True
        except Exception as e:
            print(f"⚠️ Warning: ChromaDB initialization failed: {e}")
            print("   Semantic search will be disabled, but basic memory will work.")
            self.chroma_available = False
            self.facts = None
            self.conversations = None
            self.files = None
    
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
        
        # Add index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_facts_entity ON facts(entity)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_goals_status ON goals(status)
        """)
        
        self.conn.commit()
    
    def remember_fact(self, entity: str, fact: str, context: str = None) -> int:
        """Remember a fact about an entity"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO facts (entity, fact, context) VALUES (?, ?, ?)",
                (entity, fact, context)
            )
            self.conn.commit()
            fact_id = cursor.lastrowid
            
            # Add to vector DB if available
            if self.chroma_available and self.facts:
                try:
                    self.facts.add(
                        documents=[fact],
                        metadatas=[{"entity": entity, "context": context or ""}],
                        ids=[f"fact_{fact_id}"]
                    )
                except Exception as e:
                    print(f"⚠️ Warning: Failed to add fact to vector DB: {e}")
            
            return fact_id
        except sqlite3.Error as e:
            print(f"❌ Error saving fact: {e}")
            raise
    
    def recall(self, query: str, n_results: int = 5) -> List[Dict]:
        """Semantic search across all memories"""
        if not self.chroma_available or not self.facts:
            # Fallback to SQL search if ChromaDB unavailable
            return self._sql_search_facts(query, n_results)
        
        try:
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
        except Exception as e:
            print(f"⚠️ Warning: Semantic search failed, falling back to SQL: {e}")
            return self._sql_search_facts(query, n_results)
    
    def _sql_search_facts(self, query: str, limit: int = 5) -> List[Dict]:
        """Fallback SQL-based search"""
        try:
            cursor = self.conn.cursor()
            query_pattern = f"%{query}%"
            cursor.execute(
                """SELECT entity, fact, context FROM facts 
                   WHERE fact LIKE ? OR entity LIKE ? 
                   ORDER BY created_at DESC LIMIT ?""",
                (query_pattern, query_pattern, limit)
            )
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'fact': row['fact'],
                    'entity': row['entity'],
                    'context': row['context']
                })
            return results
        except sqlite3.Error as e:
            print(f"❌ Error in SQL search: {e}")
            return []
    
    def get_recent_facts(self, limit: int = 10) -> List[Dict]:
        """Get most recent facts"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT entity, fact, context FROM facts ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"❌ Error getting recent facts: {e}")
            return []
    
    def get_facts_about(self, entity: str) -> List[Dict]:
        """Get all facts about a specific entity"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM facts WHERE entity = ? ORDER BY created_at DESC",
                (entity,)
            )
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"❌ Error getting facts about {entity}: {e}")
            return []
    
    def save_preference(self, key: str, value: str, description: str = None):
        """Save a user preference"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """INSERT OR REPLACE INTO preferences (key, value, description, updated_at) 
                   VALUES (?, ?, ?, CURRENT_TIMESTAMP)""",
                (key, value, description)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"❌ Error saving preference: {e}")
            raise
    
    def get_preference(self, key: str) -> Optional[str]:
        """Get a user preference"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT value FROM preferences WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row['value'] if row else None
        except sqlite3.Error as e:
            print(f"❌ Error getting preference: {e}")
            return None
    
    def _extract_conversation_topic(self, conversation: List[Dict]) -> str:
        """Extract a simple topic from conversation"""
        if not conversation:
            return "general"
        
        # Get first user message (usually contains the main topic)
        first_user_msg = next((msg['content'] for msg in conversation if msg['role'] == 'user'), "")
        
        if not first_user_msg:
            return "general"
        
        # Take first 50 chars, clean it up
        topic = first_user_msg[:50].strip()
        
        # Remove common question words
        for word in ["what", "how", "why", "when", "where", "can you", "please", "help me"]:
            topic = topic.lower().replace(word, "").strip()
        
        # Clean up
        topic = " ".join(topic.split()[:5])  # Max 5 words
        topic = topic.strip(" ,.?!:")
        
        return topic if topic else "general"
    
    def save_conversation(self, conversation: List[Dict], topic: str = None):
        """Save a conversation to both ChromaDB AND text file"""
        if not conversation:
            return None
        
        timestamp = datetime.now()
        conv_id = f"conv_{timestamp.timestamp()}"
        
        # Auto-extract topic if not provided
        if not topic:
            topic = self._extract_conversation_topic(conversation)
        
        conv_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation])
        
        # 1. Save to ChromaDB (for semantic search) - only if available
        if self.chroma_available and self.conversations:
            try:
                self.conversations.add(
                    documents=[conv_text],
                    metadatas=[{"topic": topic, "timestamp": timestamp.isoformat()}],
                    ids=[conv_id]
                )
            except Exception as e:
                print(f"⚠️ Warning: ChromaDB conversation save failed: {e}")
        
        # 2. ALWAYS save to text file (for easy reading and backup)
        try:
            # Create dated folder
            date_folder = timestamp.strftime('%Y-%m-%d')  # 2024-11-16
            text_folder = Path("conversations") / date_folder
            text_folder.mkdir(parents=True, exist_ok=True)
            
            # Clean topic for filename
            clean_topic = topic.replace(" ", "_").replace("/", "-")[:30]  # Limit length
            filename = f"{timestamp.strftime('%H%M%S')}_{clean_topic}.txt"
            filepath = text_folder / filename
            
            # Write conversation to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("="*70 + "\n")
                f.write("PERSONAL OS CONVERSATION LOG\n")
                f.write("="*70 + "\n")
                f.write(f"Date: {timestamp.strftime('%A, %B %d, %Y')}\n")
                f.write(f"Time: {timestamp.strftime('%H:%M:%S')}\n")
                f.write(f"Topic: {topic}\n")
                f.write("="*70 + "\n\n")
                
                # Write each message with formatting
                for msg in conversation:
                    role = "YOU" if msg['role'] == 'user' else "CLAUDE"
                    content = msg['content']
                    
                    f.write(f"{role}:\n")
                    f.write(f"{content}\n")
                    f.write("\n" + "-"*70 + "\n\n")
                
                f.write("="*70 + "\n")
                f.write("END OF CONVERSATION\n")
                f.write("="*70 + "\n")
            
            # print(f"💾 Saved to: {filepath.relative_to(Path.cwd())}")
            
        except Exception as e:
            print(f"❌ Error saving conversation to file: {e}")
        
        return conv_id
    
    def add_goal(self, goal: str, deadline: str = None):
        """Add a goal"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO goals (goal, deadline) VALUES (?, ?)",
                (goal, deadline)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"❌ Error adding goal: {e}")
            raise
    
    def get_active_goals(self) -> List[Dict]:
        """Get active goals"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM goals WHERE status = 'active' ORDER BY created_at DESC"
            )
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"❌ Error getting active goals: {e}")
            return []
    
    def index_file(self, filepath: str, content: str, summary: str = None):
        """Index a file for search"""
        if not self.chroma_available or not self.files:
            print("⚠️ Warning: File indexing unavailable (ChromaDB not available)")
            return
        
        try:
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
        except Exception as e:
            print(f"❌ Error indexing file: {e}")
    
    def search_files(self, query: str, n_results: int = 3) -> List[Dict]:
        """Search indexed files"""
        if not self.chroma_available or not self.files:
            print("⚠️ File search unavailable (ChromaDB not available)")
            return []
        
        try:
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
        except Exception as e:
            print(f"❌ Error searching files: {e}")
            return []
    
    def recall_conversations(self, query: str, n_results: int = 3) -> List[Dict]:
        """Search past conversations"""
        if not self.chroma_available or not self.conversations:
            return []
        
        try:
            results = self.conversations.query(
                query_texts=[query],
                n_results=n_results
            )
            
            convos = []
            if results['documents'] and results['documents'][0]:
                for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
                    convos.append({
                        'conversation': doc,
                        'topic': metadata.get('topic'),
                        'timestamp': metadata.get('timestamp')
                    })
            
            return convos
        except Exception as e:
            print(f"⚠️ Warning: Conversation search failed: {e}")
            return []
    
    def get_conversations_by_date(self, date_str: str = None) -> List[Dict]:
        """Get conversations from a specific date
        
        Args:
            date_str: Date in format "2024-11-16" or None for today
        """
        from datetime import date
        
        if not self.chroma_available or not self.conversations:
            return []
        
        if date_str is None:
            date_str = date.today().isoformat()
        
        try:
            all_convs = self.conversations.get()
            
            if not all_convs['ids']:
                return []
            
            # Filter by date
            matching = []
            for doc, meta in zip(all_convs['documents'], all_convs['metadatas']):
                timestamp = meta.get('timestamp', '')
                if timestamp.startswith(date_str):
                    matching.append({
                        'conversation': doc,
                        'topic': meta.get('topic'),
                        'timestamp': timestamp
                    })
            
            # Sort by timestamp
            matching.sort(key=lambda x: x['timestamp'])
            
            return matching
        except Exception as e:
            print(f"⚠️ Warning: get_conversations_by_date failed: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        try:
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
        except Exception as e:
            print(f"⚠️ Warning: Error closing database: {e}")
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()