"""Enhanced Claude client with memory"""

import os
import re
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
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        
        # Validate API key format (basic check)
        if not self.api_key.startswith("sk-ant-"):
            print("⚠️ Warning: API key format looks unusual. Expected format: sk-ant-...")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")
        self.memory = Memory()
        
        self.base_system_prompt = """You are a personal AI operating system with persistent memory.
        
Your capabilities:
- Remember facts when user says "remember that...", "don't forget...", "keep in mind that..."
- Recall information when asked
- Apply saved preferences and styles
- Help organize thoughts and decisions
- Provide emotional support
- Maintain context across sessions

Be conversational, helpful, and proactive. You're a thought partner.

When the user shares important information naturally in conversation, you can suggest:
"Would you like me to remember that?" to help build their knowledge base."""
    
    def chat(self, user_message: str, conversation_history: List[Dict] = None,
            include_memories: bool = True) -> str:
        """Chat with memory-augmented context"""
        
        system_prompt = self.base_system_prompt
        
        if include_memories:
            # Collect all memories
            all_facts = []
            
            # 1. Semantic search for relevant facts
            relevant_facts = self.memory.recall(user_message, n_results=5)
            all_facts.extend(relevant_facts)
            
            # 2. Get recent facts (might overlap with semantic search)
            recent_facts = self.memory.get_recent_facts(limit=10)
            for fact in recent_facts:
                all_facts.append({
                    'entity': fact['entity'],
                    'fact': fact['fact'],
                    'context': fact.get('context')
                })
            
            # 3. Deduplicate facts
            unique_facts = self._deduplicate_facts(all_facts)
            
            # 4. Search for relevant conversations (if available)
            past_conversations = self.memory.recall_conversations(user_message, n_results=2)
            
            # Build context section
            if unique_facts or past_conversations:
                system_prompt += "\n\n=== WHAT YOU KNOW ABOUT THE USER ===\n"
                
                if unique_facts:
                    system_prompt += "\nRelevant information:\n"
                    for mem in unique_facts[:15]:  # Limit to prevent token bloat
                        entity = mem.get('entity', 'general')
                        fact = mem.get('fact', '')
                        system_prompt += f"- {entity}: {fact}\n"
                
                # Add past conversations (with truncation)
                if past_conversations:
                    system_prompt += "\n\nRelevant past conversations:\n"
                    for conv in past_conversations:
                        preview = conv['conversation'][:300] + "..."
                        timestamp = conv.get('timestamp', '')[:10] if conv.get('timestamp') else "Unknown"
                        topic = conv.get('topic', 'general')
                        system_prompt += f"\n[{timestamp} - {topic}]\n{preview}\n"
            
            # Add active goals (if any)
            goals = self.memory.get_active_goals()
            if goals:
                system_prompt += "\n\nUser's active goals:\n"
                for goal in goals[:5]:  # Limit to 5 most recent
                    system_prompt += f"- {goal['goal']}"
                    if goal['deadline']:
                        system_prompt += f" (deadline: {goal['deadline']})"
                    system_prompt += "\n"
            
            # Add preferences
            writing_style = self.memory.get_preference("writing_style")
            if writing_style:
                system_prompt += f"\n\nUser's writing style: {writing_style}\n"
        
        # Prepare messages - use shallow copy to avoid modifying original
        messages = list(conversation_history) if conversation_history else []
        messages.append({"role": "user", "content": user_message})
        
        # Truncate conversation history if too long (keep last 20 exchanges = 40 messages)
        if len(messages) > 40:
            messages = messages[-40:]
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=messages
            )
            
            assistant_message = response.content[0].text
            
            # Process any memory commands in the user's message
            self._process_memory_commands(user_message, assistant_message)
            
            return assistant_message
        
        except Exception as e:
            print(f"❌ Error calling Claude API: {e}")
            raise

    def generate_explanation(self, topic: str, skill_name: str, 
                            skill_level: str) -> str:
        """
        Generate a structured explanation for learning
        
        Why separate from chat():
        - Different purpose (teaching vs. conversation)
        - Different system prompt (teacher vs. assistant)
        - No memory context needed (topic is self-contained)
        - Optimized for speed (no memory lookups)
        - Focused on educational quality
        
        Args:
            topic: What to explain (e.g., "list comprehensions")
            skill_name: Skill context (e.g., "Python Programming")
            skill_level: User's level (e.g., "beginner", "intermediate")
        
        Returns:
            Markdown-formatted explanation
        """
        # Custom system prompt for teaching
        system_prompt = (
            "You are an expert teacher providing clear, structured explanations. "
            "Your goal is to help learners deeply understand concepts. "
            "Format your response in Markdown with:\n"
            "- Clear headers for sections\n"
            "- Bullet points for key concepts\n"
            "- Code blocks for examples\n"
            "- Emphasis on practical application\n"
            "Keep explanations concise but thorough."
        )
        
        # Build focused prompt
        user_message = f"""I am learning {skill_name} at a {skill_level} level.

    Please explain: {topic}

    Structure your explanation with:
    1. **Overview**: Brief introduction (2-3 sentences)
    2. **Key Concepts**: Main ideas to understand
    3. **Examples**: Practical demonstrations
    4. **Common Pitfalls**: What to watch out for
    5. **Practice Tips**: How to master this
    6. **Related Topics**: What to explore next

    Keep it practical and actionable."""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,  # ← Custom prompt for teaching
                messages=[{"role": "user", "content": user_message}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            print(f"❌ Error generating explanation: {e}")
            raise
    
    def _deduplicate_facts(self, facts_list: List[Dict]) -> List[Dict]:
        """Remove duplicate facts based on entity and fact content"""
        seen = set()
        unique = []
        
        for fact in facts_list:
            # Create a unique key from entity and fact
            entity = fact.get('entity', '').lower().strip()
            fact_text = fact.get('fact', '').lower().strip()
            key = f"{entity}:{fact_text}"
            
            if key not in seen and fact_text:  # Only add non-empty facts
                seen.add(key)
                unique.append(fact)
        
        return unique
    
    def _process_memory_commands(self, user_msg: str, assistant_msg: str):
        """Extract and process memory commands from conversation
        
        Recognizes patterns like:
        - "remember that X"
        - "don't forget X"
        - "please remember X"
        - "keep in mind that X"
        """
        user_lower = user_msg.lower()
        
        # Pattern 1: "remember that..." or "remember to..." or "don't forget..."
        remember_patterns = [
            r"remember that (.+?)(?:\.|$)",
            r"remember to (.+?)(?:\.|$)",
            r"don't forget (?:that )?(.+?)(?:\.|$)",
            r"please remember (?:that )?(.+?)(?:\.|$)",
            r"keep in mind (?:that )?(.+?)(?:\.|$)",
        ]
        
        for pattern in remember_patterns:
            match = re.search(pattern, user_lower, re.IGNORECASE)
            if match:
                fact = match.group(1).strip()
                
                # Try to extract entity (subject of the fact)
                entity = self._extract_entity(fact)
                
                try:
                    self.memory.remember_fact(entity, fact, context=user_msg)
                    # Don't print confirmation - let the assistant handle it naturally
                except Exception as e:
                    print(f"⚠️ Warning: Failed to save memory: {e}")
                
                break  # Only process first match
    
    def _extract_entity(self, fact: str) -> str:
        """Try to extract the main entity/subject from a fact"""
        # Simple heuristic: look for common patterns
        
        # Pattern: "X is/was/has/lives..."
        match = re.match(r"^(\w+(?:\s+\w+)?)\s+(?:is|was|has|have|lives?|works?|likes?)", fact, re.IGNORECASE)
        if match:
            return match.group(1).lower()
        
        # Pattern: "my X..."
        match = re.search(r"my (\w+(?:\s+\w+)?)", fact, re.IGNORECASE)
        if match:
            return f"user's {match.group(1).lower()}"
        
        # Pattern: "I am/have/like/live..."
        if fact.startswith("i "):
            return "user"
        
        # Default: use first few words or "general"
        words = fact.split()[:2]
        if words:
            return " ".join(words).lower()
        
        return "general"
    
    def apply_writing_style(self, text: str) -> str:
        """Apply user's saved writing style"""
        style = self.memory.get_preference("writing_style")
        if not style:
            style = "casual, concise, active voice"
        
        prompt = f"Edit this text according to this style: {style}\n\nText:\n{text}"
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
        except Exception as e:
            print(f"❌ Error applying writing style: {e}")
            return text  # Return original text on error
    
    def summarize_file(self, content: str, filename: str) -> str:
        """Summarize a file and index it"""
        # Truncate very large files
        content_preview = content[:10000] if len(content) > 10000 else content
        
        prompt = f"Summarize this file ({filename}) in 2-3 sentences:\n\n{content_preview}"
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            
            summary = response.content[0].text
            
            # Index the file
            self.memory.index_file(filename, content, summary)
            
            return summary
        except Exception as e:
            print(f"❌ Error summarizing file: {e}")
            return f"File: {filename} (summary failed)"