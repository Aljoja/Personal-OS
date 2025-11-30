"""Learning tracking system with spaced repetition and skill management"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import json


class LearningTracker:
    """Track learning progress with spaced repetition"""
    
    def __init__(self, db_path: str = "brain/knowledge.db"):

        self.db_path = Path(db_path).absolute()

        # Create connection
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        # Enable foreign key constraints
        self.conn.execute("PRAGMA foreign_keys = ON")
        # Continue with setup
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
    
    def _init_tables(self):
        """Initialize learning tracking tables"""
        cursor = self.conn.cursor()
        
        # Skills/Topics being learned
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_name TEXT UNIQUE NOT NULL,
                category TEXT,
                difficulty TEXT DEFAULT 'beginner',
                target_level TEXT,
                status TEXT DEFAULT 'active',
                start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_reviewed TIMESTAMP,
                next_review TIMESTAMP,
                total_time_minutes INTEGER DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Learning sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_id INTEGER NOT NULL,
                session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration_minutes INTEGER,
                topics_covered TEXT,
                understanding_level INTEGER CHECK(understanding_level BETWEEN 1 AND 5),
                notes TEXT,
                key_takeaways TEXT,
                FOREIGN KEY (skill_id) REFERENCES learning_skills(id)
            )
        """)
        
        # Learning items (facts, concepts, Q&A)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_id INTEGER NOT NULL,
                item_type TEXT NOT NULL,
                question TEXT,
                answer TEXT NOT NULL,
                difficulty INTEGER DEFAULT 3 CHECK(difficulty BETWEEN 1 AND 5),
                times_reviewed INTEGER DEFAULT 0,
                times_correct INTEGER DEFAULT 0,
                last_reviewed TIMESTAMP,
                next_review TIMESTAMP,
                confidence_level INTEGER DEFAULT 1 CHECK(confidence_level BETWEEN 1 AND 5),
                tags TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (skill_id) REFERENCES learning_skills(id)
            )
        """)
        
        # Review history for spaced repetition
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                was_correct BOOLEAN,
                confidence_before INTEGER,
                confidence_after INTEGER,
                time_taken_seconds INTEGER,
                FOREIGN KEY (item_id) REFERENCES learning_items(id)
            )
        """)
        
        # Learning goals and milestones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_id INTEGER NOT NULL,
                milestone TEXT NOT NULL,
                target_date DATE,
                completed BOOLEAN DEFAULT 0,
                completed_date TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (skill_id) REFERENCES learning_skills(id)
            )
        """)
        
        # Add indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_next_review 
            ON learning_items(next_review, skill_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_skills_next_review 
            ON learning_skills(next_review, status)
        """)

        # ===== NEW TABLES FOR CHALLENGE-BASED LEARNING =====
        
        # Learning challenges (projects to build)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS learning_challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                skill_id INTEGER NOT NULL,
                difficulty TEXT CHECK(difficulty IN ('beginner', 'intermediate', 'advanced')),
                estimated_hours INTEGER,
                skills_taught TEXT,
                prerequisites TEXT,
                unlocks TEXT,
                status TEXT DEFAULT 'not_started' CHECK(status IN ('not_started', 'in_progress', 'completed', 'abandoned')),
                progress_percent INTEGER DEFAULT 0,
                time_spent INTEGER DEFAULT 0,
                github_link TEXT,
                notes TEXT,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (skill_id) REFERENCES learning_skills(id)
            )
        """)
        
        # Obstacles encountered during challenges
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS challenge_obstacles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenge_id INTEGER NOT NULL,
                obstacle_description TEXT NOT NULL,
                solution TEXT,
                insight TEXT,
                time_to_solve INTEGER,
                resources_used TEXT,
                status TEXT DEFAULT 'blocking' CHECK(status IN ('blocking', 'solved', 'workaround')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                solved_at TIMESTAMP,
                FOREIGN KEY (challenge_id) REFERENCES learning_challenges(id)
            )
        """)
        
        # Daily building streaks
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_streaks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE NOT NULL,
                minutes_worked INTEGER DEFAULT 0,
                challenge_worked_on INTEGER,
                obstacles_encountered INTEGER DEFAULT 0,
                obstacles_solved INTEGER DEFAULT 0,
                maintained_streak BOOLEAN DEFAULT 1,
                notes TEXT,
                FOREIGN KEY (challenge_worked_on) REFERENCES learning_challenges(id)
            )
        """)
        
        # Skill mastery evidence (what you've actually built)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS skill_evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_id INTEGER NOT NULL,
                challenge_id INTEGER NOT NULL,
                evidence_type TEXT CHECK(evidence_type IN ('project_completed', 'obstacle_overcome', 'concept_applied')),
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (skill_id) REFERENCES learning_skills(id),
                FOREIGN KEY (challenge_id) REFERENCES learning_challenges(id)
            )
        """)
            
        self.conn.commit()
    
    def add_skill(self, skill_name: str, category: str = None, 
                  difficulty: str = 'beginner', target_level: str = None,
                  notes: str = None) -> int:
        """Start tracking a new skill"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO learning_skills 
                (skill_name, category, difficulty, target_level, notes, next_review)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (skill_name, category, difficulty, target_level, notes, 
                  datetime.now() + timedelta(days=1)))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"⚠️ Skill '{skill_name}' already exists")
            cursor.execute("SELECT id FROM learning_skills WHERE skill_name = ?", (skill_name,))
            return cursor.fetchone()['id']
    
    def get_all_skills(self, status: str = 'active') -> List[Dict]:
        """Get all skills being tracked"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT s.*, 
                   COUNT(DISTINCT ls.id) as session_count,
                   COUNT(DISTINCT li.id) as item_count
            FROM learning_skills s
            LEFT JOIN learning_sessions ls ON s.id = ls.skill_id
            LEFT JOIN learning_items li ON s.id = li.skill_id
            WHERE s.status = ?
            GROUP BY s.id
            ORDER BY s.last_reviewed DESC, s.created_at DESC
        """, (status,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_skill_details(self, skill_id: int) -> Dict:
        """Get detailed information about a skill"""
        # Check if skill exists
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id FROM learning_skills WHERE id = ?",
            (skill_id,)
        )
        skill = cursor.fetchone()

        if skill is None:
            # Skill doesn't exist!
            raise ValueError(f"Skill ID {skill_id} does not exist")
        
        # Get skill info
        cursor.execute("SELECT * FROM learning_skills WHERE id = ?", (skill_id,))
        skill = dict(cursor.fetchone())
        
        # Get recent sessions
        cursor.execute("""
            SELECT * FROM learning_sessions 
            WHERE skill_id = ? 
            ORDER BY session_date DESC 
            LIMIT 5
        """, (skill_id,))
        skill['recent_sessions'] = [dict(row) for row in cursor.fetchall()]
        
        # Get stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_items,
                AVG(confidence_level) as avg_confidence,
                SUM(times_correct) as total_correct,
                SUM(times_reviewed) as total_reviews
            FROM learning_items
            WHERE skill_id = ?
        """, (skill_id,))
        skill['stats'] = dict(cursor.fetchone())
        
        return skill
    
    def log_session(self, skill_id: int, duration_minutes: int,
                    topics_covered: str, understanding_level: int,
                    notes: str = None, key_takeaways: str = None) -> int:
        """Log a learning session"""
        cursor = self.conn.cursor()
        #Check if skill exists
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id FROM learning_skills WHERE id = ?",
            (skill_id,)
        )
        skill = cursor.fetchone()

        if skill is None:
            # Skill doesn't exist!
            raise ValueError(f"Skill ID {skill_id} does not exist")
        
        # Insert session
        cursor.execute("""
            INSERT INTO learning_sessions 
            (skill_id, duration_minutes, topics_covered, understanding_level, notes, key_takeaways)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (skill_id, duration_minutes, topics_covered, understanding_level, notes, key_takeaways))
        
        # Update skill stats
        cursor.execute("""
            UPDATE learning_skills 
            SET last_reviewed = CURRENT_TIMESTAMP,
                next_review = ?,
                total_time_minutes = total_time_minutes + ?
            WHERE id = ?
        """, (self._calculate_next_review(understanding_level), duration_minutes, skill_id))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def add_learning_item(self, skill_id: int, answer: str,
                         question: str = None, item_type: str = 'concept',
                         difficulty: int = 3, tags: str = None,
                         source: str = None) -> int:
        """Add a learning item (concept, Q&A, fact, etc.)"""
        # Check if skill exists
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id FROM learning_skills WHERE id = ?",
            (skill_id,)
        )
        skill = cursor.fetchone()

        if skill is None:
            # Skill doesn't exist!
            raise ValueError(f"Skill ID {skill_id} does not exist")
        
        next_review = datetime.now() + timedelta(days=1)  # Review tomorrow
        
        cursor.execute("""
            INSERT INTO learning_items 
            (skill_id, item_type, question, answer, difficulty, tags, source, next_review)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (skill_id, item_type, question, answer, difficulty, tags, source, next_review))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_items_due_for_review(self, skill_id: int = None, limit: int = 10) -> List[Dict]:
        """Get learning items due for review (spaced repetition)"""
        cursor = self.conn.cursor()
        
        if skill_id:
            cursor.execute("""
                SELECT li.*, ls.skill_name 
                FROM learning_items li
                JOIN learning_skills ls ON li.skill_id = ls.id
                WHERE li.skill_id = ? 
                  AND (li.next_review IS NULL OR li.next_review <= CURRENT_TIMESTAMP)
                ORDER BY li.next_review ASC, li.confidence_level ASC
                LIMIT ?
            """, (skill_id, limit))
        else:
            cursor.execute("""
                SELECT li.*, ls.skill_name 
                FROM learning_items li
                JOIN learning_skills ls ON li.skill_id = ls.id
                WHERE (li.next_review IS NULL OR li.next_review <= CURRENT_TIMESTAMP)
                  AND ls.status = 'active'
                ORDER BY li.next_review ASC, li.confidence_level ASC
                LIMIT ?
            """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def record_review(self, item_id: int, was_correct: bool, 
                     confidence_before: int, confidence_after: int,
                     time_taken_seconds: int = None):
        """Record a review of a learning item"""
        cursor = self.conn.cursor()
        
        # Insert review history
        cursor.execute("""
            INSERT INTO review_history 
            (item_id, was_correct, confidence_before, confidence_after, time_taken_seconds)
            VALUES (?, ?, ?, ?, ?)
        """, (item_id, was_correct, confidence_before, confidence_after, time_taken_seconds))
        
        # Update item stats
        cursor.execute("""
            UPDATE learning_items 
            SET times_reviewed = times_reviewed + 1,
                times_correct = times_correct + ?,
                last_reviewed = CURRENT_TIMESTAMP,
                next_review = ?,
                confidence_level = ?
            WHERE id = ?
        """, (1 if was_correct else 0, 
              self._calculate_next_review_for_item(was_correct, confidence_after),
              confidence_after, item_id))
        
        self.conn.commit()
    
    def _calculate_next_review(self, understanding_level: int) -> datetime:
        """Calculate next review date based on understanding"""
        # Spaced repetition intervals
        intervals = {
            1: 1,   # Poor understanding: review tomorrow
            2: 3,   # Below average: review in 3 days
            3: 7,   # Average: review in 1 week
            4: 14,  # Good: review in 2 weeks
            5: 30   # Excellent: review in 1 month
        }
        days = intervals.get(understanding_level, 7)
        return datetime.now() + timedelta(days=days)
    
    def _calculate_next_review_for_item(self, was_correct: bool, confidence: int) -> datetime:
        """Calculate next review for individual item"""
        if not was_correct:
            return datetime.now() + timedelta(hours=4)  # Review soon
        
        # Increasing intervals based on confidence
        intervals = {
            1: 1,   # Low confidence: review tomorrow
            2: 3,   # Some confidence: 3 days
            3: 7,   # Moderate: 1 week
            4: 14,  # Good: 2 weeks
            5: 30   # High: 1 month
        }
        days = intervals.get(confidence, 7)
        return datetime.now() + timedelta(days=days)
    
    def get_daily_review_summary(self) -> Dict:
        """Get summary of items due today"""
        cursor = self.conn.cursor()
        
        # Items due for review
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM learning_items
            WHERE next_review <= CURRENT_TIMESTAMP
        """)
        items_due = cursor.fetchone()['count']
        
        # Skills needing attention
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM learning_skills
            WHERE status = 'active' 
              AND next_review <= CURRENT_TIMESTAMP
        """)
        skills_due = cursor.fetchone()['count']
        
        # Recent progress
        cursor.execute("""
            SELECT 
                COUNT(*) as sessions_this_week,
                SUM(duration_minutes) as minutes_this_week
            FROM learning_sessions
            WHERE session_date >= date('now', '-7 days')
        """)
        progress = dict(cursor.fetchone())
        
        return {
            'items_due_for_review': items_due,
            'skills_needing_attention': skills_due,
            'sessions_this_week': progress['sessions_this_week'] or 0,
            'minutes_this_week': progress['minutes_this_week'] or 0
        }
    
    def search_learning_items(self, query: str, skill_id: int = None) -> List[Dict]:
        """Search through learning items"""
        cursor = self.conn.cursor()
        search_pattern = f"%{query}%"
        
        if skill_id:
            cursor.execute("""
                SELECT li.*, ls.skill_name
                FROM learning_items li
                JOIN learning_skills ls ON li.skill_id = ls.id
                WHERE li.skill_id = ?
                  AND (li.question LIKE ? OR li.answer LIKE ? OR li.tags LIKE ?)
                ORDER BY li.confidence_level ASC, li.last_reviewed DESC
            """, (skill_id, search_pattern, search_pattern, search_pattern))
        else:
            cursor.execute("""
                SELECT li.*, ls.skill_name
                FROM learning_items li
                JOIN learning_skills ls ON li.skill_id = ls.id
                WHERE (li.question LIKE ? OR li.answer LIKE ? OR li.tags LIKE ?)
                  AND ls.status = 'active'
                ORDER BY li.confidence_level ASC, li.last_reviewed DESC
                LIMIT 20
            """, (search_pattern, search_pattern, search_pattern))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def add_milestone(self, skill_id: int, milestone: str, 
                     target_date: str = None, notes: str = None) -> int:
        """Add a learning milestone"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO learning_milestones (skill_id, milestone, target_date, notes)
            VALUES (?, ?, ?, ?)
        """, (skill_id, milestone, target_date, notes))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_milestones(self, skill_id: int, include_completed: bool = False) -> List[Dict]:
        """Get milestones for a skill"""
        cursor = self.conn.cursor()
        
        if include_completed:
            cursor.execute("""
                SELECT * FROM learning_milestones
                WHERE skill_id = ?
                ORDER BY completed ASC, target_date ASC
            """, (skill_id,))
        else:
            cursor.execute("""
                SELECT * FROM learning_milestones
                WHERE skill_id = ? AND completed = 0
                ORDER BY target_date ASC
            """, (skill_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def complete_milestone(self, milestone_id: int):
        """Mark a milestone as completed"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE learning_milestones
            SET completed = 1, completed_date = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (milestone_id,))
        self.conn.commit()
    
    def get_learning_stats(self, days: int = 30) -> Dict:
        """Get learning statistics for the past N days"""
        cursor = self.conn.cursor()
        
        # Total time spent
        cursor.execute("""
            SELECT SUM(duration_minutes) as total_minutes
            FROM learning_sessions
            WHERE session_date >= date('now', ?)
        """, (f'-{days} days',))
        total_minutes = cursor.fetchone()['total_minutes'] or 0
        
        # Sessions by skill
        cursor.execute("""
            SELECT ls.skill_name, COUNT(*) as session_count, SUM(duration_minutes) as total_minutes
            FROM learning_sessions lses
            JOIN learning_skills ls ON lses.skill_id = ls.id
            WHERE lses.session_date >= date('now', ?)
            GROUP BY ls.skill_name
            ORDER BY total_minutes DESC
        """, (f'-{days} days',))
        by_skill = [dict(row) for row in cursor.fetchall()]
        
        # Review accuracy
        cursor.execute("""
            SELECT 
                COUNT(*) as total_reviews,
                SUM(CASE WHEN was_correct = 1 THEN 1 ELSE 0 END) as correct_reviews
            FROM review_history
            WHERE review_date >= date('now', ?)
        """, (f'-{days} days',))
        reviews = dict(cursor.fetchone())
        
        accuracy = 0
        if reviews['total_reviews'] > 0:
            accuracy = (reviews['correct_reviews'] / reviews['total_reviews']) * 100
        
        return {
            'total_minutes': total_minutes,
            'total_hours': round(total_minutes / 60, 1),
            'avg_minutes_per_day': round(total_minutes / days, 1),
            'by_skill': by_skill,
            'total_reviews': reviews['total_reviews'] or 0,
            'review_accuracy': round(accuracy, 1)
        }
    
    def close(self):
        """Close database connection"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close()

    # ===== CHALLENGE-BASED LEARNING METHODS =====

    def add_challenge(self, title: str, description: str, skill_id: int, 
                    difficulty: str, estimated_hours: int, skills_taught: list,
                    prerequisites: list = None, unlocks: list = None) -> int:
        """
        Add a new challenge to the database
        
        Returns: challenge_id
        
        Why this method:
        - Allows custom challenges beyond library
        - User can add their own project ideas
        - Flexible learning path
        """
        import json
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO learning_challenges 
            (title, description, skill_id, difficulty, estimated_hours, 
            skills_taught, prerequisites, unlocks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title, description, skill_id, difficulty, estimated_hours,
            json.dumps(skills_taught),
            json.dumps(prerequisites or []),
            json.dumps(unlocks or [])
        ))
        
        self.conn.commit()
        return cursor.lastrowid

    def get_all_challenges(self, skill_id: int = None, status: str = None) -> list:
        """
        Get challenges, optionally filtered by skill or status
        
        Why filtering:
        - View by skill (focus on Python projects)
        - View by status (what's in progress)
        - Overview of learning pipeline
        """
        import json
        
        query = "SELECT * FROM learning_challenges WHERE 1=1"
        params = []
        
        if skill_id:
            query += " AND skill_id = ?"
            params.append(skill_id)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC"
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        
        challenges = []
        for row in cursor.fetchall():
            challenge = dict(row)
            # Parse JSON fields
            challenge['skills_taught'] = json.loads(challenge['skills_taught']) if challenge['skills_taught'] else []
            challenge['prerequisites'] = json.loads(challenge['prerequisites']) if challenge['prerequisites'] else []
            challenge['unlocks'] = json.loads(challenge['unlocks']) if challenge['unlocks'] else []
            challenges.append(challenge)
        
        return challenges

    def start_challenge(self, challenge_id: int) -> bool:
        """
        Mark challenge as started
        
        Why separate method:
        - Clear action (starting != just viewing)
        - Timestamp when started
        - Analytics on completion time
        """
        from datetime import datetime
        
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE learning_challenges
            SET status = 'in_progress',
                started_at = ?
            WHERE id = ?
        """, (datetime.now(), challenge_id))
        
        self.conn.commit()
        return cursor.rowcount > 0

    def update_challenge_progress(self, challenge_id: int, progress_percent: int,
                                time_spent_minutes: int = 0, notes: str = None) -> bool:
        """
        Update progress on a challenge
        
        Why track progress:
        - See how far you've come
        - Motivating
        - Understand time investment
        """
        cursor = self.conn.cursor()
        
        # Get current time spent
        cursor.execute("SELECT time_spent FROM learning_challenges WHERE id = ?", (challenge_id,))
        row = cursor.fetchone()
        if not row:
            return False
        
        current_time = row['time_spent'] or 0
        new_time = current_time + time_spent_minutes
        
        update_query = """
            UPDATE learning_challenges
            SET progress_percent = ?,
                time_spent = ?
        """
        params = [progress_percent, new_time]
        
        if notes:
            update_query += ", notes = ?"
            params.append(notes)
        
        update_query += " WHERE id = ?"
        params.append(challenge_id)
        
        cursor.execute(update_query, params)
        self.conn.commit()
        
        return cursor.rowcount > 0

    def complete_challenge(self, challenge_id: int, github_link: str = None,
                        final_notes: str = None) -> bool:
        """
        Mark challenge as completed
        
        Why this matters:
        - Official completion = skill proven
        - GitHub link = portfolio evidence
        - Final notes = capture learnings
        """
        from datetime import datetime
        
        cursor = self.conn.cursor()
        
        update_query = """
            UPDATE learning_challenges
            SET status = 'completed',
                completed_at = ?,
                progress_percent = 100
        """
        params = [datetime.now()]
        
        if github_link:
            update_query += ", github_link = ?"
            params.append(github_link)
        
        if final_notes:
            update_query += ", notes = COALESCE(notes || '\n\n', '') || ?"
            params.append(f"Final notes: {final_notes}")
        
        update_query += " WHERE id = ?"
        params.append(challenge_id)
        
        cursor.execute(update_query, params)
        self.conn.commit()
        
        # Add skill evidence
        cursor.execute("SELECT skill_id FROM learning_challenges WHERE id = ?", (challenge_id,))
        row = cursor.fetchone()
        if row:
            cursor.execute("""
                INSERT INTO skill_evidence (skill_id, challenge_id, evidence_type, description)
                VALUES (?, ?, 'project_completed', 'Completed full challenge')
            """, (row['skill_id'], challenge_id))
            self.conn.commit()
        
        return True

    def log_obstacle(self, challenge_id: int, description: str) -> int:
        """
        Log an obstacle encountered during a challenge
        
        Why this is THE MOST IMPORTANT method:
        - Obstacles = where real learning happens
        - Track what blocks you
        - Build obstacle-solving library
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO challenge_obstacles
            (challenge_id, obstacle_description, status)
            VALUES (?, ?, 'blocking')
        """, (challenge_id, description))
        
        self.conn.commit()
        return cursor.lastrowid

    def solve_obstacle(self, obstacle_id: int, solution: str, insight: str = None,
                    time_to_solve: int = None, resources_used: str = None) -> bool:
        """
        Mark obstacle as solved with solution details
        
        Why capture this:
        - Solution = reference for future
        - Insight = deeper understanding
        - Time = track problem-solving skill growth
        - Resources = know what helps you learn
        """
        from datetime import datetime
        
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE challenge_obstacles
            SET solution = ?,
                insight = ?,
                time_to_solve = ?,
                resources_used = ?,
                status = 'solved',
                solved_at = ?
            WHERE id = ?
        """, (solution, insight, time_to_solve, resources_used, datetime.now(), obstacle_id))
        
        self.conn.commit()
        
        # Add skill evidence for obstacle overcome
        cursor.execute("""
            SELECT co.challenge_id, lc.skill_id
            FROM challenge_obstacles co
            JOIN learning_challenges lc ON co.challenge_id = lc.id
            WHERE co.id = ?
        """, (obstacle_id,))
        
        row = cursor.fetchone()
        if row:
            cursor.execute("""
                INSERT INTO skill_evidence (skill_id, challenge_id, evidence_type, description)
                VALUES (?, ?, 'obstacle_overcome', ?)
            """, (row['skill_id'], row['challenge_id'], solution[:200]))
            self.conn.commit()
        
        return True

    def get_obstacles_for_challenge(self, challenge_id: int) -> list:
        """Get all obstacles for a specific challenge"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM challenge_obstacles
            WHERE challenge_id = ?
            ORDER BY created_at DESC
        """, (challenge_id,))
        
        return [dict(row) for row in cursor.fetchall()]

    def search_past_obstacles(self, keyword: str) -> list:
        """
        Search past obstacles and solutions
        
        Why this is powerful:
        - "I've solved this before!"
        - Build personal Stack Overflow
        - Learn from past you
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT co.*, lc.title as challenge_title, ls.skill_name
            FROM challenge_obstacles co
            JOIN learning_challenges lc ON co.challenge_id = lc.id
            JOIN learning_skills ls ON lc.skill_id = ls.id
            WHERE co.obstacle_description LIKE ? OR co.solution LIKE ?
            ORDER BY co.solved_at DESC
        """, (f'%{keyword}%', f'%{keyword}%'))
        
        return [dict(row) for row in cursor.fetchall()]

    def log_daily_streak(self, minutes_worked: int, challenge_id: int = None,
                        obstacles_encountered: int = 0, obstacles_solved: int = 0,
                        notes: str = None) -> bool:
        """
        Log daily building activity
        
        Why daily logging:
        - Build consistency habit
        - Track streaks
        - See patterns in productivity
        """
        from datetime import date
        
        cursor = self.conn.cursor()
        
        # Check if today already logged
        cursor.execute("SELECT id FROM daily_streaks WHERE date = ?", (date.today(),))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing
            cursor.execute("""
                UPDATE daily_streaks
                SET minutes_worked = minutes_worked + ?,
                    obstacles_encountered = obstacles_encountered + ?,
                    obstacles_solved = obstacles_solved + ?,
                    notes = COALESCE(notes || '\n', '') || COALESCE(?, '')
                WHERE date = ?
            """, (minutes_worked, obstacles_encountered, obstacles_solved, notes, date.today()))
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO daily_streaks
                (date, minutes_worked, challenge_worked_on, obstacles_encountered, 
                obstacles_solved, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (date.today(), minutes_worked, challenge_id, obstacles_encountered,
                obstacles_solved, notes))
        
        self.conn.commit()
        return True

    def get_streak_stats(self) -> dict:
        """
        Get streak statistics
        
        Returns: current streak, longest streak, total days
        
        Why this matters:
        - Gamification = motivation
        - Visible progress
        - Don't break the chain!
        """
        from datetime import date, timedelta
        
        cursor = self.conn.cursor()
        
        # Get all streak days
        cursor.execute("""
            SELECT date FROM daily_streaks
            WHERE maintained_streak = 1
            ORDER BY date DESC
        """)
        
        dates = [row['date'] for row in cursor.fetchall()]
        
        if not dates:
            return {'current_streak': 0, 'longest_streak': 0, 'total_days': 0}
        
        # Calculate current streak
        current_streak = 0
        check_date = date.today()
        
        for streak_date in dates:
            if isinstance(streak_date, str):
                streak_date = date.fromisoformat(streak_date)
            
            if streak_date == check_date:
                current_streak += 1
                check_date -= timedelta(days=1)
            else:
                break
        
        # Calculate longest streak
        longest_streak = 1
        current_run = 1
        
        for i in range(len(dates) - 1):
            date1 = date.fromisoformat(dates[i]) if isinstance(dates[i], str) else dates[i]
            date2 = date.fromisoformat(dates[i+1]) if isinstance(dates[i+1], str) else dates[i+1]
            
            if (date1 - date2).days == 1:
                current_run += 1
                longest_streak = max(longest_streak, current_run)
            else:
                current_run = 1
        
        return {
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'total_days': len(dates)
        }

    def get_skill_progression(self, skill_id: int) -> dict:
        """
        Get skill progression based on challenges completed
        
        Returns evidence of competency, not just time spent
        
        Why this approach:
        - Completed projects = proof
        - Obstacles overcome = depth
        - Clear progression path
        """
        cursor = self.conn.cursor()
        
        # Get challenges for this skill
        cursor.execute("""
            SELECT 
                COUNT(*) as total_challenges,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
                SUM(time_spent) as total_minutes
            FROM learning_challenges
            WHERE skill_id = ?
        """, (skill_id,))
        
        challenge_stats = dict(cursor.fetchone())
        
        # Get obstacles for this skill
        cursor.execute("""
            SELECT 
                COUNT(*) as total_obstacles,
                SUM(CASE WHEN co.status = 'solved' THEN 1 ELSE 0 END) as solved_obstacles
            FROM challenge_obstacles co
            JOIN learning_challenges lc ON co.challenge_id = lc.id
            WHERE lc.skill_id = ?
        """, (skill_id,))
        
        obstacle_stats = dict(cursor.fetchone())
        
        # Get skill evidence
        cursor.execute("""
            SELECT COUNT(*) as evidence_count
            FROM skill_evidence
            WHERE skill_id = ?
        """, (skill_id,))
        
        evidence = cursor.fetchone()['evidence_count']
        
        # Calculate competency level (simple heuristic)
        completed = challenge_stats['completed'] or 0
        
        if completed >= 10:
            level = 'advanced'
            percent = 90
        elif completed >= 5:
            level = 'intermediate'
            percent = 70
        elif completed >= 2:
            level = 'beginner+'
            percent = 50
        elif completed >= 1:
            level = 'beginner'
            percent = 30
        else:
            level = 'just_starting'
            percent = 10
        
        return {
            **challenge_stats,
            **obstacle_stats,
            'evidence_count': evidence,
            'competency_level': level,
            'competency_percent': percent
        }
