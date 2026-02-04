"""
Skills for Project Chimera

This module contains the Skill registry and all skill implementations.
"""

from typing import Dict, Type
from .skill_analyze_trends import AnalyzeTrendsSkill
from .skill_generate_image import GenerateImageSkill
from .skill_download_youtube import DownloadYoutubeSkill
from .skill_transcribe_audio import TranscribeAudioSkill
from .skill_post_content import PostContentSkill
from .skill_commerce import CommerceSkill
from .skill_memory import MemorySkill


class SkillRegistry:
    """Registry for managing Chimera agent skills."""
    
    def __init__(self):
        """Initialize the skill registry."""
        self._skills: Dict[str, Type] = {}
        self._register_default_skills()
    
    def _register_default_skills(self):
        """Register all default skills."""
        self.register("skill_analyze_trends", AnalyzeTrendsSkill)
        self.register("skill_generate_image", GenerateImageSkill)
        self.register("skill_download_youtube", DownloadYoutubeSkill)
        self.register("skill_transcribe_audio", TranscribeAudioSkill)
        self.register("skill_post_content", PostContentSkill)
        self.register("skill_commerce", CommerceSkill)
        self.register("skill_memory", MemorySkill)
    
    def register(self, name: str, skill_class: Type):
        """
        Register a skill with the registry.
        
        Args:
            name: The skill name
            skill_class: The skill class to register
        """
        self._skills[name] = skill_class
    
    def get(self, name: str):
        """
        Get a skill by name.
        
        Args:
            name: The skill name
            
        Returns:
            The skill class or None if not found
        """
        return self._skills.get(name)
    
    def list_skills(self) -> list[str]:
        """
        List all registered skills.
        
        Returns:
            List of skill names
        """
        return list(self._skills.keys())
    
    def _keys(self):
        """Return skill names iterator."""
        return self._skills.keys()
    
    def __contains__(self, name: str) -> bool:
        """Check if a skill is registered."""
        return name in self._skills
    
    def __len__(self) -> int:
        """Return number of registered skills."""
        return len(self._skills)


# Default registry instance
SkillRegistry = SkillRegistry
