from brain.learning_tracker import LearningTracker

tracker = LearningTracker()
cursor = tracker.conn.cursor()

print("=" * 60)
print("Current Skills:")
print("=" * 60)

# Show all skills
cursor.execute("SELECT id, skill_name, category FROM learning_skills ORDER BY id")
skills = cursor.fetchall()

for skill in skills:
    print(f"  {skill[0]:2d}. {skill[1]:30s} ({skill[2]})")

print("\n" + "=" * 60)
print("Skills to Delete:")
print("=" * 60)

# Identify test skills
test_keywords = ['test', 'debug', 'parser']
to_delete = []

for skill in skills:
    skill_id, skill_name, category = skill
    skill_lower = skill_name.lower()
    
    if any(keyword in skill_lower for keyword in test_keywords):
        to_delete.append(skill_id)
        print(f"  ❌ {skill_id}. {skill_name}")

print("\n" + "=" * 60)
print("Skills to Keep:")
print("=" * 60)

for skill in skills:
    skill_id, skill_name, category = skill
    if skill_id not in to_delete:
        print(f"  ✅ {skill_id}. {skill_name}")

# Confirm
print("\n" + "=" * 60)
if to_delete:
    confirm = input(f"\nDelete {len(to_delete)} test skill(s)? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        # Delete challenges first (foreign key constraint)
        for skill_id in to_delete:
            cursor.execute("DELETE FROM learning_challenges WHERE skill_id = ?", (skill_id,))
            print(f"  🗑️  Deleted challenges for skill {skill_id}")
        
        # Delete skills
        placeholders = ','.join('?' * len(to_delete))
        cursor.execute(f"DELETE FROM learning_skills WHERE id IN ({placeholders})", to_delete)
        
        tracker.conn.commit()
        
        print(f"\n✅ Deleted {len(to_delete)} skill(s) and their challenges")
        
        # Show remaining skills
        print("\n" + "=" * 60)
        print("Remaining Skills:")
        print("=" * 60)
        
        cursor.execute("SELECT id, skill_name FROM learning_skills ORDER BY id")
        for skill in cursor.fetchall():
            print(f"  {skill[0]}. {skill[1]}")
    else:
        print("Cancelled.")
else:
    print("No test skills found.")