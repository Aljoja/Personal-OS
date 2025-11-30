# Personal OS 🧠

Your AI-powered learning and productivity system with persistent memory, project-based learning, and personalized assistance.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key:
# ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Run
```bash
python main.py
```

---

## ✨ Core Features

### 🧠 **Persistent Memory System**
- Remembers facts, preferences, and conversations
- Semantic search across all your knowledge
- Automatic memory from natural conversation
- Goal tracking and progress monitoring

### 🏗️ **Challenge-Based Learning Lab** (NEW!)
- Project-driven skill development
- Learn by building, not just studying
- Obstacle logging and solution tracking
- Skill progression based on completed projects
- Daily building streaks for consistency
- Predefined challenges in Python, ML, Data Analysis, IoT

### 📚 **Explanation Library**
- Request AI-generated explanations on any topic
- Save explanations as Markdown files
- Organize by skill
- Browse and revisit saved explanations
- Custom guidance for explanation style

### 📖 **Traditional Learning Tracker**
- Time-based session logging
- Q&A spaced repetition system
- Review scheduling
- Progress statistics
- Milestone tracking

### 📁 **File Intelligence**
- Auto-index files dropped in watched folder
- Semantic file search
- Automatic summarization
- Conversation search across past chats

### ✍️ **Writing Assistant**
- Save your writing style
- Apply style to any text
- Consistent voice across all writing

### 🤖 **Automation**
- File watcher (auto-index)
- Morning routine briefings
- Scheduled learning reviews

---

## 🎯 Main Commands

### Natural Conversation
Just chat naturally - it learns about you automatically:
```
You: Remember that I'm working on a factory optimization project
You: I'm interested in Madrid for its tech scene
You: What did I tell you about Madrid?
```

### Core Commands
```
chat        - Natural conversation (default)
build       - Challenge-based learning lab 🏗️
learn       - Traditional learning tracker 🎓
explain     - Get & save explanations 📖
goals       - Manage your goals
recall      - Search your memories
remember    - Save facts manually
style       - Set writing style
edit        - Apply style to text
files       - Search indexed files
```

---

## 🏗️ Challenge-Based Learning (Your Primary Tool)

### Getting Started
```bash
python main.py
> build
```

### Options:
1. **Start new challenge** - Browse library, pick a project
2. **Continue challenge** - Work on in-progress projects
3. **Log obstacle** - Track what's blocking you
4. **View skill progression** - See your competency growth
5. **Search past obstacles** - Find solutions you've discovered
6. **View all challenges** - Overview of your pipeline

### Example Workflow
```bash
# Start a challenge
> build
Choice: 1  # Start new challenge
Skill: Python Programming
Challenge: CLI Todo App
Start? y

# Work on it, hit an obstacle
[You code for 30 minutes...]
[You get stuck on file I/O]

# Log the obstacle
> build
Choice: 3  # Log obstacle
Obstacle: Don't know how to save dictionary to file

# Solve it (after learning/searching)
> build
Choice: 2  # Continue challenge
Choice: 3  # Solve obstacle
Solution: Use json.dump() to serialize dictionary
Insight: JSON is perfect for Python data structures

# Update progress
Choice: 1  # Update progress
Progress: 60%
Minutes worked: 90

# Complete the challenge
Choice: 4  # Complete challenge
GitHub: https://github.com/yourname/todo-app
Notes: Learned file I/O, list manipulation, CLI design

✅ Challenge completed!
🏆 Skill progression updated!
```

### Your Progress
```bash
> build
Choice: 4  # View skill progression

📊 Your Skill Progression

Python Programming: BEGINNER+
  [███████░░░] 70%
  Projects completed: 2
  In progress: 1
  Obstacles overcome: 5
  Total time: 8h

Machine Learning: JUST_STARTING
  [██░░░░░░░░] 20%
  Projects completed: 0
  In progress: 1
  Obstacles overcome: 2
  Total time: 3h
```

### Predefined Challenges

**Python (4 challenges):**
- CLI Todo App (beginner, 3h)
- Web Scraper with Error Handling (beginner, 4h)
- Data Validator with Decorators (intermediate, 4h)
- Simple REST API (intermediate, 5h)

**Data Analysis (3 challenges):**
- Kaggle Dataset Analysis (beginner, 5h)
- Automated Report Generator (intermediate, 6h)
- Time Series Analysis (intermediate, 6h)

**Machine Learning (3 challenges):**
- Linear Regression from Scratch (beginner, 6h)
- Neural Network from Scratch (advanced, 10h)
- Housing Price Predictor (intermediate, 8h)

**Digitalization (2 challenges):**
- IoT Data Pipeline (intermediate, 8h)
- Manufacturing Dashboard (advanced, 10h)

**Add your own challenges or use the library!**

---

## 📖 Explanation System

### Request Explanations
```bash
> explain

📖 Explanation Assistant

Your skills:
  1. Python Programming
  2. Machine Learning

Which skill? 1
Topic: list comprehensions

Customization (optional):
Examples:
  • 'Focus on practical examples'
  • 'Keep it brief and simple'

Your guidance: focus on examples

[Claude generates explanation]

Save? y
✅ Saved to: explanations/1_Python_Programming/list_comprehensions.md
```

### Browse Saved Explanations
```bash
> explain
Choice: 2  # Browse

📚 Your Saved Explanations

Python Programming (3 explanations):
  1. List Comprehensions
  2. Decorators
  3. Lambda Functions

Select: 1
[Shows explanation]
```

---

## 🎓 Traditional Learning Tracker

For time-based study sessions (courses, reading, theory):
```bash
> learn

📚 Learning Tracker

1. Add new skill
2. Log learning session
3. Add Q&A for review
4. Review items
5. View statistics
6. Set milestone
7. View skill details
```

### Example: Log Study Session
```bash
Choice: 2  # Log session
Skill: Machine Learning
Duration: 90 minutes
Topics: Gradient descent, backpropagation
Notes: Watched Andrew Ng lecture, took notes

✅ Session logged!
```

---

## 🤖 Automation Services

### File Watcher
Auto-indexes files dropped in `files/watched/`:
```bash
python -m automation.file_watcher
```

Drop a PDF, document, or code file → automatically summarized and searchable!

### Morning Routine
Daily briefing with goals and reminders:
```bash
python -m automation.morning_routine
```

Runs at 8 AM daily (configurable).

---

## 📂 File Structure
```
personal-os/
├── brain/                      # Core intelligence
│   ├── knowledge.db           # SQLite database (memory, learning, challenges)
│   ├── embeddings/            # Vector database (semantic search)
│   ├── memory.py              # Memory system
│   ├── learning_tracker.py   # Learning & challenge system
│   ├── challenge_library.py  # Predefined challenges
│   ├── explanations.py        # Explanation management
│   └── claude_client.py       # AI interface
│
├── files/
│   └── watched/               # Auto-indexed files
│
├── automation/
│   ├── file_watcher.py        # File auto-indexing
│   └── morning_routine.py     # Daily briefings
│
├── conversations/             # Saved chat history (.txt)
├── explanations/              # Saved explanations (.md)
│   ├── 1_Python_Programming/
│   │   ├── list_comprehensions.md
│   │   └── decorators.md
│   └── 2_Machine_Learning/
│       └── gradient_descent.md
│
└── main.py                    # Main entry point
```

---

## 🎯 Learning Philosophy

### Why Challenge-Based Learning?

**Traditional approach (doesn't work for everyone):**
```
Study theory → Take notes → Forget
```

**Challenge-based approach (learn by doing):**
```
Build project → Hit obstacle → Learn what you need → Apply immediately → Remember forever
```

**This system supports YOUR learning style:**
- ✅ Learn by building real projects
- ✅ Track obstacles (where real learning happens)
- ✅ Prove competency through completed work
- ✅ Build portfolio while learning
- ✅ Maintain consistency with streaks

---

## 📊 Database Schema

### Core Tables

**Memory System:**
- `facts` - Knowledge about you
- `conversations` - Chat history
- `goals` - Your objectives
- `preferences` - Writing style, settings
- `files` - Indexed documents

**Learning System:**
- `learning_skills` - Skills you're developing
- `learning_sessions` - Time-based study logs
- `learning_items` - Q&A for spaced repetition
- `review_history` - Review performance

**Challenge System:**
- `learning_challenges` - Projects to build
- `challenge_obstacles` - Problems & solutions
- `daily_streaks` - Consistency tracking
- `skill_evidence` - Proof of competency

---

## 🔧 Configuration

### Environment Variables (.env)
```bash
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-sonnet-4-20250514
```

### Customization

**Add your own challenges:**
Edit `brain/challenge_library.py` and add to the appropriate category.

**Adjust streak requirements:**
Edit `learning_tracker.py` → `log_daily_streak()` method.

**Change explanation format:**
Edit `claude_client.py` → `generate_explanation()` method.

---

## 💡 Tips for Success

### For Learning
1. **Start with one skill** - Don't spread too thin
2. **Pick beginner challenges first** - Build confidence
3. **Log obstacles immediately** - Capture learning moments
4. **Review past obstacles** - Build your personal Stack Overflow
5. **Complete challenges** - Finish what you start
6. **Maintain streak** - Consistency > intensity

### For Memory
1. **Chat naturally** - It learns automatically
2. **Use "remember that..."** - For important facts
3. **Search before asking** - Use `recall` command
4. **Review goals weekly** - Stay aligned

### For Explanations
1. **Save explanations as you learn** - Build knowledge base
2. **Use custom guidance** - "Focus on examples", "Keep brief"
3. **Browse before requesting** - Might already have it
4. **Review explanations before challenges** - Refresh knowledge

---

## 🚀 Getting Started Checklist

- [ ] Install dependencies
- [ ] Add API key to .env
- [ ] Run `python main.py`
- [ ] Add your first skill: `> learn` → Add new skill
- [ ] Start your first challenge: `> build` → Start new challenge
- [ ] Complete one challenge this week
- [ ] Save 3-5 explanations for concepts you're learning
- [ ] Build a 3-day streak
- [ ] Review your skill progression: `> build` → View progression

---

## 🐛 Troubleshooting

### "No such table" error
```bash
# Delete and recreate database
rm brain/knowledge.db
python main.py  # Tables will be created automatically
```

### "FOREIGN KEY constraint failed"
Check that `PRAGMA foreign_keys = ON` is set in `learning_tracker.py`.

### Explanations not saving
Check that `explanations/` directory exists and is writable.

### Streaks not tracking
Ensure you're calling `log_daily_streak()` when updating challenge progress.

---

## 🎯 Next Steps

1. **Start your first challenge today**
2. **Use the system for 2-3 weeks**
3. **Note what you use vs. don't use**
4. **Customize based on your patterns**

---

## 📚 Learn More

- [Anthropic Claude API Docs](https://docs.anthropic.com)
- [Spaced Repetition](https://en.wikipedia.org/wiki/Spaced_repetition)
- [Project-Based Learning](https://en.wikipedia.org/wiki/Project-based_learning)

---

## 🤝 Contributing

This is a personal tool, but feel free to:
- Fork and customize for your needs
- Share your challenge library additions
- Report bugs or suggest improvements

---

## 📝 License

Personal use. Modify as you wish!

---

**Now stop reading and start building something! 🚀**

Your first challenge awaits in `> build` → Start new challenge