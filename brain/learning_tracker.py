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
