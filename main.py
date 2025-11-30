"""Main interactive interface for Personal OS with Learning Tracker"""

import os
import sys
import signal
import atexit
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from brain.claude_client import PersonalClaude
from brain.memory import Memory
from brain.learning_tracker import LearningTracker
from brain.explanations import ExplanationManager

load_dotenv()


class PersonalOS:
    """Main interface for Personal OS"""
    
    def __init__(self):
        self.claude = PersonalClaude()
        self.memory = Memory()
        self.learning = LearningTracker()
        self.explanations = ExplanationManager()
        self.conversation = []
        self.messages_since_save = 0
        self.save_interval = 10  # Save every 10 messages
        self._cleanup_done = False
        
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

        # Check if already cleaned up
        if self._cleanup_done:
            return    # Already done, exit early

        try:
            if self.conversation:
                self.memory.save_conversation(self.conversation)
                print("💾 Conversation saved!")
                self._cleanup_done = True  # Mark as done
            
            # Close resources
            self.memory.close()
            self.learning.close()
        except Exception as e:
            print(f"⚠️ Warning during cleanup: {e}")
    
    def _save_conversation_if_needed(self):
        """Periodically save conversation to avoid data loss"""
        self.messages_since_save += 1
        
        if self.messages_since_save >= self.save_interval and self.conversation:
            try:
                self.memory.save_conversation(self.conversation)
                self.messages_since_save = 0
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
        print("  learn       - Learning & skills tracker  🎓")
        print("  explain     - Get & save explanations  🔖")
        print("  build       - Challenge-based learning lab 🏗️")
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
                
                elif user_input.lower() == 'learn':
                    self._learning_menu()
                    continue

                elif user_input.lower() == 'explain':
                    self._explanation_menu()
                    continue

                elif user_input.lower() == 'build':
                    self._challenge_lab_menu()
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
                if self.conversation:
                    try:
                        self.memory.save_conversation(self.conversation)
                        print("💾 Conversation saved")
                    except:
                        print("⚠️ Could not save conversation")
    
    def _learning_menu(self):
        """Learning tracking submenu"""
        while True:
            print("\n" + "="*60)
            print("🎓 Learning Tracker")
            print("="*60)
            
            # Show daily summary
            summary = self.learning.get_daily_review_summary()
            print(f"\n📊 Today's Summary:")
            print(f"  • {summary['items_due_for_review']} items due for review")
            print(f"  • {summary['skills_needing_attention']} skills need attention")
            print(f"  • {summary['sessions_this_week']} sessions this week")
            print(f"  • {summary['minutes_this_week']} minutes this week")
            
            print("\n📚 Options:")
            print("  1. View all skills")
            print("  2. Add new skill")
            print("  3. Log learning session")
            print("  4. Review items (spaced repetition)")
            print("  5. Add learning item (Q&A, concept, fact)")
            print("  6. Search learning items")
            print("  7. View skill details")
            print("  8. Learning statistics")
            print("  9. Manage milestones")
            print("  0. Back to main menu")
            
            choice = input("\nChoice: ").strip()
            
            if choice == '0':
                break
            
            elif choice == '1':
                self._view_all_skills()
            
            elif choice == '2':
                self._add_new_skill()
            
            elif choice == '3':
                self._log_learning_session()
            
            elif choice == '4':
                self._review_items()
            
            elif choice == '5':
                self._add_learning_item()
            
            elif choice == '6':
                self._search_learning_items()
            
            elif choice == '7':
                self._view_skill_details()
            
            elif choice == '8':
                self._view_learning_stats()
            
            elif choice == '9':
                self._manage_milestones()
            
            else:
                print("❌ Invalid choice")
    
    def _view_all_skills(self):
        """View all tracked skills"""
        skills = self.learning.get_all_skills()
        
        if not skills:
            print("\n📚 No skills being tracked yet")
            print("   Use option 2 to add your first skill!")
            return
        
        print("\n📚 Your Learning Journey:")
        print("-" * 80)
        for skill in skills:
            print(f"\n🎯 {skill['skill_name']} (ID: {skill['id']})")
            print(f"   Category: {skill['category'] or 'Uncategorized'}")
            print(f"   Difficulty: {skill['difficulty']} → Target: {skill['target_level'] or 'Not set'}")
            print(f"   Time invested: {skill['total_time_minutes']} minutes")
            print(f"   Sessions: {skill['session_count']} | Items: {skill['item_count']}")
            if skill['last_reviewed']:
                print(f"   Last reviewed: {skill['last_reviewed'][:10]}")
    
    def _add_new_skill(self):
        """Add a new skill to track"""
        print("\n➕ Add New Skill")
        
        skill_name = input("Skill name: ").strip()
        if not skill_name:
            print("❌ Skill name cannot be empty")
            return
        
        category = input("Category (e.g., Programming, Language, etc.): ").strip() or None
        
        print("\nDifficulty level:")
        print("  1. Beginner")
        print("  2. Intermediate")
        print("  3. Advanced")
        diff_choice = input("Choice (default: 1): ").strip() or "1"
        difficulty_map = {"1": "beginner", "2": "intermediate", "3": "advanced"}
        difficulty = difficulty_map.get(diff_choice, "beginner")
        
        target_level = input("Target level (e.g., 'Build web apps', 'Conversational'): ").strip() or None
        notes = input("Notes (optional): ").strip() or None
        
        try:
            skill_id = self.learning.add_skill(skill_name, category, difficulty, target_level, notes)
            print(f"\n✅ Skill added! (ID: {skill_id})")
            print("   Start your first session with option 3!")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _log_learning_session(self):
        """Log a learning session"""
        skills = self.learning.get_all_skills()
        if not skills:
            print("\n❌ No skills tracked yet. Add one first!")
            return
        
        print("\n📝 Log Learning Session")
        print("\nYour skills:")
        for skill in skills:
            print(f"  {skill['id']}. {skill['skill_name']}")
        
        skill_id = input("\nSkill ID: ").strip()
        if not skill_id.isdigit():
            print("❌ Invalid skill ID")
            return
        skill_id = int(skill_id)
        
        duration = input("Duration (minutes): ").strip()
        if not duration.isdigit() or duration == '0' or int(duration) < 0:
            print("❌ Invalid duration")
            return
        duration = int(duration)
        
        topics = input("What did you cover? ").strip()
        if not topics:
            print("❌ Topics cannot be empty")
            return
        
        print("\nUnderstanding level:")
        print("  1. Poor - Need to review again soon")
        print("  2. Below average - Some confusion")
        print("  3. Average - Got the basics")
        print("  4. Good - Feel confident")
        print("  5. Excellent - Mastered it!")
        
        understanding = input("Level (1-5): ").strip()
        if not understanding.isdigit() or int(understanding) not in range(1, 6):
            print("❌ Invalid understanding level")
            return
        understanding = int(understanding)
        
        notes = input("Session notes (optional): ").strip() or None
        takeaways = input("Key takeaways (optional): ").strip() or None
        
        try:
            session_id = self.learning.log_session(
                skill_id, duration, topics, understanding, notes, takeaways
            )
            print(f"\n✅ Session logged! (ID: {session_id})")
            
            # Calculate next review
            days_map = {1: 1, 2: 3, 3: 7, 4: 14, 5: 30}
            days = days_map.get(understanding, 7)
            print(f"📅 Next review scheduled in {days} days")
        except ValueError as e:
            # This catches our "skill doesn't exist" error
            print(f"❌ Error: {e}")
            print("💡 Use option 1 to view valid skill IDs")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    def _review_items(self):
        """Review learning items with spaced repetition"""
        items = self.learning.get_items_due_for_review(limit=10)
        
        if not items:
            print("\n✅ No items due for review right now!")
            print("   Great job staying on top of your learning!")
            return
        
        print(f"\n📖 {len(items)} items due for review")
        print("="*60)
        
        for i, item in enumerate(items, 1):
            print(f"\n[{i}/{len(items)}] {item['skill_name']}")
            print(f"Type: {item['item_type']}")
            
            if item['question']:
                print(f"\n❓ {item['question']}")
                input("\n[Press Enter to reveal answer]")
            
            print(f"\n💡 Answer: {item['answer']}")
            
            # Get review result
            correct = input("\nDid you get it right? (y/n): ").strip().lower()
            was_correct = correct == 'y'
            
            print("\nConfidence level:")
            print("  1. Very unsure")
            print("  2. Somewhat unsure")
            print("  3. Moderately confident")
            print("  4. Quite confident")
            print("  5. Very confident")
            
            confidence = input("How confident? (1-5): ").strip()
            if not confidence.isdigit() or int(confidence) not in range(1, 6):
                confidence = 3  # Default to moderate
            confidence = int(confidence)
            
            # Record review
            try:
                self.learning.record_review(
                    item['id'], was_correct, 
                    item['confidence_level'], confidence
                )
                
                if was_correct:
                    print("✅ Great job!")
                else:
                    print("📚 Don't worry, you'll see this again soon!")
                
            except Exception as e:
                print(f"⚠️ Error recording review: {e}")
            
            if i < len(items):
                cont = input("\nContinue to next item? (y/n): ").strip().lower()
                if cont != 'y':
                    break
        
        print("\n🎉 Review session complete!")
    
    def _add_learning_item(self):
        """Add a learning item"""
        skills = self.learning.get_all_skills()
        if not skills:
            print("\n❌ No skills tracked yet. Add one first!")
            return
        
        print("\n➕ Add Learning Item")
        print("\nYour skills:")
        for skill in skills:
            print(f"  {skill['id']}. {skill['skill_name']}")
        
        skill_id = input("\nSkill ID: ").strip()
        if not skill_id.isdigit():
            print("❌ Invalid skill ID")
            return
        skill_id = int(skill_id)
        
        print("\nItem type:")
        print("  1. Concept (definition, explanation)")
        print("  2. Fact (memorization)")
        print("  3. Q&A (question and answer)")
        print("  4. Example (code snippet, use case)")
        
        type_choice = input("Choice: ").strip()
        type_map = {"1": "concept", "2": "fact", "3": "qa", "4": "example"}
        item_type = type_map.get(type_choice, "concept")
        
        question = None
        if item_type == "qa":
            question = input("\nQuestion: ").strip()
            if not question:
                print("❌ Question cannot be empty for Q&A")
                return
        
        answer = input("Answer/Content: ").strip()
        if not answer:
            print("❌ Answer cannot be empty")
            return
        
        tags = input("Tags (comma-separated, optional): ").strip() or None
        source = input("Source (book, video, etc., optional): ").strip() or None
        
        try:
            item_id = self.learning.add_learning_item(
                skill_id, answer, question, item_type, tags=tags, source=source
            )
            print(f"\n✅ Learning item added! (ID: {item_id})")
            print("📅 Scheduled for review tomorrow")
        except ValueError as e:
            # This catches our "skill doesn't exist" error
            print(f"❌ Error: {e}")
            print("💡 Use option 1 to view valid skill IDs")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    def _search_learning_items(self):
        """Search learning items"""
        query = input("\n🔍 Search for: ").strip()
        if not query:
            print("❌ Search query cannot be empty")
            return
        
        items = self.learning.search_learning_items(query)
        
        if not items:
            print("\n❌ No items found")
            return
        
        print(f"\n📚 Found {len(items)} items:")
        print("="*60)
        
        for item in items:
            print(f"\n🎯 {item['skill_name']} ({item['item_type']})")
            if item['question']:
                print(f"   Q: {item['question']}")
            print(f"   A: {item['answer'][:100]}..." if len(item['answer']) > 100 else f"   A: {item['answer']}")
            print(f"   Confidence: {item['confidence_level']}/5 | Reviewed: {item['times_reviewed']} times")
    
    def _view_skill_details(self):
        """View detailed information about a skill"""
        skills = self.learning.get_all_skills()
        if not skills:
            print("\n❌ No skills tracked yet")
            return
        
        print("\nYour skills:")
        for skill in skills:
            print(f"  {skill['id']}. {skill['skill_name']}")
        
        skill_id = input("\nSkill ID: ").strip()
        if not skill_id.isdigit():
            print("❌ Invalid skill ID")
            return
        
        try:
            details = self.learning.get_skill_details(int(skill_id))
            
            print("\n" + "="*60)
            print(f"🎯 {details['skill_name']}")
            print("="*60)
            
            print(f"\n📊 Overview:")
            print(f"   Category: {details['category'] or 'Uncategorized'}")
            print(f"   Difficulty: {details['difficulty']} → {details['target_level'] or 'No target set'}")
            print(f"   Status: {details['status']}")
            print(f"   Total time: {details['total_time_minutes']} minutes ({details['total_time_minutes']//60}h {details['total_time_minutes']%60}m)")
            
            if details['notes']:
                print(f"   Notes: {details['notes']}")
            
            stats = details['stats']
            print(f"\n📈 Statistics:")
            print(f"   Items: {stats['total_items']}")
            print(f"   Reviews: {stats['total_reviews'] or 0}")
            print(f"   Correct: {stats['total_correct'] or 0}")
            if stats['avg_confidence']:
                print(f"   Avg confidence: {stats['avg_confidence']:.1f}/5")
            
            if details['recent_sessions']:
                print(f"\n📝 Recent Sessions ({len(details['recent_sessions'])}):")
                for session in details['recent_sessions'][:3]:
                    print(f"   • {session['session_date'][:10]}: {session['topics_covered'][:50]}...")
                    print(f"     {session['duration_minutes']}min, understanding: {session['understanding_level']}/5")
        except ValueError as e:
            # This catches our "skill doesn't exist" error
            print(f"❌ Error: {e}")
            print("💡 Use option 1 to view valid skill IDs")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    def _view_learning_stats(self):
        """View learning statistics"""
        print("\n📊 Learning Statistics")
        
        period = input("Period (7/30/90 days, default: 30): ").strip()
        if not period.isdigit():
            period = 30
        else:
            period = int(period)
        
        try:
            stats = self.learning.get_learning_stats(days=period)
            
            print(f"\n📈 Last {period} days:")
            print("="*60)
            print(f"⏰ Time invested: {stats['total_hours']} hours ({stats['total_minutes']} minutes)")
            print(f"📅 Average per day: {stats['avg_minutes_per_day']} minutes")
            print(f"🎯 Review accuracy: {stats['review_accuracy']}%")
            print(f"📚 Total reviews: {stats['total_reviews']}")
            
            if stats['by_skill']:
                print(f"\n📚 By Skill:")
                for skill_stat in stats['by_skill']:
                    hours = skill_stat['total_minutes'] // 60
                    mins = skill_stat['total_minutes'] % 60
                    print(f"   • {skill_stat['skill_name']}: {hours}h {mins}m ({skill_stat['session_count']} sessions)")
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _manage_milestones(self):
        """Manage learning milestones"""
        skills = self.learning.get_all_skills()
        if not skills:
            print("\n❌ No skills tracked yet")
            return
        
        print("\nYour skills:")
        for skill in skills:
            print(f"  {skill['id']}. {skill['skill_name']}")
        
        skill_id = input("\nSkill ID: ").strip()
        if not skill_id.isdigit():
            print("❌ Invalid skill ID")
            return
        skill_id = int(skill_id)
        
        print("\n1. View milestones")
        print("2. Add milestone")
        print("3. Complete milestone")
        
        choice = input("\nChoice: ").strip()
        
        if choice == '1':
            milestones = self.learning.get_milestones(skill_id, include_completed=True)
            if not milestones:
                print("\n📌 No milestones set yet")
                return
            
            print("\n📌 Milestones:")
            for m in milestones:
                status = "✅" if m['completed'] else "⏳"
                target = f" (target: {m['target_date']})" if m['target_date'] else ""
                print(f"   {status} [{m['id']}] {m['milestone']}{target}")
        
        elif choice == '2':
            milestone = input("Milestone: ").strip()
            if not milestone:
                print("❌ Milestone cannot be empty")
                return
            
            target_date = input("Target date (YYYY-MM-DD, optional): ").strip() or None
            notes = input("Notes (optional): ").strip() or None
            
            try:
                m_id = self.learning.add_milestone(skill_id, milestone, target_date, notes)
                print(f"✅ Milestone added! (ID: {m_id})")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif choice == '3':
            milestones = self.learning.get_milestones(skill_id)
            if not milestones:
                print("\n❌ No pending milestones")
                return
            
            print("\nPending milestones:")
            for m in milestones:
                print(f"   {m['id']}. {m['milestone']}")
            
            m_id = input("\nMilestone ID to complete: ").strip()
            if not m_id.isdigit():
                print("❌ Invalid milestone ID")
                return
            
            try:
                self.learning.complete_milestone(int(m_id))
                print("🎉 Milestone completed! Great progress!")
            except Exception as e:
                print(f"❌ Error: {e}")
    
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

    def _explanation_menu(self):
        """
        Handle explanation requests
        
        Flow:
        1. Show user's skills
        2. Get skill choice
        3. Get topic
        4. Generate explanation with Claude
        5. Show explanation
        6. Ask to save
        
        Why this flow:
        - Skill first = provides context for explanation
        - Topic from user = they know what they need
        - Show before save = user can decide quality
        """
        print("\n" + "="*60)
        print("📖 Explanation Assistant")
        print("="*60)
        
        # Get user's skills
        skills = self.learning.get_all_skills()
        
        if not skills:
            print("\n⚠️ No skills found. Add a skill first with 'learn' command.")
            return
        
        # Show skills
        print("\nYour skills:")
        for idx, skill in enumerate(skills, 1):
            print(f"  {idx}. {skill['skill_name']}")
        
        # Get skill choice
        try:
            choice = input("\nWhich skill? (number or 0 to cancel): ").strip()
            if choice == '0':
                return
            
            skill_idx = int(choice) - 1
            if skill_idx < 0 or skill_idx >= len(skills):
                print("❌ Invalid choice")
                return
            
            selected_skill = skills[skill_idx]
            
        except (ValueError, IndexError):
            print("❌ Invalid choice")
            return
        
        # Get topic
        topic = input("\nWhat topic do you want explained?\nTopic: ").strip()
        
        if not topic:
            print("❌ Topic cannot be empty")
            return
        
        # Get optional custom guidance with shortcuts
        print("\nCustomization (optional - press Enter to skip):")
        print("\nQuick options:")
        print("  1. Brief & simple")
        print("  2. Lots of examples")
        print("  3. Like I'm 5 (ELI5)")
        print("  4. Advanced/deep dive")
        print("  5. Custom (type your own)")
        print("  [Enter] Skip customization")

        guidance_choice = input("\nChoice: ").strip()

        custom_guidance = None

        if guidance_choice == '1':
            custom_guidance = "Keep this explanation brief and simple, focusing on the core concept only"
        elif guidance_choice == '2':
            custom_guidance = "Provide lots of practical examples showing different use cases"
        elif guidance_choice == '3':
            custom_guidance = "Explain this like I'm 5 years old, using simple analogies and avoiding jargon"
        elif guidance_choice == '4':
            custom_guidance = "Provide an advanced, in-depth explanation with edge cases and best practices"
        elif guidance_choice == '5':
            custom_input = input("Your custom guidance: ").strip()
            if custom_input:
                custom_guidance = custom_input

        # If empty, set to None
        if not custom_guidance:
            custom_guidance = None
                
        # Check if explanation already exists
        if self.explanations.explanation_exists(
            selected_skill['id'], 
            selected_skill['skill_name'], 
            topic
        ):
            print(f"\n⚠️ Explanation for '{topic}' already exists")
            choice = input("View existing? (y/n): ").strip().lower()
            
            if choice == 'y':
                self._view_explanation(
                    selected_skill['id'],
                    selected_skill['skill_name'],
                    topic
                )
            return
        
        # Generate explanation
        print(f"\n🤔 Generating explanation for '{topic}'...")
        
        try:
            # Get explanation from Claude
            response = self.claude.generate_explanation(
                topic,
                selected_skill['skill_name'],
                selected_skill['difficulty'],
                custom_guidance=custom_guidance
            )
            
            # Show explanation
            print("\n" + "="*60)
            print(f"📖 {topic.title()}")
            print("="*60)
            print(response)
            print("="*60)
            
            # Ask to save
            save_choice = input("\n💾 Save this explanation? (y/n): ").strip().lower()
            
            if save_choice == 'y':
                # Save with metadata header
                content = f"# {topic.title()}\n\n"
                content += f"**Skill:** {selected_skill['skill_name']}\n"
                content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"

                # Add custom guidance to metadata if provided
                if custom_guidance:
                    content += f"**Custom Request:** {custom_guidance}\n"

                content += "\n---\n\n"
                content += response
                
                success, filepath = self.explanations.save_explanation(
                    selected_skill['id'],
                    selected_skill['skill_name'],
                    topic,
                    content
                )
                
                if success:
                    print(f"✅ Saved to: {filepath}")
                else:
                    print(f"❌ Failed to save: {filepath}")
            
        except Exception as e:
            print(f"❌ Error generating explanation: {e}")


    def _view_explanation(self, skill_id: int, skill_name: str, topic: str):
        """
        Display a saved explanation
        
        Why separate method:
        - Can be called from multiple places
        - Single responsibility
        - Reusable logic
        """
        content = self.explanations.get_explanation(skill_id, skill_name, topic)
        
        if content is None:
            print(f"❌ Explanation not found: {topic}")
            return
        
        print("\n" + "="*60)
        print(content)
        print("="*60)
        
        # Offer options
        print("\nOptions:")
        print("  1. Request new explanation (replace)")
        print("  2. Back to menu")
        
        choice = input("\nChoice: ").strip()
        
        if choice == '1':
            self._replace_explanation(skill_id, skill_name, topic)


    def _replace_explanation(self, skill_id: int, skill_name: str, topic: str):
        """
        Generate new explanation and replace existing one
        
        Why separate method:
        - Handles replacement logic
        - Confirms before overwriting
        - Reusable for future features
        """
        print(f"\n🤔 Generating new explanation for '{topic}'...")
        
        # Similar to _explanation_menu but for replacement
        # (Implementation similar to above, but replaces existing file)
        # For brevity, user can expand on this
        
        print("💡 Feature hint: Implement similar to _explanation_menu")
        print("   but skip existence check and show comparison")

    def _challenge_lab_menu(self):
        """Challenge-based learning lab - main menu"""
        from brain.challenge_library import ChallengeLibrary
        
        challenge_lib = ChallengeLibrary()
        
        while True:
            print("\n" + "="*60)
            print("🏗️  Challenge-Based Learning Lab")
            print("="*60)
            
            # Show streak
            streak_stats = self.learning.get_streak_stats()
            if streak_stats['current_streak'] > 0:
                print(f"\n🔥 Current streak: {streak_stats['current_streak']} days")
            
            # Show in-progress challenges
            in_progress = self.learning.get_all_challenges(status='in_progress')
            if in_progress:
                print(f"\n⚙️  {len(in_progress)} challenge(s) in progress")
            
            print("\nOptions:")
            print("  1. Start new challenge")
            print("  2. Continue challenge")
            print("  3. Log obstacle")
            print("  4. View skill progression")
            print("  5. Search past obstacles")
            print("  6. View all challenges")
            print("  0. Back to main menu")
            
            choice = input("\nChoice: ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                self._start_new_challenge(challenge_lib)
            elif choice == '2':
                self._continue_challenge()
            elif choice == '3':
                self._log_obstacle()
            elif choice == '4':
                self._view_skill_progression()
            elif choice == '5':
                self._search_obstacles()
            elif choice == '6':
                self._view_all_challenges()
            else:
                print("❌ Invalid choice")

    def _start_new_challenge(self, challenge_lib):
        """Browse and start a new challenge"""
        
        print("\n" + "="*60)
        print("📚 Challenge Library")
        print("="*60)
        
        # Get user's skills
        skills = self.learning.get_all_skills()
        if not skills:
            print("\n⚠️  No skills found. Add a skill first with 'learn' command.")
            return
        
        # Show skills
        print("\nYour skills:")
        for idx, skill in enumerate(skills, 1):
            # Get progression for this skill
            progression = self.learning.get_skill_progression(skill['id'])
            level = progression['competency_level']
            completed = progression['completed'] or 0
            print(f"  {idx}. {skill['skill_name']} - {level} ({completed} completed)")
        
        # Select skill
        try:
            choice = input("\nWhich skill? (number or 0 to cancel): ").strip()
            if choice == '0':
                return
            
            skill_idx = int(choice) - 1
            if skill_idx < 0 or skill_idx >= len(skills):
                print("❌ Invalid choice")
                return
            
            selected_skill = skills[skill_idx]
        except (ValueError, IndexError):
            print("❌ Invalid choice")
            return
        
        # Map skill name to challenge category
        # (You'll need to map your skill names to challenge categories)
        skill_name_lower = selected_skill['skill_name'].lower()
        
        if 'python' in skill_name_lower:
            category = 'python'
        elif 'data' in skill_name_lower or 'analysis' in skill_name_lower:
            category = 'data_analysis'
        elif 'machine' in skill_name_lower or 'ml' in skill_name_lower:
            category = 'machine_learning'
        elif 'digital' in skill_name_lower or 'iot' in skill_name_lower:
            category = 'digitalization'
        else:
            # Show all categories
            category = None
        
        # Get challenges
        if category:
            challenges = challenge_lib.get_challenges_for_skill(category)
        else:
            all_challenges = challenge_lib.get_all_challenges()
            challenges = []
            for cat, chals in all_challenges.items():
                challenges.extend([{**c, 'category': cat} for c in chals])
        
        if not challenges:
            print(f"\n⚠️  No challenges found for {selected_skill['skill_name']}")
            print("💡 You can add custom challenges!")
            return
        
        # Show challenges
        print(f"\n📋 Challenges for {selected_skill['skill_name']}:")
        print()
        
        for idx, challenge in enumerate(challenges, 1):
            diff_emoji = {'beginner': '🟢', 'intermediate': '🟡', 'advanced': '🔴'}
            emoji = diff_emoji.get(challenge['difficulty'], '⚪')
            
            print(f"{idx}. {emoji} {challenge['title']}")
            print(f"   Difficulty: {challenge['difficulty'].title()} | Est. time: {challenge['estimated_hours']}h")
            print(f"   Teaches: {', '.join(challenge['skills_taught'][:3])}...")
            print()
        
        # Select challenge
        try:
            choice = input("Which challenge? (number or 0 to cancel): ").strip()
            if choice == '0':
                return
            
            challenge_idx = int(choice) - 1
            if challenge_idx < 0 or challenge_idx >= len(challenges):
                print("❌ Invalid choice")
                return
            
            selected_challenge = challenges[challenge_idx]
        except (ValueError, IndexError):
            print("❌ Invalid choice")
            return
        
        # Show full description
        print("\n" + "="*60)
        print(f"📖 {selected_challenge['title']}")
        print("="*60)
        print(f"\nDifficulty: {selected_challenge['difficulty'].title()}")
        print(f"Estimated time: {selected_challenge['estimated_hours']} hours")
        print(f"\nDescription:")
        print(selected_challenge['description'])
        print(f"\nSkills you'll learn:")
        for skill in selected_challenge['skills_taught']:
            print(f"  • {skill}")
        
        # Confirm start
        start = input("\n🚀 Start this challenge? (y/n): ").strip().lower()
        
        if start == 'y':
            # Add to database
            challenge_id = self.learning.add_challenge(
                title=selected_challenge['title'],
                description=selected_challenge['description'],
                skill_id=selected_skill['id'],
                difficulty=selected_challenge['difficulty'],
                estimated_hours=selected_challenge['estimated_hours'],
                skills_taught=selected_challenge['skills_taught'],
                prerequisites=selected_challenge['prerequisites'],
                unlocks=selected_challenge.get('unlocks', [])
            )
            
            # Start challenge
            self.learning.start_challenge(challenge_id)
            
            print(f"\n✅ Challenge started! (ID: {challenge_id})")
            print("💡 Use 'build' → 'Continue challenge' to work on it")
            print("💡 Log obstacles as you encounter them!")

    def _continue_challenge(self):
        """Continue working on an in-progress challenge"""
        
        # Get in-progress challenges
        in_progress = self.learning.get_all_challenges(status='in_progress')
        
        if not in_progress:
            print("\n⚠️  No challenges in progress")
            print("💡 Start a new challenge first!")
            return
        
        print("\n" + "="*60)
        print("⚙️  Challenges in Progress")
        print("="*60)
        
        for idx, challenge in enumerate(in_progress, 1):
            print(f"\n{idx}. {challenge['title']}")
            print(f"   Progress: {challenge['progress_percent']}%")
            print(f"   Time spent: {challenge['time_spent'] // 60}h {challenge['time_spent'] % 60}m")
            
            # Show obstacles
            obstacles = self.learning.get_obstacles_for_challenge(challenge['id'])
            blocking = [o for o in obstacles if o['status'] == 'blocking']
            if blocking:
                print(f"   ⚠️  {len(blocking)} blocking obstacle(s)")
        
        # Select challenge
        try:
            choice = input("\nWhich challenge? (number or 0 to cancel): ").strip()
            if choice == '0':
                return
            
            challenge_idx = int(choice) - 1
            if challenge_idx < 0 or challenge_idx >= len(in_progress):
                print("❌ Invalid choice")
                return
            
            selected_challenge = in_progress[challenge_idx]
        except (ValueError, IndexError):
            print("❌ Invalid choice")
            return
        
        # Work session
        print("\n" + "="*60)
        print(f"🛠️  Working on: {selected_challenge['title']}")
        print("="*60)
        
        # Show current obstacles
        obstacles = self.learning.get_obstacles_for_challenge(selected_challenge['id'])
        blocking = [o for o in obstacles if o['status'] == 'blocking']
        
        if blocking:
            print("\n⚠️  Current blockers:")
            for obs in blocking:
                print(f"  • {obs['obstacle_description']}")
        
        print("\nWhat do you want to do?")
        print("  1. Update progress")
        print("  2. Log new obstacle")
        print("  3. Solve obstacle")
        print("  4. Complete challenge")
        print("  0. Back")
        
        action = input("\nChoice: ").strip()
        
        if action == '1':
            # Update progress
            try:
                progress = int(input("\nCurrent progress %: ").strip())
                minutes = int(input("Minutes worked this session: ").strip())
                notes = input("Notes (optional): ").strip()
                
                self.learning.update_challenge_progress(
                    selected_challenge['id'],
                    progress,
                    minutes,
                    notes if notes else None
                )
                
                # Log streak
                self.learning.log_daily_streak(minutes, selected_challenge['id'])
                
                print("\n✅ Progress updated!")
                
            except ValueError:
                print("❌ Invalid input")
        
        elif action == '2':
            # Log obstacle
            obstacle = input("\nWhat's blocking you?: ").strip()
            if obstacle:
                self.learning.log_obstacle(selected_challenge['id'], obstacle)
                print("\n✅ Obstacle logged!")
                print("💡 Work on solving it, then come back to mark it solved")
        
        elif action == '3':
            # Solve obstacle
            if not blocking:
                print("\n⚠️  No blocking obstacles for this challenge")
                return
            
            print("\nWhich obstacle did you solve?")
            for idx, obs in enumerate(blocking, 1):
                print(f"  {idx}. {obs['obstacle_description']}")
            
            try:
                obs_choice = int(input("\nObstacle #: ").strip()) - 1
                if 0 <= obs_choice < len(blocking):
                    selected_obs = blocking[obs_choice]
                    
                    solution = input("\nHow did you solve it?: ").strip()
                    insight = input("What did you learn?: ").strip()
                    minutes = input("Minutes to solve (optional): ").strip()
                    
                    self.learning.solve_obstacle(
                        selected_obs['id'],
                        solution,
                        insight if insight else None,
                        int(minutes) if minutes else None
                    )
                    
                    print("\n✅ Obstacle marked as solved!")
                    print("🎉 You're building problem-solving skills!")
                    
            except (ValueError, IndexError):
                print("❌ Invalid input")
        
        elif action == '4':
            # Complete challenge
            print("\n🎉 Complete challenge?")
            confirm = input("Are you sure? (yes/no): ").strip().lower()
            
            if confirm == 'yes':
                github = input("\nGitHub link (optional): ").strip()
                notes = input("Final notes/learnings: ").strip()
                
                self.learning.complete_challenge(
                    selected_challenge['id'],
                    github if github else None,
                    notes if notes else None
                )
                
                print("\n✅ Challenge completed!")
                print("🏆 Skill progression updated!")
                print("💡 Check your skill progression to see your growth")

    def _log_obstacle(self):
        """Quick log obstacle for any challenge"""
        
        in_progress = self.learning.get_all_challenges(status='in_progress')
        
        if not in_progress:
            print("\n⚠️  No challenges in progress")
            return
        
        print("\nWhich challenge?")
        for idx, challenge in enumerate(in_progress, 1):
            print(f"  {idx}. {challenge['title']}")
        
        try:
            choice = int(input("\nChallenge #: ").strip()) - 1
            if 0 <= choice < len(in_progress):
                selected = in_progress[choice]
                
                obstacle = input("\nWhat's blocking you?: ").strip()
                if obstacle:
                    self.learning.log_obstacle(selected['id'], obstacle)
                    print("\n✅ Obstacle logged!")
            else:
                print("❌ Invalid choice")
        except (ValueError, IndexError):
            print("❌ Invalid input")

    def _view_skill_progression(self):
        """View skill progression based on challenges"""
        
        skills = self.learning.get_all_skills()
        if not skills:
            print("\n⚠️  No skills found")
            return
        
        print("\n" + "="*60)
        print("📊 Your Skill Progression")
        print("="*60)
        
        for skill in skills:
            progression = self.learning.get_skill_progression(skill['id'])
            
            print(f"\n{skill['skill_name']}: {progression['competency_level'].upper()}")
            
            # Progress bar
            percent = progression['competency_percent']
            filled = int(percent / 10)
            bar = '█' * filled + '░' * (10 - filled)
            print(f"  [{bar}] {percent}%")
            
            print(f"  Projects completed: {progression['completed'] or 0}")
            print(f"  In progress: {progression['in_progress'] or 0}")
            print(f"  Obstacles overcome: {progression['solved_obstacles'] or 0}")
            print(f"  Total time: {(progression['total_minutes'] or 0) // 60}h")

    def _search_obstacles(self):
        """Search past obstacles and solutions"""
        
        keyword = input("\nSearch for (keyword): ").strip()
        
        if not keyword:
            return
        
        results = self.learning.search_past_obstacles(keyword)
        
        if not results:
            print(f"\n⚠️  No obstacles found matching '{keyword}'")
            return
        
        print(f"\n Found {len(results)} obstacle(s):\n")
        
        for idx, obs in enumerate(results, 1):
            print(f"{idx}. [{obs['skill_name']}] {obs['challenge_title']}")
            print(f"   Problem: {obs['obstacle_description']}")
            if obs['solution']:
                print(f"   Solution: {obs['solution'][:100]}...")
            if obs['insight']:
                print(f"   💡 {obs['insight']}")
            print()
        
        # Option to view full details
        view = input("View full details? (number or 0 to skip): ").strip()
        if view and view != '0':
            try:
                idx = int(view) - 1
                if 0 <= idx < len(results):
                    obs = results[idx]
                    print("\n" + "="*60)
                    print(f"🔍 {obs['challenge_title']}")
                    print("="*60)
                    print(f"\nSkill: {obs['skill_name']}")
                    print(f"Problem:\n{obs['obstacle_description']}")
                    print(f"\nSolution:\n{obs['solution']}")
                    if obs['insight']:
                        print(f"\nInsight:\n{obs['insight']}")
                    if obs['time_to_solve']:
                        print(f"\nTime to solve: {obs['time_to_solve']} minutes")
            except (ValueError, IndexError):
                pass

    def _view_all_challenges(self):
        """View all challenges organized by status"""
        
        not_started = self.learning.get_all_challenges(status='not_started')
        in_progress = self.learning.get_all_challenges(status='in_progress')
        completed = self.learning.get_all_challenges(status='completed')
        
        print("\n" + "="*60)
        print("📋 All Challenges")
        print("="*60)
        
        if completed:
            print(f"\n✅ Completed ({len(completed)}):")
            for c in completed:
                print(f"  • {c['title']}")
        
        if in_progress:
            print(f"\n⚙️  In Progress ({len(in_progress)}):")
            for c in in_progress:
                print(f"  • {c['title']} - {c['progress_percent']}%")
        
        if not_started:
            print(f"\n📚 Available ({len(not_started)}):")
            for c in not_started[:5]:  # Show first 5
                print(f"  • {c['title']}")
            if len(not_started) > 5:
                print(f"  ... and {len(not_started) - 5} more")

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
