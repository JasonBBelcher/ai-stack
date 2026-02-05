"""
Profile Manager - User configuration profile management system
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# No ModelType import needed in profile_manager


@dataclass
class UserProfile:
    """User profile for model configuration and preferences"""
    name: str
    description: str
    created_at: datetime
    modified_at: datetime
    
    # Role mappings
    role_mappings: Dict[str, Dict[str, Any]]
    
    # System settings overrides
    system_settings: Dict[str, Any]
    
    # Selection preferences
    selection_preferences: Dict[str, Any]
    
    # Cloud provider settings
    cloud_settings: Dict[str, Any]
    
    # Cascade processing settings
    cascade_settings: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert datetime to ISO string
        data['created_at'] = self.created_at.isoformat()
        data['modified_at'] = self.modified_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """Create from dictionary"""
        # Convert ISO string to datetime
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if isinstance(data.get('modified_at'), str):
            data['modified_at'] = datetime.fromisoformat(data['modified_at'])
        
        return cls(**data)


class ProfileManager:
    """Manages user configuration profiles"""
    
    def __init__(self, profiles_dir: Optional[str] = None):
        self.profiles_dir = Path(profiles_dir or "config/user_profiles")
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        
        self._active_profile_file = self.profiles_dir.parent / "active_profile.txt"
        self._profiles_cache: Dict[str, UserProfile] = {}
        self._active_profile: Optional[str] = None
        
        # Load existing profiles
        self._load_all_profiles()
        self._load_active_profile()
    
    def _load_all_profiles(self) -> None:
        """Load all profiles from disk"""
        self._profiles_cache.clear()
        
        for profile_file in self.profiles_dir.glob("*.json"):
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
                
                profile = UserProfile.from_dict(profile_data)
                self._profiles_cache[profile.name] = profile
                
            except Exception as e:
                print(f"Error loading profile {profile_file}: {e}")
    
    def _load_active_profile(self) -> None:
        """Load the active profile name"""
        try:
            if self._active_profile_file.exists():
                with open(self._active_profile_file, 'r', encoding='utf-8') as f:
                    self._active_profile = f.read().strip()
        except Exception as e:
            print(f"Error loading active profile: {e}")
            self._active_profile = None
    
    def _save_active_profile(self, profile_name: str) -> None:
        """Save the active profile name"""
        try:
            with open(self._active_profile_file, 'w', encoding='utf-8') as f:
                f.write(profile_name)
            self._active_profile = profile_name
        except Exception as e:
            print(f"Error saving active profile: {e}")
    
    def _get_profile_path(self, profile_name: str) -> Path:
        """Get file path for a profile"""
        return self.profiles_dir / f"{profile_name}.json"
    
    def save_profile(self, profile: UserProfile, overwrite: bool = False) -> bool:
        """Save a profile to disk"""
        profile_path = self._get_profile_path(profile.name)
        
        if profile_path.exists() and not overwrite:
            return False
        
        try:
            profile.modified_at = datetime.now()
            
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)
            
            self._profiles_cache[profile.name] = profile
            return True
            
        except Exception as e:
            print(f"Error saving profile {profile.name}: {e}")
            return False
    
    def load_profile(self, profile_name: str) -> Optional[UserProfile]:
        """Load a specific profile"""
        return self._profiles_cache.get(profile_name)
    
    def delete_profile(self, profile_name: str) -> bool:
        """Delete a profile"""
        if profile_name not in self._profiles_cache:
            return False
        
        try:
            profile_path = self._get_profile_path(profile_name)
            if profile_path.exists():
                profile_path.unlink()
            
            del self._profiles_cache[profile_name]
            
            # If this was the active profile, clear it
            if self._active_profile == profile_name:
                self._active_profile = None
                if self._active_profile_file.exists():
                    self._active_profile_file.unlink()
            
            return True
            
        except Exception as e:
            print(f"Error deleting profile {profile_name}: {e}")
            return False
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """List all profiles with summary information"""
        profiles = []
        
        for profile_name, profile in self._profiles_cache.items():
            profiles.append({
                'name': profile_name,
                'description': profile.description,
                'created_at': profile.created_at.isoformat(),
                'modified_at': profile.modified_at.isoformat(),
                'is_active': profile_name == self._active_profile
            })
        
        return profiles
    
    def set_active_profile(self, profile_name: str) -> bool:
        """Set the active profile"""
        if profile_name not in self._profiles_cache:
            return False
        
        self._save_active_profile(profile_name)
        return True
    
    def get_active_profile(self) -> Optional[UserProfile]:
        """Get the currently active profile"""
        if not self._active_profile:
            return None
        return self._profiles_cache.get(self._active_profile)
    
    def get_active_profile_name(self) -> Optional[str]:
        """Get the name of the active profile"""
        return self._active_profile
    
    def create_profile_from_current_config(
        self, 
        name: str, 
        description: str,
        current_config: Dict[str, Any]
    ) -> UserProfile:
        """Create a new profile from current configuration"""
        now = datetime.now()
        
        # Extract relevant configuration parts
        profile = UserProfile(
            name=name,
            description=description,
            created_at=now,
            modified_at=now,
            role_mappings=current_config.get('role_mappings', {}),
            system_settings=current_config.get('system_settings', {}),
            selection_preferences=current_config.get('selection_preferences', {}),
            cloud_settings=current_config.get('cloud_settings', {})
        )
        
        return profile
    
    def create_default_profiles(self) -> None:
        """Create default profiles if they don't exist"""
        
        # Coding profile
        if 'coding' not in self._profiles_cache:
            coding_profile = UserProfile(
                name='coding',
                description='Optimized for programming and development tasks',
                created_at=datetime.now(),
                modified_at=datetime.now(),
                role_mappings={
                    'planner': {
                        'preferred': ['llama3.1:8b', 'mistral:latest'],
                        'reasoning_strength': 0.8,
                        'context_length_min': 8000
                    },
                    'critic': {
                        'preferred': ['llama3.1:8b', 'qwen2.5:7b'],
                        'reasoning_strength': 0.85
                    },
                    'executor': {
                        'preferred': ['qwen2.5-coder:14b', 'qwen2.5:14b'],
                        'coding_strength': 0.9
                    }
                },
                system_settings={
                    'enable_cloud_fallbacks': True,
                    'max_memory_usage_gb': 12.0,
                    'thermal_threshold': 0.7
                },
                selection_preferences={
                    'prefer_local': True,
                    'prefer_smaller': False
                },
                cloud_settings={
                    'enable_openai': True,
                    'enable_anthropic': False
                }
            )
            self.save_profile(coding_profile)
        
        # Writing profile
        if 'writing' not in self._profiles_cache:
            writing_profile = UserProfile(
                name='writing',
                description='Optimized for creative writing and content creation',
                created_at=datetime.now(),
                modified_at=datetime.now(),
                role_mappings={
                    'planner': {
                        'preferred': ['llama3.1:8b', 'mistral:latest'],
                        'creativity': 0.7,
                        'context_length_min': 16000
                    },
                    'critic': {
                        'preferred': ['llama3.1:8b', 'claude-3-haiku'],
                        'creativity': 0.6
                    },
                    'executor': {
                        'preferred': ['gpt-4o', 'claude-3.5-sonnet'],
                        'creativity': 0.8
                    }
                },
                system_settings={
                    'enable_cloud_fallbacks': True,
                    'max_memory_usage_gb': 10.0,
                    'thermal_threshold': 0.8
                },
                selection_preferences={
                    'prefer_local': False,
                    'prefer_larger': True
                },
                cloud_settings={
                    'enable_openai': True,
                    'enable_anthropic': True
                }
            )
            self.save_profile(writing_profile)
        
        # Research profile
        if 'research' not in self._profiles_cache:
            research_profile = UserProfile(
                name='research',
                description='Optimized for research and analysis tasks',
                created_at=datetime.now(),
                modified_at=datetime.now(),
                role_mappings={
                    'planner': {
                        'preferred': ['llama3.1:8b', 'mistral:latest'],
                        'reasoning_strength': 0.9,
                        'context_length_min': 32000
                    },
                    'critic': {
                        'preferred': ['llama3.1:8b', 'claude-3-haiku'],
                        'reasoning_strength': 0.95
                    },
                    'executor': {
                        'preferred': ['gpt-4o', 'claude-3-opus'],
                        'reasoning_strength': 0.9
                    }
                },
                system_settings={
                    'enable_cloud_fallbacks': True,
                    'max_memory_usage_gb': 14.0,
                    'thermal_threshold': 0.9
                },
                selection_preferences={
                    'prefer_local': False,
                    'prefer_larger': True
                },
                cloud_settings={
                    'enable_openai': True,
                    'enable_anthropic': True
                }
            )
            self.save_profile(research_profile)
    
    def get_profile_config_for_role(
        self, 
        role: ModelType,
        profile_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get role configuration from a profile"""
        
        profile_name = profile_name or self._active_profile
        if not profile_name:
            return None
        
        profile = self._profiles_cache.get(profile_name)
        if not profile:
            return None
        
        return profile.role_mappings.get(role.value)
    
    def get_system_settings_from_profile(
        self, 
        profile_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get system settings from a profile"""
        
        profile_name = profile_name or self._active_profile
        if not profile_name:
            return {}
        
        profile = self._profiles_cache.get(profile_name)
        if not profile:
            return {}
        
        return profile.system_settings
    
    def get_selection_preferences_from_profile(
        self, 
        profile_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get selection preferences from a profile"""
        
        profile_name = profile_name or self._active_profile
        if not profile_name:
            return {}
        
        profile = self._profiles_cache.get(profile_name)
        if not profile:
            return {}
        
        return profile.selection_preferences
    
    def export_profile(self, profile_name: str, export_path: str) -> bool:
        """Export a profile to a file"""
        profile = self._profiles_cache.get(profile_name)
        if not profile:
            return False
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting profile {profile_name}: {e}")
            return False
    
    def import_profile(self, import_path: str, new_name: Optional[str] = None) -> bool:
        """Import a profile from a file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            
            profile = UserProfile.from_dict(profile_data)
            
            # Override name if provided
            if new_name:
                profile.name = new_name
                profile.modified_at = datetime.now()
            
            return self.save_profile(profile, overwrite=False)
            
        except Exception as e:
            print(f"Error importing profile: {e}")
            return False
    
    def validate_profile(self, profile: UserProfile) -> List[str]:
        """Validate a profile and return issues"""
        issues = []
        
        # Check required fields
        if not profile.name:
            issues.append("Profile name is required")
        
        if not profile.role_mappings:
            issues.append("Role mappings are required")
        
        # Validate role mappings
        required_roles = ['planner', 'critic', 'executor']
        for role in required_roles:
            if role not in profile.role_mappings:
                issues.append(f"Missing role mapping for: {role}")
        
        # Validate system settings
        if profile.system_settings.get('max_memory_usage_gb', 16) <= 0:
            issues.append("Max memory usage must be positive")
        
        if profile.system_settings.get('thermal_threshold', 0.8) <= 0:
            issues.append("Thermal threshold must be positive")
        
        return issues
    
    def get_profile_statistics(self) -> Dict[str, Any]:
        """Get statistics about profiles"""
        total_profiles = len(self._profiles_cache)
        
        if total_profiles == 0:
            return {'total_profiles': 0}
        
        # Count by creation date
        creation_dates = [p.created_at for p in self._profiles_cache.values()]
        oldest_profile = min(creation_dates)
        newest_profile = max(creation_dates)
        
        # Count by modification
        recent_modifications = sum(
            1 for p in self._profiles_cache.values()
            if (datetime.now() - p.modified_at).days <= 7
        )
        
        return {
            'total_profiles': total_profiles,
            'oldest_profile': oldest_profile.isoformat(),
            'newest_profile': newest_profile.isoformat(),
            'recent_modifications': recent_modifications,
            'active_profile': self._active_profile
        }