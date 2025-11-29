from pathlib import Path
import re
from typing import Optional, List, Tuple


class ExplanationManager:
    """Manages saving and retrieving explanations as Markdown files"""
    
    def __init__(self, base_path: str = "explanations"):
        """
        Initialize the explanation manager
        
        Why this approach:
        - base_path stored as Path object (cross-platform)
        - Folder created on first save, not here (lazy initialization)
        - Keeps __init__ lightweight
        """
        self.base_path = Path(base_path)
    
    def _get_skill_folder(self, skill_id: int, skill_name: str) -> Path:
        """
        Get folder path for a skill
        
        Returns: explanations/{skill_id}_{skill_name}/
        
        Why include both ID and name:
        - ID ensures uniqueness (even if skill renamed)
        - Name makes folders human-readable
        - Underscore separates them clearly
        """
        # Sanitize skill name for folder (remove special chars, spaces)
        safe_name = re.sub(r'[^\w\s-]', '', skill_name)
        safe_name = re.sub(r'[-\s]+', '_', safe_name)
        
        return self.base_path / f"{skill_id}_{safe_name}"
    
    def _sanitize_topic(self, topic: str) -> str:
        """
        Convert topic to safe filename
        
        Example: "What are Python's decorators?" → "what_are_pythons_decorators"
        
        Why this approach:
        - Lowercase = consistent, avoids case issues
        - Underscores = readable, filesystem-safe
        - Remove special chars = avoid filesystem errors
        - Max 100 chars = prevent too-long filenames
        """
        # Convert to lowercase
        topic = topic.lower()
        # Replace spaces and hyphens with underscores
        topic = re.sub(r'[-\s]+', '_', topic)
        # Remove any character that's not alphanumeric or underscore
        topic = re.sub(r'[^\w]', '', topic)
        # Limit length
        topic = topic[:100]
        
        return topic
    
    def save_explanation(self, skill_id: int, skill_name: str, 
                        topic: str, content: str) -> Tuple[bool, str]:
        """
        Save explanation to markdown file
        
        Returns: (success: bool, filepath: str)
        
        Why return tuple:
        - bool = caller knows if it worked
        - filepath = caller can show user where it saved
        
        Why create folders here (not __init__):
        - Lazy initialization = only create when needed
        - No wasted folders for unused features
        """
        try:
            # Get skill folder path
            skill_folder = self._get_skill_folder(skill_id, skill_name)
            
            # Create folder if doesn't exist
            skill_folder.mkdir(parents=True, exist_ok=True)
            
            # Sanitize topic for filename
            safe_topic = self._sanitize_topic(topic)
            
            # Create file path
            filepath = skill_folder / f"{safe_topic}.md"
            
            # Write content
            filepath.write_text(content, encoding='utf-8')
            
            return True, str(filepath)
            
        except Exception as e:
            return False, str(e)
    
    def get_explanation(self, skill_id: int, skill_name: str, 
                       topic: str) -> Optional[str]:
        """
        Load explanation from file
        
        Returns: content string or None if not found
        
        Why return None (not raise exception):
        - None = "not found" is expected behavior
        - Exception = unexpected error
        - Caller can easily check: if content is None
        """
        try:
            skill_folder = self._get_skill_folder(skill_id, skill_name)
            safe_topic = self._sanitize_topic(topic)
            filepath = skill_folder / f"{safe_topic}.md"
            
            if not filepath.exists():
                return None
            
            return filepath.read_text(encoding='utf-8')
            
        except Exception:
            return None
    
    def list_explanations(self, skill_id: int, skill_name: str) -> List[str]:
        """
        List all explanation topics for a skill
        
        Returns: List of topic names (not filenames)
        
        Why convert filenames back to topics:
        - User sees "List Comprehensions", not "list_comprehensions.md"
        - More user-friendly
        - Hides implementation details
        """
        try:
            skill_folder = self._get_skill_folder(skill_id, skill_name)
            
            if not skill_folder.exists():
                return []
            
            # Get all .md files
            md_files = skill_folder.glob("*.md")
            
            # Convert filenames back to readable topics
            topics = []
            for file in md_files:
                # Remove .md extension and convert underscores to spaces
                topic = file.stem.replace('_', ' ').title()
                topics.append(topic)
            
            return sorted(topics)
            
        except Exception:
            return []
    
    def explanation_exists(self, skill_id: int, skill_name: str, 
                          topic: str) -> bool:
        """
        Check if explanation already exists
        
        Why separate method:
        - Check before saving (warn user about overwrite)
        - Simpler than loading full content just to check
        - Single responsibility principle
        """
        skill_folder = self._get_skill_folder(skill_id, skill_name)
        safe_topic = self._sanitize_topic(topic)
        filepath = skill_folder / f"{safe_topic}.md"
        
        return filepath.exists()