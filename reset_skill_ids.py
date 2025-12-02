from brain.learning_tracker import LearningTracker

tracker = LearningTracker()
cursor = tracker.conn.cursor()

print("Current Skills:")
cursor.execute("SELECT id, skill_name FROM learning_skills ORDER BY id")
skills = cursor.fetchall()

for skill in skills:
    print(f"  {skill[0]}. {skill[1]}")

print("\n" + "="*60)
print("Reassigning IDs sequentially...")
print("="*60)

# Create mapping of old ID -> new ID
old_to_new = {}
new_id = 1

for skill in skills:
    old_id = skill[0]
    old_to_new[old_id] = new_id
    new_id += 1

# Temporarily disable foreign key constraints
cursor.execute("PRAGMA foreign_keys = OFF")

# Update skills table
for old_id, new_id in old_to_new.items():
    cursor.execute("UPDATE learning_skills SET id = ? WHERE id = ?", 
                   (-new_id, old_id))  # Negative to avoid conflicts

for old_id, new_id in old_to_new.items():
    cursor.execute("UPDATE learning_skills SET id = ? WHERE id = ?", 
                   (new_id, -new_id))

# Update foreign keys in related tables
for old_id, new_id in old_to_new.items():
    cursor.execute("UPDATE learning_challenges SET skill_id = ? WHERE skill_id = ?",
                   (-new_id, old_id))
    cursor.execute("UPDATE learning_sessions SET skill_id = ? WHERE skill_id = ?",
                   (-new_id, old_id))
    cursor.execute("UPDATE learning_items SET skill_id = ? WHERE skill_id = ?",
                   (-new_id, old_id))
    cursor.execute("UPDATE learning_milestones SET skill_id = ? WHERE skill_id = ?",
                   (-new_id, old_id))

for old_id, new_id in old_to_new.items():
    cursor.execute("UPDATE learning_challenges SET skill_id = ? WHERE skill_id = ?",
                   (new_id, -new_id))
    cursor.execute("UPDATE learning_sessions SET skill_id = ? WHERE skill_id = ?",
                   (new_id, -new_id))
    cursor.execute("UPDATE learning_items SET skill_id = ? WHERE skill_id = ?",
                   (new_id, -new_id))
    cursor.execute("UPDATE learning_milestones SET skill_id = ? WHERE skill_id = ?",
                   (new_id, -new_id))

# Reset auto-increment counter
cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'learning_skills'")
cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('learning_skills', ?)",
               (len(skills),))

# Re-enable foreign keys
cursor.execute("PRAGMA foreign_keys = ON")

tracker.conn.commit()

print("\n✅ IDs reassigned!")
print("\nNew Skills:")
cursor.execute("SELECT id, skill_name FROM learning_skills ORDER BY id")
for skill in cursor.fetchall():
    print(f"  {skill[0]}. {skill[1]}")