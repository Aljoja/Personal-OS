# Personal OS 🧠

Your AI-powered learning and productivity system with persistent memory, AI-generated roadmaps, project-based learning, and personalized assistance.

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

## ✨ Core Features Overview

### 🧠 **Persistent Memory System**
Claude remembers your conversations, facts, preferences, and goals across sessions.

### 🤖 **AI-Powered Skill Roadmaps** (NEW!)
Get personalized learning paths with challenges tailored to your level, goals, and timeline.

### 🏗️ **Challenge-Based Learning Lab**
Learn by building real projects, not just studying theory. Track obstacles and prove competency.

### 📚 **Explanation Library**
Request and save AI-generated explanations organized by skill for future reference.

### 📖 **Traditional Learning Tracker**
Time-based session logging, spaced repetition Q&A, and milestone tracking.

### 📁 **File Intelligence**
Auto-index and search through your documents with semantic search.

### ✍️ **Writing Assistant**
Save your writing style and apply it to any text for consistency.

### 🤖 **Automation**
File watching, morning briefings, and scheduled learning reviews.

---

## 🎯 Command Reference
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

## 🤖 AI-Powered Skill Roadmaps

### What It Does

Creates a **personalized learning path** based on:
- Your current knowledge level
- What you're comfortable with
- What you want to learn
- Your goals and motivation
- Your timeline

**The AI generates 6-12 practical challenges** organized in progressive phases, each designed to build real skills through hands-on projects.

---

### Creating a New Skill with Roadmap
```bash
> learn
Choice: 3  # Add skill with AI roadmap 🤖

Skill name: Machine Learning
Category: AI
Current level: 2 (Intermediate)

Ready? y
```

**AI Interview:**
```
📊 CURRENT LEVEL ASSESSMENT

What do you already know about Machine Learning?
> I completed Andrew Ng's course. Know scikit-learn, supervised learning,
> regression, classification. But rusty - haven't used it much recently.

What are you COMFORTABLE with?
> Statistical analysis, basic model training, using scikit-learn

What do you want to learn or struggle with?
> Building from scratch, deep learning, neural networks, deploying models

🎯 GOALS & OBJECTIVES

Why do you want to learn Machine Learning?
> Want to build ML tools for factory optimization, uncover insights from data,
> and eventually move into deep learning and AI

Specific areas?
> Manufacturing optimization, financial analysis, engineering applications

Timeline?
> 3 months
```

**What You Get:**
```
🔄 Parsing challenges...
   Found 11 challenge(s)
  ✅ Regression Model End-to-End Pipeline
  ✅ Classification Battle: Compare 5 Algorithms
  ✅ Build Your ML Math Foundation
  ✅ Financial Portfolio Risk Analyzer
  ✅ Predictive Maintenance System for Engineering
  ✅ Automated Hyperparameter Optimization Framework
  ✅ Feature Engineering Innovation Lab
  ✅ Ensemble Methods Masterclass
  ✅ Unsupervised Learning for Innovation Discovery
  ✅ Neural Network from Scratch
  ✅ End-to-End ML Product: Innovation Opportunity Detector

✅ Skill created: Machine Learning
✅ Added 11 challenges
✅ Learning roadmap saved

🎯 Your first recommended challenge:
   Regression Model End-to-End Pipeline

Start this challenge now? (y/n):
```

**Each challenge includes:**
- Clear title describing what you'll build
- Difficulty level (beginner/intermediate/advanced)
- Estimated hours
- Detailed description
- Skills you'll learn
- Prerequisites needed

---

### Adding Roadmap to Existing Skills

Already have a skill? Generate a roadmap for it:
```bash
> learn
Choice: 8  # View skill details
Skill ID: 1  # Python coding

⚠️ AI Learning Roadmap: Not generated
   💡 Generate a personalized roadmap with challenge recommendations

Options:
  1. Generate AI roadmap for this skill 🤖
  2. View challenges for this skill

Choice: 1
```

**The AI will:**
- See your existing challenges (won't duplicate)
- Ask about your current level and goals
- Generate NEW challenges that fill gaps
- Preserve all your existing progress
```
📋 You already have 2 challenge(s):
  1. CLI Todo App
  2. Web Scraper

[Goes through interview]

✅ Added 8 new challenges
✅ Preserved 2 existing challenges
✅ Total challenges: 10
```

---

### Viewing Roadmap Context

See the context that drives your recommendations:
```bash
> learn
Choice: 8  # View skill details
Skill ID: 5  # Machine Learning

Choice: 1  # View full roadmap context
```
```
📋 Learning Roadmap: Machine Learning

📊 Level Assessment:
Knows: Completed ML course, know scikit-learn, supervised learning
Comfortable: Statistical analysis, basic model training
Wants to learn: Building from scratch, deep learning, deployment

🎯 Goals & Focus:
Goals: Build ML tools for factory optimization, gain insights from data
Focus areas: Manufacturing, financial analysis, engineering

⏱️ Timeline: 3 months
```

---

## 🏗️ Challenge-Based Learning Lab

### Philosophy

**Traditional Learning:**
```
Study theory → Take notes → Try to remember → Forget ❌
```

**Challenge-Based Learning:**
```
Build project → Hit obstacle → Learn what's needed → Apply immediately → Remember forever ✅
```

**You learn by DOING, not just reading.**

---

### Main Menu
```bash
> build

Options:
  1. Start new challenge
  2. Continue challenge
  3. Log obstacle
  4. View skill progression
  5. Get recommendation 🎯
  6. View learning path 🗺️
  7. Search past obstacles
  8. View all challenges
```

---

### 1. Start New Challenge

Two ways to add challenges:

**Option A: Create Custom Challenge**
```bash
> build
Choice: 1

Skill: Python Programming

Challenge title: Build a Pomodoro Timer CLI
Description: CLI app with 25min work/5min break cycles, notifications
Difficulty: beginner
Hours: 3
Skills: time handling, CLI, notifications
Prerequisites: functions, loops

✅ Challenge created!
Start now? y
```

**Option B: Use AI-Generated Challenges**

When you create a skill with AI roadmap, challenges are automatically added. Just pick one:
```bash
> build
Choice: 1

Skill: Machine Learning

Available challenges:
  1. Regression Model Pipeline (intermediate, 8h)
  2. Classification Battle (intermediate, 10h)
  3. Build ML Math Foundation (intermediate, 12h)

Which challenge? 1
Start? y
```

---

### 2. Continue Challenge

Work on in-progress projects:
```bash
> build
Choice: 2

In Progress (1):
  1. Regression Model Pipeline - 30% (2h spent)
     🚧 1 obstacle blocking

Which challenge? 1

Options:
  1. Update progress
  2. Log obstacle
  3. Solve obstacle
  4. Complete challenge

Choice: 1  # Update progress
Progress %: 50
Minutes worked today: 90

✅ Progress updated!
🔥 Daily streak: 3 days
```

---

### 3. Log Obstacle

**This is where real learning happens!**
```bash
> build
Choice: 3

Challenge: Regression Model Pipeline
Obstacle: Getting NaN values in predictions, don't understand why

✅ Obstacle logged!
```

**Later, when you solve it:**
```bash
> build
Choice: 2  # Continue challenge
Challenge: Regression Model Pipeline
Choice: 3  # Solve obstacle

Solution: Missing values in training data. Used SimpleImputer with mean strategy
Insight: Always check for NaN before training. pd.isna().sum() is your friend
Time to solve: 45 minutes
Resources: scikit-learn docs, Stack Overflow

✅ Obstacle solved! 🎉
```

**Why this matters:**
- Builds your personal "Stack Overflow"
- Prevents forgetting solutions
- Tracks problem-solving skills
- Searchable later

---

### 4. View Skill Progression

See evidence-based competency, not just time spent:
```bash
> build
Choice: 4

📊 Your Skill Progression

Machine Learning: INTERMEDIATE
  [███████░░░] 70%
  Projects completed: 5
  In progress: 2
  Obstacles overcome: 12
  Total time: 38h

Python Programming: BEGINNER+
  [█████░░░░░] 50%
  Projects completed: 2
  In progress: 1
  Obstacles overcome: 7
  Total time: 14h
```

**Progression Algorithm:**
- 10+ completed = Advanced (90%)
- 5-9 completed = Intermediate (70%)
- 2-4 completed = Beginner+ (50%)
- 1 completed = Beginner (30%)
- 0 completed = Just Starting (10%)

**Based on actual projects built, not just hours logged.**

---

### 5. Get Recommendation 🎯 (NEW!)

**Let the AI tell you what to work on next:**
```bash
> build
Choice: 5

Your skills:
  1. Python coding - beginner (2 completed)
  2. Machine Learning - intermediate (5 completed)

Skill: 2

🤔 Analyzing your progress in Machine Learning...

🎯 RECOMMENDED CHALLENGE

📝 Neural Network from Scratch
⏱️ Estimated time: 15 hours
📊 Difficulty: Advanced

💡 Why this challenge now:
 - Prerequisites met: Python, NumPy, ML fundamentals
 - Matches your progression (5+ projects completed)
 - Teaches new skills: backpropagation, gradient descent deep dive
 - Unlocks: Deep Learning projects, CNN architectures

📚 You'll learn: backpropagation, activation functions, optimization

📖 Description:
Build a neural network from scratch without frameworks. Implement forward
propagation, backpropagation, and gradient descent. Train on MNIST dataset
and visualize learning curves.

🚀 Start this challenge now? (y/n):
```

**How recommendations work:**
- Analyzes your completed challenges
- Checks prerequisites are met
- Matches difficulty to your level
- Considers skills you haven't learned yet
- Shows what completing it unlocks

---

### 6. View Learning Path 🗺️ (NEW!)

**See your complete progression path:**
```bash
> build
Choice: 6

Skill: Machine Learning

🗺️ Machine Learning Learning Path

✅ Regression Model Pipeline
   Difficulty: Intermediate | Est: 8h
   Status: Completed ✅
   Completed: 2024-12-01
       ↓

✅ Classification Battle
   Difficulty: Intermediate | Est: 10h
   Status: Completed ✅
   Completed: 2024-12-08
       ↓

⚙️ ML Math Foundation
   Difficulty: Intermediate | Est: 12h
   Status: In Progress (45%)
   Time spent: 5h 30m
       ↓

🎯 Neural Network from Scratch
   Difficulty: Advanced | Est: 15h
   Status: RECOMMENDED 🎯
   
   Why now:
    • Prerequisites met: Python, NumPy, ML fundamentals
    • Matches your progression
    • Teaches: backpropagation, activation functions
       ↓

🔒 Deep Learning CNN Project
   Difficulty: Advanced | Est: 20h
   Status: Future (locked)
   Unlocked by: Neural Network from Scratch

Legend:
  ✅ Completed
  ⚙️ In Progress
  🎯 Recommended Next
  🔒 Future (locked)

🚀 Start the recommended challenge? (y/n):
```

**This shows:**
- What you've completed
- What you're working on
- What you should do next (and why)
- What's coming later

---

### 7. Search Past Obstacles

**Your personal knowledge base:**
```bash
> build
Choice: 7

Search obstacles: NaN predictions

📋 Found 2 obstacle(s):

1. Regression Model Pipeline
   Problem: Getting NaN values in predictions
   Solution: Missing values in data. Used SimpleImputer with mean
   Insight: Always check pd.isna().sum() before training
   Time: 45 min
   
2. Housing Price Predictor
   Problem: Model predicting NaN for some houses
   Solution: Log transform skewed features first
   Insight: Check feature distributions, transform if needed

View details? (1-2, or 0 to exit): 1
```

**Never solve the same problem twice!**

---

### 8. View All Challenges

Overview of everything:
```bash
> build
Choice: 8

✅ Completed (7):
  • CLI Todo App
  • Web Scraper
  • Regression Model Pipeline
  • Classification Battle
  • ML Math Foundation
  • Feature Engineering Lab
  • Ensemble Methods

⚙️ In Progress (2):
  • Neural Network from Scratch - 30%
  • Financial Portfolio Analyzer - 15%

📋 Available (12):
  • Housing Price Predictor (ML, intermediate, 8h)
  • Predictive Maintenance (ML, advanced, 14h)
  • Data Validator (Python, intermediate, 4h)
  • REST API (Python, intermediate, 5h)
  ...
```

---

### Complete Workflow Example

**Week 1: Start**
```bash
> build → 5 (Get recommendation)
Skill: Machine Learning
Recommended: Regression Model Pipeline

Start? y
✅ Challenge started!
```

**Week 1-2: Work & Learn**
```bash
# Day 1
> build → 2 (Continue)
Update progress: 20%, 2h
🔥 Streak: 1 day

# Day 3 - Hit obstacle
> build → 3 (Log obstacle)
Obstacle: NaN in predictions

# Day 4 - Solve it
> build → 2 → Solve obstacle
Solution: Missing data, used SimpleImputer
Time: 45 min
✅ Solved! 🎉

# Day 7
> build → 2 (Continue)
Update progress: 60%, 3h
🔥 Streak: 7 days
```

**Week 2: Complete**
```bash
> build → 2 (Continue)
Complete challenge? y
GitHub: github.com/you/regression-pipeline
Notes: Learned: missing data handling, feature scaling, model evaluation

✅ Challenge completed!
🏆 Skill progression: INTERMEDIATE (70%)

Next recommendation: Neural Network from Scratch
```

---

## 📖 Explanation System

Save AI-generated explanations as you learn.

### Request Explanation
```bash
> explain

Your skills:
  1. Python Programming
  2. Machine Learning

Which skill? 2
Topic: backpropagation

Custom guidance (optional): focus on intuition and examples

[Claude generates detailed explanation]

💾 Save? y
✅ Saved to: explanations/2_Machine_Learning/backpropagation.md
```

### Browse Explanations
```bash
> explain
Choice: 2  # Browse

📚 Your Saved Explanations

Machine Learning (8 explanations):
  1. Backpropagation
  2. Gradient Descent
  3. Overfitting vs Underfitting
  4. Cross Validation
  5. Feature Engineering
  6. Ensemble Methods
  7. Learning Rate Tuning
  8. Batch Normalization

Select: 1

[Shows backpropagation.md content]
```

### Search Explanations
```bash
> explain
Choice: 3  # Search

Search: gradient

Found 3 explanation(s):
  1. Gradient Descent (ML)
  2. Vanishing Gradient Problem (ML)
  3. Stochastic Gradient Descent (ML)

Select: 2
```

**Use cases:**
- Review concepts before challenges
- Build personal documentation
- Reference during coding
- Study for interviews

---

## 🎓 Traditional Learning Tracker

For theory-based learning (courses, books, lectures):
```bash
> learn

Options:
  1. View all skills
  2. Add new skill (basic)
  3. Add skill with AI roadmap 🤖
  4. Log learning session
  5. Review items (spaced repetition)
  6. Add learning item (Q&A, concept, fact)
  7. Search learning items
  8. View skill details
  9. Learning statistics
  10. Manage milestones
```

### Log Learning Session
```bash
> learn
Choice: 4

Skill: Machine Learning
Duration: 90 minutes
Topics: Watched lecture on CNNs, took notes
Understanding (1-5): 4

✅ Session logged!
```

### Add Q&A for Spaced Repetition
```bash
> learn
Choice: 6

Skill: Machine Learning
Type: question

Question: What is the vanishing gradient problem?
Answer: When gradients become very small during backprop in deep networks,
making early layers learn very slowly. Solved with ReLU, batch norm, etc.

Difficulty (1-5): 3

✅ Item added!
Next review: 2024-12-05
```

### Review Items
```bash
> learn
Choice: 5

📚 Review Session

Item 1/5:
Q: What is the vanishing gradient problem?

[Press Enter to see answer]

A: When gradients become very small during backprop...

How confident? (1-5): 4

[Algorithm adjusts next review date based on confidence]
```

---

## 🧠 Memory System

### Natural Learning

Just chat naturally:
```
You: Remember that I'm working on a factory optimization ML project
You: I prefer Python over R for data analysis
You: My goal is to reduce downtime by 20%

[Later]

You: What ML project am I working on?
Claude: You're working on a factory optimization ML project with a goal
        to reduce downtime by 20%, using Python for data analysis.
```

### Manual Memory
```bash
> remember
Fact: I completed AWS ML certification
✅ Remembered!

> recall
Search: certification

Found: I completed AWS ML certification (saved 2024-12-01)
```

### Goal Tracking
```bash
> goals

Current goals:
  1. Complete 5 ML challenges (3/5 done)
  2. Build portfolio project
  3. Apply to 10 jobs

Add new goal? y
Goal: Deploy ML model to production
Target date: 2025-03-01
✅ Goal added!
```

---

## 📁 File Intelligence

### Auto-Indexing
```bash
# Start watcher
python -m automation.file_watcher

# Drop files into files/watched/
# → Automatically indexed and searchable
```

### Search Files
```bash
> files

Search: machine learning papers

Found 3 files:
  1. attention_is_all_you_need.pdf
  2. resnet_paper.pdf
  3. ml_notes_2024.txt

Select: 1
[Shows summary and content]
```

---

## ✍️ Writing Assistant

### Save Your Style
```bash
> style

Describe your writing style:
> Concise, active voice, max 150 words per paragraph,
> use bullet points, technical but accessible

✅ Style saved!
```

### Apply Style
```bash
> edit

Text to edit:
> [Paste your draft]

✨ Edited version:
[Claude rewrites in your style]

Save? y
✅ Saved!
```

---

## 🤖 Automation

### File Watcher
```bash
python -m automation.file_watcher
```

Watches `files/watched/` and auto-indexes new files.

### Morning Routine
```bash
python -m automation.morning_routine
```

Daily briefing at 8 AM:
- Goals for today
- Due reviews
- Challenges in progress
- Streak status

---

## 📊 Understanding Your Data

### Database Structure
```
knowledge.db
├── Memory System
│   ├── facts                    # What Claude knows about you
│   ├── conversations            # Chat history
│   ├── goals                    # Your objectives
│   └── preferences              # Settings, style
│
├── Learning System
│   ├── learning_skills          # Skills + roadmap context
│   │   ├── current_level        # What you know
│   │   ├── goals                # Why you're learning
│   │   ├── timeline             # When you want mastery
│   │   └── roadmap_generated    # Has AI roadmap?
│   │
│   ├── learning_sessions        # Time-based logs
│   ├── learning_items           # Q&A for review
│   └── review_history           # Spaced repetition data
│
└── Challenge System
    ├── learning_challenges      # Projects to build
    ├── challenge_obstacles      # Problems & solutions
    ├── daily_streaks            # Consistency tracking
    └── skill_evidence           # Proof of competency
```

### Skill Progression Algorithm
```python
completed_projects = count(status='completed')

if completed >= 10:
    level = 'advanced' (90%)
elif completed >= 5:
    level = 'intermediate' (70%)
elif completed >= 2:
    level = 'beginner+' (50%)
elif completed >= 1:
    level = 'beginner' (30%)
else:
    level = 'just_starting' (10%)
```

**Evidence-based:** Actual completed projects, not just time.

---

## 💡 Pro Tips

### For Maximum Learning

1. **Let AI create your roadmap** - It asks the right questions and builds a personalized path
2. **Follow recommendations** - The AI knows what you should do next
3. **Log obstacles immediately** - Capture the learning moment
4. **Complete challenges before starting new ones** - Finish what you start
5. **Review obstacles before similar challenges** - Search your solutions
6. **Maintain your streak** - Consistency beats intensity
7. **Use explanations liberally** - Build your knowledge base

### For Staying Organized

1. **One skill at a time** - Deep focus beats shallow dabbling
2. **Check learning path weekly** - See the big picture
3. **Review roadmap context** - Remember why you're learning
4. **Set realistic timelines** - 3-6 months per skill
5. **Celebrate completions** - Each finished project matters

### For Career Development

1. **Track GitHub links** - Build your portfolio
2. **Write good challenge notes** - They become talking points
3. **Focus on business value** - Factory optimization, cost reduction
4. **Document insights** - Show problem-solving ability
5. **Export progression data** - Show evidence of growth

---

## 🚀 Getting Started Checklist

**Setup (5 minutes):**
- [ ] `pip install -r requirements.txt`
- [ ] Add API key to `.env`
- [ ] Run `python main.py`

**First Skill (30 minutes):**
- [ ] `learn` → `3` (Add skill with AI roadmap)
- [ ] Answer interview questions thoughtfully
- [ ] Review generated challenges
- [ ] Accept the roadmap

**First Challenge (This Week):**
- [ ] `build` → `5` (Get recommendation)
- [ ] Start the recommended challenge
- [ ] Work on it for 2-3 hours
- [ ] Log at least one obstacle
- [ ] Complete the challenge

**Build Habit (This Month):**
- [ ] Build 7-day streak
- [ ] Complete 3 challenges
- [ ] Save 5 explanations
- [ ] Search obstacles 3 times
- [ ] Review learning path weekly

---

## 🐛 Troubleshooting

### Database Errors
```bash
# Reset database
rm brain/knowledge.db
python main.py
```

### No Recommendations

**Reasons:**
- No challenges created (generate roadmap)
- All prerequisites not met
- All challenges completed (add more!)
```bash
> learn → 8 → [skill] → 2 (Add more challenges)
```

### Challenges Not Parsing

**Check:**
- Claude API working?
- Internet connection?
- Try again (Claude might format differently)

### Streaks Not Tracking

**Make sure:**
- Update progress when working
- Log time spent
- System auto-tracks daily activity

---

## 📚 Learn More

- [Anthropic Claude API](https://docs.anthropic.com)
- [Spaced Repetition](https://en.wikipedia.org/wiki/Spaced_repetition)
- [Project-Based Learning](https://en.wikipedia.org/wiki/Project-based_learning)
- [Evidence-Based Learning](https://en.wikipedia.org/wiki/Evidence-based_education)

---

## 🎯 Philosophy

This system is built on three principles:

1. **Learn by Doing** - Projects over theory
2. **Evidence-Based Progress** - Completed work over time logged
3. **AI-Guided Growth** - Personalized paths over generic courses

**You don't learn to code by reading about code. You learn by writing code and fixing bugs.**

---

## 🤝 Contributing

Personal tool, but you can:
- Fork for your needs
- Share challenge ideas
- Report bugs
- Suggest improvements

---

## 📝 License

Personal use. Modify freely!

---

**Stop reading. Start building.** 🚀
```bash
python main.py
> learn
Choice: 3  # Create your first skill with AI roadmap
```

**Your personalized learning journey starts now.**