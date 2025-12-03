"""Main interactive interface for Personal OS with Learning Tracker"""

import os
import sys
import signal
import atexit
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from sympy import re
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
            print("  3. Add skill with AI roadmap 🤖")
            print("  4. Log learning session")
            print("  5. Review items (spaced repetition)")
            print("  6. Add learning item (Q&A, concept, fact)")
            print("  7. Search learning items")
            print("  8. View skill details")
            print("  9. Learning statistics")
            print("  10. Manage milestones")
            print("  0. Back to main menu")
            
            choice = input("\nChoice: ").strip()
            
            if choice == '0':
                break
            
            elif choice == '1':
                self._view_all_skills()
            
            elif choice == '2':
                self._add_new_skill()

            elif choice == '3':
                self._add_skill_with_roadmap()
            
            elif choice == '4':
                self._log_learning_session()
            
            elif choice == '5':
                self._review_items()
            
            elif choice == '6':
                self._add_learning_item()
            
            elif choice == '7':
                self._search_learning_items()
            
            elif choice == '8':
                self._view_skill_details()
            
            elif choice == '9':
                self._view_learning_stats()
            
            elif choice == '10':
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

        # Sort by ID
        skills = sorted(skills, key=lambda s: s['id'])

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

            # Get challenge progression (if any)
            progression = self.learning.get_skill_progression(int(skill_id))
            
            completed = progression.get('completed') or 0
            in_progress = progression.get('in_progress') or 0
            solved_obstacles = progression.get('solved_obstacles') or 0

            if completed > 0 or in_progress > 0:
                print(f"\n🏗️  Challenge Progress:")
                print(f"   Completed: {completed}")
                print(f"   In progress: {in_progress}")
                print(f"   Obstacles solved: {solved_obstacles}")
                print(f"   Competency: {progression['competency_level']} ({progression['competency_percent']}%)")
            
            # Check roadmap status
            cursor = self.learning.conn.cursor()
            cursor.execute("""
                SELECT roadmap_generated, goals, current_level, timeline 
                FROM learning_skills 
                WHERE id = ?
            """, (int(skill_id),))
            roadmap_data = cursor.fetchone()
            
            has_roadmap = roadmap_data['roadmap_generated'] if roadmap_data else 0
            
            print("\n" + "-"*60)
            if has_roadmap:
                print("✅ AI Learning Roadmap: Generated")
                if roadmap_data['goals']:
                    goals_preview = roadmap_data['goals'][:80]
                    if len(roadmap_data['goals']) > 80:
                        goals_preview += "..."
                    print(f"   {goals_preview}")
            else:
                print("⚠️  AI Learning Roadmap: Not generated")
                print("   💡 Generate a personalized roadmap with challenge recommendations")
            
            # Roadmap options
            print("\n" + "-"*60)
            print("Options:")
            
            if not has_roadmap:
                print("  1. Generate AI roadmap for this skill 🤖")
                print("  2. View challenges for this skill")
                print("  0. Back")
                
                option = input("\nChoice: ").strip()
                
                if option == '1':
                    # Get skill name for the method call
                    skill_name = details['skill_name']
                    self._generate_roadmap_for_existing_skill(int(skill_id), skill_name)
                elif option == '2':
                    # Show challenges
                    challenges = self.learning.get_all_challenges(skill_id=int(skill_id))
                    if challenges:
                        print(f"\n📋 Challenges for {details['skill_name']}:")
                        for c in challenges:
                            status_icon = {'completed': '✅', 'in_progress': '⚙️', 'not_started': '📋', 'abandoned': '❌'}
                            icon = status_icon.get(c['status'], '❓')
                            print(f"   {icon} {c['title']} ({c['difficulty']}, {c['estimated_hours']}h)")
                    else:
                        print("\n💡 No challenges yet. Generate a roadmap to create challenges!")
                    input("\nPress Enter to continue...")
            else:
                print("  1. View full roadmap context")
                print("  2. Add more challenges to roadmap")
                print("  3. View challenges for this skill")
                print("  0. Back")
                
                option = input("\nChoice: ").strip()
                
                if option == '1':
                    # Show full roadmap details
                    print("\n" + "="*60)
                    print(f"📋 Learning Roadmap: {details['skill_name']}")
                    print("="*60)
                    
                    if roadmap_data['current_level']:
                        print("\n📊 Level Assessment:")
                        print(roadmap_data['current_level'])
                    
                    if roadmap_data['goals']:
                        print("\n🎯 Goals & Focus:")
                        print(roadmap_data['goals'])
                    
                    if roadmap_data['timeline']:
                        print(f"\n⏱️  Timeline: {roadmap_data['timeline']}")
                    
                    input("\nPress Enter to continue...")
                
                elif option == '2':
                    confirm = input("\n⚠️  Add more challenges? (existing preserved) (y/n): ").strip().lower()
                    if confirm == 'y':
                        skill_name = details['skill_name']
                        self._generate_roadmap_for_existing_skill(int(skill_id), skill_name)
                
                elif option == '3':
                    # Show challenges
                    challenges = self.learning.get_all_challenges(skill_id=int(skill_id))
                    if challenges:
                        print(f"\n📋 Challenges for {details['skill_name']}:")
                        for c in challenges:
                            status_icon = {'completed': '✅', 'in_progress': '⚙️', 'not_started': '📋', 'abandoned': '❌'}
                            icon = status_icon.get(c['status'], '❓')
                            print(f"   {icon} {c['title']} ({c['difficulty']}, {c['estimated_hours']}h)")
                            if c['status'] == 'in_progress':
                                print(f"       Progress: {c['progress_percent']}%, Time: {c['time_spent']}min")
                    else:
                        print("\n💡 No challenges yet. Generate a roadmap to create challenges!")
                    input("\nPress Enter to continue...")

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
            print("  5. Get recommendation 🎯")
            print("  6. View learning path 🗺️")
            print("  7. Search past obstacles")
            print("  8. View all challenges")
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
                self._get_recommendation()
            elif choice == '6':
                self._view_learning_path()
            elif choice == '7':
                self._search_obstacles()
            elif choice == '8':
                self._view_all_challenges()
            else:
                print("❌ Invalid choice")

    def _start_new_challenge(self, challenge_lib): # TODO: fix - still using challenge_lib
        """Browse and start a new challenge"""
        
        print("\n" + "="*60)
        print("📚 Challenge Library")
        print("="*60)
        
        # Get user's skills
        skills = self.learning.get_all_skills()
        if not skills:
            print("\n⚠️  No skills found. Add a skill first with 'learn' command.")
            return
        
        # Sort by ID
        skills = sorted(skills, key=lambda s: s['id'])

        # Show skills
        print("\nYour skills:")
        for skill in skills:
            # Get progression for this skill
            progression = self.learning.get_skill_progression(skill['id'])
            level = progression['competency_level']
            completed = progression['completed'] or 0
            print(f"  {skill['id']}. {skill['skill_name']} - {level} ({completed} completed)")
        
        # Select skill
        try:
            choice = input("\nWhich skill? (number or 0 to cancel): ").strip()
            if choice == '0':
                return
            
            skill_id = int(choice)
            if skill_id < 0 or skill_id >= len(skills):
                print("❌ Invalid choice")
                return
            
            # selected_skill = skills[skill_idx]
        except (ValueError, IndexError):
            print("❌ Invalid choice")
            return
        
        # Get all challenges
        challenges = self.learning.get_all_challenges(skill_id=skill_id, status='not_started')
        
        if not challenges:
            print(f"\n⚠️  No challenges found for {skills[skill_id]['skill_name']}")
            print("💡 You can add custom challenges!")
            return
        
        # Show challenges
        print(f"\n📋 Challenges for {skills[skill_id]['skill_name']}:")
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
                skill_id=skills[skill_id]['id'],
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

        # New Roadmap methods
    
    def _add_skill_with_roadmap(self):
        """Add new skill with AI-generated learning roadmap"""
        
        print("\n" + "="*60)
        print("🎓 Create New Skill with Learning Roadmap")
        print("="*60)
        
        # Basic skill info
        skill_name = input("\nSkill name (e.g., 'Python Programming'): ").strip()
        if not skill_name:
            print("❌ Skill name required")
            return
        
        category = input("Category (e.g., 'programming', 'language', 'business'): ").strip()
        
        print("\nYour current level:")
        print("  1. Beginner (just starting)")
        print("  2. Intermediate (some experience)")
        print("  3. Advanced (quite experienced)")
        
        level_choice = input("Choice (1-3): ").strip()
        level_map = {'1': 'beginner', '2': 'intermediate', '3': 'advanced'}
        difficulty = level_map.get(level_choice, 'beginner')
        
        # AI roadmap generation
        print("\n" + "="*60)
        print("🤖 AI-Powered Learning Roadmap Generator")
        print("="*60)
        
        print("\nI'll ask a few questions to create a personalized roadmap:")
        print("  • What you already know")
        print("  • Where you want to go")
        print("  • What challenges to build")
        print()
        
        proceed = input("Ready? (y/n): ").strip().lower()
        if proceed != 'y':
            print("\nCancelled. Use basic 'Add skill' for manual setup.")
            return
        
        # Interview questions
        print("\n" + "-"*60)
        print("📊 CURRENT LEVEL ASSESSMENT")
        print("-"*60)
        
        current_level = input(f"\nWhat do you already know about {skill_name}?\n(Be specific - tools, concepts, libraries, experience)\n\n> ").strip()
        
        comfortable = input(f"\nWhat are you COMFORTABLE with?\n(Things you can do without looking up)\n\n> ").strip()
        
        uncomfortable = input(f"\nWhat do you want to learn or struggle with?\n(Things you haven't tried or find difficult)\n\n> ").strip()
        
        print("\n" + "-"*60)
        print("🎯 GOALS & OBJECTIVES")
        print("-"*60)
        
        goals = input(f"\nWhy do you want to learn {skill_name}?\nWhat do you want to build or achieve?\n\n> ").strip()
        
        domains = input(f"\nSpecific areas or technologies?\n(e.g., 'web development', 'machine learning', 'financial analysis')\n\n> ").strip()
        
        timeline = input(f"\nTimeline or deadline?\n(e.g., '3 months', '6 months', 'no rush')\n\n> ").strip()
        
        # Generate roadmap with Claude
        print("\n" + "="*60)
        print("🤔 Analyzing and generating your learning roadmap...")
        print("="*60)
        
        roadmap_prompt = f"""You are an expert learning path designer. A user wants to learn: {skill_name}

CURRENT LEVEL ASSESSMENT:
- What they know: {current_level}
- Comfortable with: {comfortable}
- Want to learn/struggle with: {uncomfortable}
- Self-assessed level: {difficulty}

GOALS & MOTIVATION:
- Why they want to learn: {goals}
- Specific focus areas: {domains}
- Timeline: {timeline}

YOUR TASK:
Create a personalized, practical learning roadmap with specific buildable challenges.

GUIDELINES:
1. Start from their current level (don't teach what they already know)
2. Focus on their weak areas: {uncomfortable}
3. Align with their goals: {goals}
4. Make challenges PRACTICAL (build real things, not just study)
5. Create 6-12 challenges organized in 3-4 progressive phases
6. Each challenge should take 3-15 hours

FORMAT:
For each challenge, use EXACTLY this format:

CHALLENGE: [Concise, actionable title]
DIFFICULTY: [beginner/intermediate/advanced]
HOURS: [estimated hours as a number]
DESCRIPTION: [2-3 sentences: what they'll build and what they'll learn]
SKILLS: [comma-separated list of skills taught]
PREREQUISITES: [comma-separated list of prerequisites, or "none"]

Example:
CHALLENGE: Build a CLI Task Manager
DIFFICULTY: intermediate
HOURS: 6
DESCRIPTION: Create a command-line task management app with file persistence. Learn file I/O, data structures, and CLI design patterns. Users can add, list, complete, and delete tasks.
SKILLS: file I/O, JSON handling, CLI design, data persistence
PREREQUISITES: basic Python, functions, dictionaries

Now create the roadmap:"""
        
        try:
            # Generate with Claude
            roadmap_response = self.claude.chat(roadmap_prompt, include_memories=False)
            
            print("\n" + "="*60)
            print("📋 YOUR PERSONALIZED LEARNING ROADMAP")
            print("="*60)
            print()
            print(roadmap_response)
            print()
            print("="*60)
            
            # Ask to proceed
            proceed = input("\n💾 Create skill and add these challenges? (y/n): ").strip().lower()
            
            if proceed != 'y':
                print("Cancelled. Roadmap not saved.")
                return
            
            # Create skill
            skill_id = self.learning.add_skill(skill_name, category, difficulty)
            
            # Save context
            cursor = self.learning.conn.cursor()
            cursor.execute("""
                UPDATE learning_skills
                SET current_level = ?,
                    goals = ?,
                    timeline = ?,
                    roadmap_generated = 1
                WHERE id = ?
            """, (
                f"Knows: {current_level}\nComfortable: {comfortable}\nWants to learn: {uncomfortable}",
                f"Goals: {goals}\nFocus areas: {domains}",
                timeline,
                skill_id
            ))
            self.learning.conn.commit()
            
            # Parse and create challenges
            print("\n🔄 Parsing and creating challenges...")
            
            challenges_created = self._parse_and_create_challenges(roadmap_response, skill_id)
            
            print(f"\n✅ Skill created: {skill_name}")
            print(f"✅ Added {challenges_created} challenges")
            print(f"✅ Learning roadmap saved")
            
            # Show first recommendation
            print("\n" + "-"*60)
            recommendation = self.learning.get_recommended_challenge(skill_id)
            
            if recommendation:
                print(f"\n🎯 Your first recommended challenge:")
                print(f"   {recommendation['challenge']['title']}")
                print()
                
                start = input("Start this challenge now? (y/n): ").strip().lower()
                
                if start == 'y':
                    self.learning.start_challenge(recommendation['challenge']['id'])
                    print("\n✅ Challenge started!")
                    print("💡 Use 'build' → 'Continue challenge' to work on it")
            
        except Exception as e:
            print(f"\n❌ Error generating roadmap: {e}")
            print("You can still add the skill and challenges manually.")
    
    def _generate_roadmap_for_existing_skill(self, skill_id: int, skill_name: str):
        """Generate AI roadmap for an existing skill (preserves existing challenges)"""
        
        print("\n" + "="*60)
        print(f"🤖 Generate Learning Roadmap: {skill_name}")
        print("="*60)
        
        print("\nI'll create a personalized learning roadmap for this skill.")
        print("✅ Your existing challenges and progress will be PRESERVED.")
        print("✅ New challenges will be ADDED alongside existing ones.")
        print()
        
        proceed = input("Continue? (y/n): ").strip().lower()
        if proceed != 'y':
            return
        
        # Show existing challenges
        existing_challenges = self.learning.get_all_challenges(skill_id=skill_id)
        existing_titles = [c['title'] for c in existing_challenges]
        
        if existing_titles:
            print(f"\n📋 You already have {len(existing_titles)} challenge(s):")
            for i, title in enumerate(existing_titles[:5], 1):
                print(f"  {i}. {title}")
            if len(existing_titles) > 5:
                print(f"  ... and {len(existing_titles) - 5} more")
            print()
        
        # Interview
        print("-"*60)
        print("📊 CURRENT LEVEL ASSESSMENT")
        print("-"*60)
        
        current_level = input(f"\nWhat do you already know about {skill_name}?\n(Be specific)\n\n> ").strip()
        
        comfortable = input(f"\nWhat are you COMFORTABLE with?\n\n> ").strip()
        
        uncomfortable = input(f"\nWhat do you want to learn or struggle with?\n\n> ").strip()
        
        print("\n" + "-"*60)
        print("🎯 GOALS & OBJECTIVES")
        print("-"*60)
        
        goals = input(f"\nWhy do you want to master {skill_name}?\n\n> ").strip()
        
        domains = input(f"\nSpecific areas or technologies?\n\n> ").strip()
        
        timeline = input(f"\nTimeline?\n\n> ").strip()
        
        # Generate roadmap
        print("\n🤔 Generating personalized roadmap...")
        
        existing_challenges_text = "\n".join([f"- {title}" for title in existing_titles]) if existing_titles else "None yet"
        
        roadmap_prompt = f"""You are a learning path designer. A user wants to improve: {skill_name}

EXISTING CHALLENGES (already created - DO NOT DUPLICATE):
{existing_challenges_text}

CURRENT LEVEL:
- What they know: {current_level}
- Comfortable with: {comfortable}
- Want to improve: {uncomfortable}

GOALS:
- Why they want to learn: {goals}
- Focus areas: {domains}
- Timeline: {timeline}

YOUR TASK:
Create NEW challenges that:
1. Do NOT duplicate existing challenges
2. Fill gaps in their knowledge (focus on: {uncomfortable})
3. Align with their goals ({domains})
4. Progress from their current level toward mastery

Provide 5-10 new practical challenges.

FORMAT (use EXACTLY this format):

CHALLENGE: [Title]
DIFFICULTY: [beginner/intermediate/advanced]
HOURS: [number]
DESCRIPTION: [What they'll build and learn, 2-3 sentences]
SKILLS: [skill1, skill2, skill3]
PREREQUISITES: [prereq1, prereq2] (or "none")"""
        
        try:
            roadmap_response = self.claude.chat(roadmap_prompt, include_memories=False)
            
            print("\n" + "="*60)
            print("📋 NEW CHALLENGES FOR YOUR ROADMAP")
            print("="*60)
            print()
            print(roadmap_response)
            print()
            print("="*60)
            
            save = input("\n💾 Add these challenges to your skill? (y/n): ").strip().lower()
            
            if save != 'y':
                print("Cancelled.")
                return
            
            # Update skill with roadmap context
            cursor = self.learning.conn.cursor()
            cursor.execute("""
                UPDATE learning_skills
                SET current_level = ?,
                    goals = ?,
                    timeline = ?,
                    roadmap_generated = 1
                WHERE id = ?
            """, (
                f"Knows: {current_level}\nComfortable: {comfortable}\nWants to learn: {uncomfortable}",
                f"Goals: {goals}\nFocus areas: {domains}",
                timeline,
                skill_id
            ))
            self.learning.conn.commit()
            
            # Parse and create new challenges
            print("\n🔄 Creating new challenges...")
            
            new_challenges = self._parse_and_create_challenges(roadmap_response, skill_id)
            
            print(f"\n✅ Added {new_challenges} new challenges")
            print(f"✅ Preserved {len(existing_challenges)} existing challenges")
            print(f"✅ Total challenges: {len(existing_challenges) + new_challenges}")
            print(f"✅ Roadmap context saved")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    def _parse_and_create_challenges(self, roadmap_text: str, skill_id: int) -> int:
        """Parse Claude's roadmap response and create challenges in database"""
        import re
        
        challenges_created = 0
        
        print("\n🔄 Parsing challenges...")
        
        # Split by CHALLENGE: marker
        # Handle both "CHALLENGE:" and "**CHALLENGE:**" formats
        challenge_blocks = re.split(r'(?:^|\n)\**CHALLENGE:\s*', roadmap_text, flags=re.MULTILINE)
        
        if len(challenge_blocks) <= 1:
            print("⚠️  No CHALLENGE: markers found")
            return 0
        
        print(f"   Found {len(challenge_blocks)-1} challenge(s)")
        
        for block in challenge_blocks[1:]:  # Skip first split (text before first CHALLENGE)
            try:
                # Clean markdown formatting helper
                def clean_text(text):
                    if not text:
                        return ""
                    # Remove all asterisks (bold/italic markdown)
                    text = re.sub(r'\*+', '', text)
                    # Collapse whitespace
                    text = ' '.join(text.split())
                    return text.strip()
                
                # Extract title (first line)
                title_match = re.search(r'^(.+?)(?:\n|$)', block)
                if not title_match:
                    continue
                
                title = clean_text(title_match.group(1))
                if not title or len(title) < 3:
                    continue
                
                # Extract difficulty (case insensitive, handles **bold** format)
                difficulty_match = re.search(r'DIFFICULTY:\s*(.+?)(?:\n|$)', block, re.IGNORECASE)
                if difficulty_match:
                    difficulty = clean_text(difficulty_match.group(1)).lower()
                    if difficulty not in ['beginner', 'intermediate', 'advanced']:
                        difficulty = 'intermediate'
                else:
                    difficulty = 'intermediate'
                
                # Extract hours
                hours_match = re.search(r'HOURS?:\s*(\d+)', block, re.IGNORECASE)
                hours = int(hours_match.group(1)) if hours_match else 5
                
                # Extract description
                description_match = re.search(
                    r'DESCRIPTION:\s*(.+?)(?:\n\s*(?:SKILLS?:|PREREQUISITES?:|CHALLENGE:|$))',
                    block,
                    re.DOTALL | re.IGNORECASE
                )
                if description_match:
                    description = clean_text(description_match.group(1))
                else:
                    description = title
                
                # Limit description length
                if len(description) > 500:
                    description = description[:497] + "..."
                
                # Extract skills
                skills_match = re.search(
                    r'SKILLS?:\s*(.+?)(?:\n\s*(?:PREREQUISITES?:|CHALLENGE:|$))',
                    block,
                    re.IGNORECASE
                )
                if skills_match:
                    skills_text = clean_text(skills_match.group(1))
                    skills_taught = [s.strip() for s in skills_text.split(',') if s.strip()]
                else:
                    skills_taught = []
                
                if not skills_taught:
                    skills_taught = [title]
                
                # Extract prerequisites
                prereqs_match = re.search(
                    r'PREREQUISITES?:\s*(.+?)(?:\n\s*(?:CHALLENGE:|$))',
                    block,
                    re.IGNORECASE
                )
                if prereqs_match:
                    prereqs_text = clean_text(prereqs_match.group(1))
                    if 'none' in prereqs_text.lower():
                        prerequisites = []
                    else:
                        prerequisites = [p.strip() for p in prereqs_text.split(',') if p.strip()]
                else:
                    prerequisites = []
                
                # Create challenge in database
                self.learning.add_challenge(
                    title=title,
                    description=description,
                    skill_id=skill_id,
                    difficulty=difficulty,
                    estimated_hours=hours,
                    skills_taught=skills_taught,
                    prerequisites=prerequisites,
                    unlocks=[]
                )
                
                challenges_created += 1
                print(f"  ✅ {title}")
            
            except Exception as e:
                print(f"  ⚠️  Skipped one challenge (error: {str(e)[:50]})")
                continue
        
        if challenges_created == 0:
            print("\n⚠️  Could not create any challenges")
            print("   You can add challenges manually using 'Start new challenge'")
        
        return challenges_created
    
    def _get_recommendation(self):
        """Get smart recommendation for next challenge"""
        
        # Get user's skills
        skills = self.learning.get_all_skills()
        
        if not skills:
            print("\n⚠️  No skills found. Add a skill first with 'learn' command.")
            return
        
        # Show skills
        print("\n" + "="*60)
        print("🎯 Smart Challenge Recommendation")
        print("="*60)
        
        print("\nYour skills:")
        for idx, skill in enumerate(skills, 1):
            progression = self.learning.get_skill_progression(skill['id'])
            print(f"  {idx}. {skill['skill_name']} - {progression['competency_level']} ({progression['completed'] or 0} completed)")
        
        # Select skill
        try:
            choice = input("\nGet recommendation for which skill? (number or 0 to cancel): ").strip()
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
        
        # Get recommendation
        print(f"\n🤔 Analyzing your progress in {selected_skill['skill_name']}...")
        
        recommendation = self.learning.get_recommended_challenge(selected_skill['id'])
        
        if not recommendation:
            print(f"\n⚠️  No recommendations available")
            print("\n💡 This might mean:")
            print("  • All challenges completed! 🎉")
            print("  • No challenges created yet")
            print("  • Prerequisites not met for remaining challenges")
            return
        
        challenge = recommendation['challenge']
        
        # Display recommendation
        print("\n" + "="*60)
        print("🎯 RECOMMENDED CHALLENGE")
        print("="*60)
        
        print(f"\n📝 {challenge['title']}")
        print(f"⏱️  Estimated time: {challenge['estimated_hours']} hours")
        print(f"📊 Difficulty: {challenge['difficulty'].title()}")
        
        print(f"\n💡 Why this challenge now:")
        print(recommendation['reason'])
        
        print(f"\n📚 {recommendation['skill_gap']}")
        
        if recommendation['unlocks']:
            print(f"\n🔓 Unlocks:")
            for unlock in recommendation['unlocks']:
                print(f"  • {unlock}")
        
        print(f"\n📖 Description:")
        print(challenge['description'])
        
        # Offer to start
        print("\n" + "-"*60)
        start = input("\n🚀 Start this challenge now? (y/n): ").strip().lower()
        
        if start == 'y':
            self.learning.start_challenge(challenge['id'])
            print(f"\n✅ Challenge started!")
            print(f"💡 Use 'build' → 'Continue challenge' to work on it")
        else:
            print("\n💭 No problem! The recommendation will be here when you're ready.")

    def _view_learning_path(self):
        """View recommended learning path for a skill"""
        
        # Get user's skills
        skills = self.learning.get_all_skills()
        
        if not skills:
            print("\n⚠️  No skills found. Add a skill first with 'learn' command.")
            return
        
        # Show skills
        print("\n" + "="*60)
        print("🗺️  Learning Path Visualization")
        print("="*60)
        
        print("\nYour skills:")
        for idx, skill in enumerate(skills, 1):
            progression = self.learning.get_skill_progression(skill['id'])
            print(f"  {idx}. {skill['skill_name']} - {progression['competency_level']}")
        
        # Select skill
        try:
            choice = input("\nView path for which skill? (number or 0 to cancel): ").strip()
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
        
        # Get learning path
        path = self.learning.get_learning_path(selected_skill['id'])
        
        if not path:
            print(f"\n⚠️  No learning path available for {selected_skill['skill_name']}")
            print("💡 Add challenges first using 'Start new challenge' or generate a roadmap")
            return
        
        # Display path
        print("\n" + "="*60)
        print(f"🗺️  {selected_skill['skill_name']} Learning Path")
        print("="*60)
        
        for idx, step in enumerate(path):
            challenge = step['challenge']
            display = step['display']
            status = step['status']
            
            print(f"\n{display} {challenge['title']}")
            print(f"   Difficulty: {challenge['difficulty'].title()} | Est: {challenge['estimated_hours']}h")
            
            if status == 'completed':
                print(f"   Status: Completed ✅")
                if challenge['completed_at']:
                    print(f"   Completed: {challenge['completed_at'][:10]}")
            
            elif status == 'in_progress':
                print(f"   Status: In Progress ({challenge['progress_percent']}%)")
                print(f"   Time spent: {challenge['time_spent'] // 60}h {challenge['time_spent'] % 60}m")
            
            elif status == 'recommended':
                print(f"   Status: RECOMMENDED 🎯")
                if 'reason' in step:
                    print(f"\n   Why now:")
                    for line in step['reason'].split('\n'):
                        print(f"   {line}")
            
            elif status == 'future':
                print(f"   Status: Future (locked)")
                if 'note' in step:
                    print(f"   {step['note']}")
            
            # Show arrow to next (except last)
            if idx < len(path) - 1:
                print("       ↓")
        
        print("\n" + "="*60)
        print("\nLegend:")
        print("  ✅ Completed")
        print("  ⚙️  In Progress")
        print("  🎯 Recommended Next")
        print("  🔒 Future (locked)")
        
        # If there's a recommendation, offer to start
        recommended = [s for s in path if s['status'] == 'recommended']
        if recommended:
            print("\n" + "-"*60)
            start = input("\n🚀 Start the recommended challenge? (y/n): ").strip().lower()
            
            if start == 'y':
                rec_challenge = recommended[0]['challenge']
                self.learning.start_challenge(rec_challenge['id'])
                print(f"\n✅ Challenge started!")
                print(f"💡 Use 'build' → 'Continue challenge' to work on it")


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
