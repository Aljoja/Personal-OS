"""Morning routine automation"""

import schedule
import time
from datetime import datetime
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from brain.claude_client import PersonalClaude


def morning_routine():
    """Run morning routine"""
    print(f"\n☀️ Good morning! ({datetime.now().strftime('%A, %B %d, %Y')})\n")
    
    claude = PersonalClaude()
    
    prompt = """It's the start of a new day. Please:
1. Review my active goals
2. Suggest 3 priorities for today based on what you know about me
3. Give me a brief motivational message

Keep it concise and actionable."""
    
    response = claude.chat(prompt)
    print(response)
    print("\n" + "="*60 + "\n")


def schedule_routines():
    """Schedule automated routines"""
    # schedule.every().day.at("08:00").do(morning_routine)
    morning_routine()  # Run once immediately
    
    # print("⏰ Scheduled: Morning routine at 8:00 AM")
    # print("Running scheduler... (Ctrl+C to stop)\n")
    
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    schedule_routines()
