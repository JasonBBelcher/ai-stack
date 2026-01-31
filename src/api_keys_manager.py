"""
API Keys Manager - Secure storage and management of cloud provider API keys
"""
import json
import os
from pathlib import Path
from typing import Dict, Optional, Any
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
import base64
import getpass


class APIKeysManager:
    """Manages secure storage of API keys for cloud providers"""
    
    def __init__(self, keys_file: Optional[str] = None):
        self.keys_file = Path(keys_file or "config/api_keys.json")
        self.keys_file.parent.mkdir(parents=True, exist_ok=True)
        self._encryption_key = self._get_or_create_encryption_key()
        self._cipher_suite = Fernet(self._encryption_key)
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key"""
        key_file = self.keys_file.parent / ".encryption_key"
        
        if key_file.exists():
            try:
                with open(key_file, 'rb') as f:
                    return f.read()
            except Exception:
                pass
        
        # Create new key
        key = Fernet.generate_key()
        try:
            with open(key_file, 'wb') as f:
                f.write(key)
            # Set restrictive permissions
            os.chmod(key_file, 0o600)
        except Exception as e:
            print(f"Warning: Could not save encryption key: {e}")
        
        return key
    
    def _encrypt_data(self, data: str) -> str:
        """Encrypt data"""
        encrypted = self._cipher_suite.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    def _decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data"""
        try:
            encrypted = base64.b64decode(encrypted_data.encode())
            decrypted = self._cipher_suite.decrypt(encrypted)
            return decrypted.decode()
        except (InvalidToken, Exception) as e:
            raise ValueError(f"Failed to decrypt data: {e}")
    
    def load_keys(self) -> Dict[str, Dict[str, Any]]:
        """Load API keys from encrypted storage"""
        if not self.keys_file.exists():
            return {}
        
        try:
            with open(self.keys_file, 'r', encoding='utf-8') as f:
                encrypted_data = f.read()
            
            if not encrypted_data:
                return {}
            
            decrypted = self._decrypt_data(encrypted_data)
            return json.loads(decrypted)
            
        except Exception as e:
            print(f"Error loading API keys: {e}")
            return {}
    
    def save_keys(self, keys: Dict[str, Dict[str, Any]]) -> bool:
        """Save API keys to encrypted storage"""
        try:
            data = json.dumps(keys)
            encrypted_data = self._encrypt_data(data)
            
            with open(self.keys_file, 'w', encoding='utf-8') as f:
                f.write(encrypted_data)
            
            # Set restrictive permissions
            os.chmod(self.keys_file, 0o600)
            return True
            
        except Exception as e:
            print(f"Error saving API keys: {e}")
            return False
    
    def set_key(self, provider: str, key: str, **kwargs) -> bool:
        """Set API key for a provider"""
        keys = self.load_keys()
        
        keys[provider] = {
            'key': key,
            'last_updated': str(os.path.getmtime(self.keys_file)) if self.keys_file.exists() else None,
            **kwargs
        }
        
        return self.save_keys(keys)
    
    def get_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider"""
        keys = self.load_keys()
        provider_data = keys.get(provider)
        
        if provider_data:
            return provider_data.get('key')
        return None
    
    def has_key(self, provider: str) -> bool:
        """Check if API key exists for provider"""
        return self.get_key(provider) is not None
    
    def remove_key(self, provider: str) -> bool:
        """Remove API key for a provider"""
        keys = self.load_keys()
        
        if provider in keys:
            del keys[provider]
            return self.save_keys(keys)
        
        return True
    
    def list_providers(self) -> List[str]:
        """List all providers with stored keys"""
        keys = self.load_keys()
        return list(keys.keys())
    
    def validate_key(self, provider: str, key: Optional[str] = None) -> bool:
        """Validate API key for a provider"""
        key = key or self.get_key(provider)
        if not key:
            return False
        
        # Provider-specific validation
        if provider == "openai":
            return self._validate_openai_key(key)
        elif provider == "anthropic":
            return self._validate_anthropic_key(key)
        else:
            # Unknown provider, assume valid if key exists
            return True
    
    def _validate_openai_key(self, key: str) -> bool:
        """Validate OpenAI API key"""
        import requests
        
        try:
            headers = {
                'Authorization': f'Bearer {key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                'https://api.openai.com/v1/models',
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"OpenAI key validation error: {e}")
            return False
    
    def _validate_anthropic_key(self, key: str) -> bool:
        """Validate Anthropic API key"""
        import requests
        
        try:
            headers = {
                'x-api-key': key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
            
            response = requests.get(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                timeout=10
            )
            
            # Anthropic returns 401 for invalid keys, 200 for valid ones (even with empty content)
            return response.status_code in [200, 400]  # 400 might mean no messages but key is valid
            
        except Exception as e:
            print(f"Anthropic key validation error: {e}")
            return False
    
    def prompt_for_key(self, provider: str, force: bool = False) -> Optional[str]:
        """Prompt user to enter API key"""
        key = self.get_key(provider)
        
        if key and not force:
            use_existing = input(f"Use existing {provider} API key? (y/n): ").lower().strip()
            if use_existing in ['y', 'yes']:
                return key
        
        # Prompt for new key
        key = getpass.getpass(f"Enter {provider} API key: ").strip()
        
        if not key:
            return None
        
        # Validate the key
        if self.validate_key(provider, key):
            self.set_key(provider, key)
            print(f"✓ {provider} API key validated and saved")
            return key
        else:
            print(f"✗ Invalid {provider} API key")
            return None
    
    def setup_interactive(self) -> Dict[str, bool]:
        """Interactive setup of API keys"""
        print("=== API Keys Setup ===")
        print("Configure API keys for cloud model fallbacks")
        print("Leave blank to skip any provider\n")
        
        results = {}
        
        # OpenAI
        print("\n1. OpenAI (for GPT models)")
        openai_key = self.prompt_for_key("openai")
        results["openai"] = openai_key is not None
        
        # Anthropic
        print("\n2. Anthropic (for Claude models)")
        anthropic_key = self.prompt_for_key("anthropic")
        results["anthropic"] = anthropic_key is not None
        
        # Summary
        configured = sum(results.values())
        total = len(results)
        
        print(f"\n=== Setup Complete ===")
        print(f"Configured {configured}/{total} providers")
        
        if configured > 0:
            print("✓ Cloud fallbacks are now available")
        else:
            print("⚠ No cloud providers configured")
        
        return results
    
    def get_provider_info(self, provider: str) -> Optional[Dict[str, Any]]:
        """Get information about a provider"""
        keys = self.load_keys()
        provider_data = keys.get(provider)
        
        if not provider_data:
            return None
        
        # Add provider-specific info
        info = provider_data.copy()
        
        if provider == "openai":
            info.update({
                'name': 'OpenAI',
                'models': ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo'],
                'description': 'OpenAI GPT models'
            })
        elif provider == "anthropic":
            info.update({
                'name': 'Anthropic',
                'models': ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
                'description': 'Anthropic Claude models'
            })
        
        return info
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of API keys configuration"""
        keys = self.load_keys()
        status = {}
        
        for provider, data in keys.items():
            is_valid = self.validate_key(provider)
            status[provider] = {
                'configured': True,
                'valid': is_valid,
                'last_updated': data.get('last_updated'),
                'info': self.get_provider_info(provider)
            }
        
        # Add not configured providers
        all_providers = ['openai', 'anthropic']
        for provider in all_providers:
            if provider not in status:
                status[provider] = {
                    'configured': False,
                    'valid': False,
                    'info': self.get_provider_info(provider)
                }
        
        return status
    
    def export_keys(self, export_path: str, include_keys: bool = False) -> bool:
        """Export API keys configuration"""
        try:
            keys = self.load_keys()
            
            if include_keys:
                export_data = keys
            else:
                # Export only metadata (without actual keys)
                export_data = {}
                for provider, data in keys.items():
                    export_data[provider] = {
                        k: v for k, v in data.items() 
                        if k != 'key'
                    }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            # Set restrictive permissions
            os.chmod(export_path, 0o600)
            return True
            
        except Exception as e:
            print(f"Error exporting API keys: {e}")
            return False
    
    def import_keys(self, import_path: str, include_keys: bool = True) -> bool:
        """Import API keys configuration"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if include_keys:
                keys = import_data
            else:
                # Load existing keys and update metadata
                keys = self.load_keys()
                for provider, data in import_data.items():
                    if provider in keys:
                        keys[provider].update(data)
                    else:
                        # Import without the actual key
                        keys[provider] = {
                            k: v for k, v in data.items() 
                            if k != 'key'
                        }
            
            return self.save_keys(keys)
            
        except Exception as e:
            print(f"Error importing API keys: {e}")
            return False
    
    def rotate_key(self, provider: str) -> bool:
        """Rotate API key for a provider"""
        print(f"Rotating {provider} API key...")
        
        # Prompt for new key
        new_key = getpass.getpass(f"Enter new {provider} API key: ").strip()
        
        if not new_key:
            return False
        
        # Validate new key
        if self.validate_key(provider, new_key):
            if self.set_key(provider, new_key):
                print(f"✓ {provider} API key rotated successfully")
                return True
        
        print(f"✗ Failed to rotate {provider} API key")
        return False


# Global instance for easy access
_api_keys_manager = None

def get_api_keys_manager() -> APIKeysManager:
    """Get global API keys manager instance"""
    global _api_keys_manager
    if _api_keys_manager is None:
        _api_keys_manager = APIKeysManager()
    return _api_keys_manager