"""Main interactive interface for Personal OS"""

import os
import sys
import signal
import atexit
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
        self.messages_since_save = 0
        self.save_interval = 10  # Save every 10 messages
        
        # Register cleanup handlers
        atexit.register(self._cleanup)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle interrupt signals gracefully"""
        print("\n\n⚠️ Interrupt received, saving conversation...")
        self._cleanup()
        sys.exit(0)
    
    def _cleanup(self):
        """Save conversation and close resources"""
        try:
            if self.conversation:
                self.memory.save_conversation(self.conversation)
                print("💾 Conversation saved!")
            
            # Close memory database
            self.memory.close()
        except Exception as e:
            print(f"⚠️ Warning during cleanup: {e}")
    
    def _save_conversation_if_needed(self):
        """Periodically save conversation to avoid data loss"""
        self.messages_since_save += 1
        
        if self.messages_since_save >= self.save_interval and self.conversation:
            try:
                self.memory.save_conversation(self.conversation)
                self.messages_since_save = 0
                # Silently save - don't interrupt user flow
            except Exception as e:
                print(f"⚠️ Warning: Failed to save conversation: {e}")
    
    def run(self):
        """Run the interactive interface"""
        print("="*60)
        print("🧠 Personal OS - Your AI Operating System")
        print("="*60)
        print("\nCommands:")
        print("  chat        - Natural conversation (default)")
        print("  remember    - Manually save a fact")
        print("  recall      - Search your memories")
        print("  goals       - Manage goals")
        print("  style       - Set writing style")
        print("  edit        - Apply your style to text")
        print("  files       - Search indexed files")
        print("  clear       - Clear conversation")
        print("  quit        - Exit")
        print("\nTip: Just type naturally - I'll remember important things!")
        print("     (Conversations auto-save every 10 messages)\n")
        
        while True:
            try:
                user_input = input("\n💭 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'quit':
                    self._cleanup()
                    print("\n👋 Goodbye!")
                    break
                
                elif user_input.lower() == 'clear':
                    # Save before clearing
                    if self.conversation:
                        self.memory.save_conversation(self.conversation)
                        print("💾 Previous conversation saved!")
                    
                    self.conversation = []
                    self.messages_since_save = 0
                    print("✅ Conversation cleared")
                    continue
                
                elif user_input.lower() == 'remember':
                    entity = input("About (entity): ").strip()
                    if not entity:
                        entity = "general"
                    
                    fact = input("Fact: ").strip()
                    if not fact:
                        print("❌ Fact cannot be empty")
                        continue
                    
                    try:
                        self.memory.remember_fact(entity, fact)
                        print("✅ Remembered!")
                    except Exception as e:
                        print(f"❌ Error: {e}")
                    continue
                
                elif user_input.lower() == 'recall':
                    query = input("Search for: ").strip()
                    if not query:
                        print("❌ Search query cannot be empty")
                        continue
                    
                    memories = self.memory.recall(query)
                    if memories:
                        print("\n📚 Found memories:")
                        for mem in memories:
                            entity = mem.get('entity', 'general')
                            fact = mem.get('fact', '')
                            print(f"  • {entity}: {fact}")
                    else:
                        print("No memories found")
                    continue
                
                elif user_input.lower() == 'goals':
                    self._manage_goals()
                    continue
                
                elif user_input.lower() == 'style':
                    style = input("Describe your writing style: ").strip()
                    if not style:
                        print("❌ Style cannot be empty")
                        continue
                    
                    try:
                        self.memory.save_preference("writing_style", style)
                        print("✅ Style saved!")
                    except Exception as e:
                        print(f"❌ Error: {e}")
                    continue
                
                elif user_input.lower() == 'edit':
                    print("Text to edit (press Enter twice when done):")
                    lines = []
                    empty_count = 0
                    while True:
                        line = input()
                        if line == "":
                            empty_count += 1
                            if empty_count >= 2:
                                break
                        else:
                            empty_count = 0
                            lines.append(line)
                    
                    text = "\n".join(lines).strip()
                    if not text:
                        print("❌ No text provided")
                        continue
                    
                    try:
                        edited = self.claude.apply_writing_style(text)
                        print(f"\n✨ Edited:\n{edited}")
                    except Exception as e:
                        print(f"❌ Error: {e}")
                    continue
                
                elif user_input.lower() == 'files':
                    query = input("Search files for: ").strip()
                    if not query:
                        print("❌ Search query cannot be empty")
                        continue
                    
                    files = self.memory.search_files(query)
                    if files:
                        print("\n📄 Found files:")
                        for f in files:
                            print(f"\n  File: {f.get('filepath', 'unknown')}")
                            if f.get('summary'):
                                print(f"  Summary: {f['summary']}")
                            content = f.get('content', '')
                            if content:
                                preview = content[:200]
                                print(f"  Preview: {preview}...")
                    else:
                        print("No files found")
                    continue
                
                # Default: natural conversation
                print("\n🤖 Claude: ", end="", flush=True)
                
                try:
                    response = self.claude.chat(user_input, self.conversation)
                    print(response)
                    
                    # Update conversation history
                    self.conversation.append({"role": "user", "content": user_input})
                    self.conversation.append({"role": "assistant", "content": response})
                    
                    # Periodically save conversation
                    self._save_conversation_if_needed()
                
                except Exception as e:
                    print(f"\n❌ Error during conversation: {e}")
                    # Save conversation even on error
                    if self.conversation:
                        print("💾 Saving conversation before handling error...")
                        try:
                            self.memory.save_conversation(self.conversation)
                        except:
                            pass
            
            except KeyboardInterrupt:
                print("\n\n⚠️ Interrupt received...")
                self._cleanup()
                print("👋 Goodbye!")
                break
            
            except EOFError:
                print("\n\n⚠️ End of input received...")
                self._cleanup()
                print("👋 Goodbye!")
                break
            
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                # Try to save conversation
                if self.conversation:
                    try:
                        self.memory.save_conversation(self.conversation)
                        print("💾 Conversation saved")
                    except:
                        print("⚠️ Could not save conversation")
    
    def _manage_goals(self):
        """Manage goals submenu"""
        print("\n🎯 Goals Management")
        print("1. View active goals")
        print("2. Add new goal")
        print("3. Back")
        
        choice = input("Choice: ").strip()
        
        if choice == '1':
            goals = self.memory.get_active_goals()
            if goals:
                print("\n📋 Active goals:")
                for goal in goals:
                    print(f"  • {goal['goal']}", end="")
                    if goal.get('deadline'):
                        print(f" (deadline: {goal['deadline']})", end="")
                    print()
            else:
                print("No active goals")
        
        elif choice == '2':
            goal = input("Goal: ").strip()
            if not goal:
                print("❌ Goal cannot be empty")
                return
            
            deadline = input("Deadline (optional, YYYY-MM-DD): ").strip() or None
            
            try:
                self.memory.add_goal(goal, deadline)
                print("✅ Goal added!")
            except Exception as e:
                print(f"❌ Error adding goal: {e}")


def main():
    """Entry point"""
    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY not found in environment")
        print("Please create a .env file with your API key:")
        print("  ANTHROPIC_API_KEY=sk-ant-...")
        return 1
    
    # Validate API key format
    if not api_key.startswith("sk-ant-"):
        print("⚠️ Warning: API key format looks unusual")
        print("   Expected format: sk-ant-...")
        response = input("Continue anyway? (y/n): ").strip().lower()
        if response != 'y':
            return 1
    
    try:
        os_system = PersonalOS()
        os_system.run()
        return 0
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        return 0
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())