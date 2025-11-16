"""Enhanced Claude client with memory"""

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
            # Search for relevant FACTS
            memories = self.memory.recall(user_message, n_results=5)
            
            # ALSO search for relevant CONVERSATIONS
            past_conversations = self.memory.recall_conversations(user_message, n_results=2)
            
            # Get recent facts
            cursor = self.memory.conn.cursor()
            cursor.execute("SELECT entity, fact FROM facts ORDER BY created_at DESC LIMIT 10")
            recent_facts = cursor.fetchall()
            
            if memories or recent_facts or past_conversations:
                system_prompt += "\n\n=== WHAT YOU KNOW ABOUT THE USER ===\n"
                
                # Add search results
                if memories:
                    system_prompt += "\nRelevant context:\n"
                    for mem in memories:
                        system_prompt += f"- {mem['entity']}: {mem['fact']}\n"
                
                # Add recent facts
                if recent_facts:
                    system_prompt += "\nRecent information:\n"
                    for row in recent_facts:
                        system_prompt += f"- {row[0]}: {row[1]}\n"
                
                # ADD PAST CONVERSATIONS
                if past_conversations:
                    system_prompt += "\n\nRelevant past conversations:\n"
                    for conv in past_conversations:
                        # Show a preview
                        preview = conv['conversation'][:300] + "..."
                        timestamp = conv['timestamp'][:10] if conv['timestamp'] else "Unknown"
                        system_prompt += f"\n[{timestamp}]\n{preview}\n"
            
            # Add active goals
            goals = self.memory.get_active_goals()
            if goals:
                system_prompt += "\n\nUser's active goals:\n"
                for goal in goals[:5]:
                    system_prompt += f"- {goal['goal']}"
                    if goal['deadline']:
                        system_prompt += f" (deadline: {goal['deadline']})"
                    system_prompt += "\n"
            
            # Add preferences
            writing_style = self.memory.get_preference("writing_style")
            if writing_style:
                system_prompt += f"\n\nUser's writing style: {writing_style}\n"
        
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
        
        prompt = f"Edit this text according to this style: {style}\n\nText:\n{text}"
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def summarize_file(self, content: str, filename: str) -> str:
        """Summarize a file and index it"""
        prompt = f"Summarize this file ({filename}) in 2-3 sentences:\n\n{content[:5000]}"
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        
        summary = response.content[0].text
        self.memory.index_file(filename, content, summary)
        
        return summary