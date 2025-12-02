from brain.learning_tracker import LearningTracker
tracker = LearningTracker()
cursor = tracker.conn.cursor()

# Delete ML skill and its data
cursor.execute("DELETE FROM learning_challenges WHERE skill_id = 5")
cursor.execute("DELETE FROM learning_skills WHERE id = 5")
tracker.conn.commit()

print("✅ Machine Learning skill deleted")