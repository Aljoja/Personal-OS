"""Main interactive interface for Personal OS"""

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
        print("\nCommands:")
        print("  chat        - Natural conversation")
        print("  remember    - Manually save a fact")
        print("  recall      - Search your memories")
        print("  goals       - Manage goals")
        print("  style       - Set writing style")
        print("  edit        - Apply your style to text")
        print("  files       - Search indexed files")
        print("  clear       - Clear conversation")
        print("  quit        - Exit")
        print("\nTip: Just type naturally - I'll remember important things!\n")
        
        while True:
            try:
                user_input = input("\n💭 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'quit':
                    # Save conversation periodically
                    # if len(self.conversation) % 10 == 0:
                    if self.conversation:
                        self.memory.save_conversation(self.conversation)
                        # print('[DEBUG] Conversation saved!')
                    print("\n👋 Goodbye!")
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
                        print("\n📚 Found memories:")
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
                    text = input("Text to edit:\n").strip()
                    edited = self.claude.apply_writing_style(text)
                    print(f"\n✨ Edited:\n{edited}")
                    continue
                
                elif user_input.lower() == 'files':
                    query = input("Search files for: ").strip()
                    files = self.memory.search_files(query)
                    if files:
                        print("\n📁 Found files:")
                        for f in files:
                            print(f"\n  File: {f['filepath']}")
                            print(f"  Summary: {f['summary']}")
                            print(f"  Preview: {f['content'][:200]}...")
                    else:
                        print("No files found")
                    continue
                
                # Default: natural conversation
                print("\n🤖 Claude: ", end="", flush=True)
                
                response = self.claude.chat(user_input, self.conversation)
                print(response)
                
                # Update conversation history
                self.conversation.append({"role": "user", "content": user_input})
                self.conversation.append({"role": "assistant", "content": response})
            
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
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
                print("\nActive goals:")
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
