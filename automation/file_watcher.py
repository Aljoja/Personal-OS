"""Watch folder and auto-process new files"""

import os
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from brain.claude_client import PersonalClaude


class FileHandler(FileSystemEventHandler):
    """Handle file events"""
    
    def __init__(self, claude: PersonalClaude):
        self.claude = claude
        self.processed = set()
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        filepath = event.src_path
        if filepath in self.processed:
            return
        
        time.sleep(1)
        
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if len(content.strip()) > 0:
                print(f"\n📄 New file: {Path(filepath).name}")
                summary = self.claude.summarize_file(content, filepath)
                print(f"✅ Indexed:\n{summary}\n")
                
                self.processed.add(filepath)
        
        except Exception as e:
            print(f"Error processing {filepath}: {e}")


def start_watching(folder: str = "./files/watched"):
    """Start watching a folder"""
    folder_path = Path(folder)
    folder_path.mkdir(parents=True, exist_ok=True)
    
    print(f"👀 Watching: {folder_path.absolute()}")
    print("Drop files here - they'll be auto-indexed!\n")
    
    claude = PersonalClaude()
    event_handler = FileHandler(claude)
    observer = Observer()
    observer.schedule(event_handler, str(folder_path), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    start_watching()
