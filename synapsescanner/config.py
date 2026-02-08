"""Configuration system for SynapseScanner."""
import os
from pathlib import Path
from typing import List, Optional, Dict, Any


class Config:
    """SynapseScanner configuration management."""
    
    DEFAULT_CONFIG = """# SynapseScanner Configuration
# Generated on first run - modify as needed

# Default sources to search
default_sources:
  - arxiv
  - semantic_scholar

# Maximum results per query
max_results: 15

# AI provider settings (null to disable)
# Options: "ollama", "openai", or null
ai_provider: null

# Ollama settings
ollama_model: "llama3.2"
ollama_url: "http://localhost:11434"

# OpenAI settings (requires OPENAI_API_KEY env var)
openai_model: "gpt-3.5-turbo"

# Webhook URL for notifications (null to disable)
webhook_url: null

# Obsidian vault path for exports
obsidian_vault: "~/SynapseNotes"

# Cache settings
cache_hours: 24

# Default search depth for rabbit holes (0-3)
default_depth: 0
"""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            home = Path.home()
            config_dir = home / ".synapse"
            config_dir.mkdir(parents=True, exist_ok=True)
            config_path = str(config_dir / "config.yaml")
        
        self.config_path = config_path
        self._data: Dict[str, Any] = {}
        self._load_or_create()
    
    def _load_or_create(self):
        """Load existing config or create default."""
        path = Path(self.config_path)
        
        if not path.exists():
            # Create default config
            path.write_text(self.DEFAULT_CONFIG)
            self._data = self._parse_yaml(self.DEFAULT_CONFIG)
        else:
            # Load existing config
            content = path.read_text()
            self._data = self._parse_yaml(content)
    
    def _parse_yaml(self, content: str) -> Dict[str, Any]:
        """Simple YAML parser for basic config."""
        data: Dict[str, Any] = {}
        current_list = None
        current_list_key = None
        
        for line in content.split('\n'):
            stripped = line.strip()
            
            # Skip comments and empty lines
            if not stripped or stripped.startswith('#'):
                continue
            
            # Check for list items
            if stripped.startswith('- '):
                if current_list_key and current_list is not None:
                    value = stripped[2:].strip().strip('"').strip("'")
                    current_list.append(value)
                continue
            
            # Check for key-value pairs
            if ':' in stripped:
                key, _, value = stripped.partition(':')
                key = key.strip()
                value = value.strip()
                
                # Start of a new list
                if not value:
                    data[key] = []
                    current_list = data[key]
                    current_list_key = key
                else:
                    # Parse value
                    parsed = self._parse_value(value)
                    data[key] = parsed
                    current_list = None
                    current_list_key = None
        
        return data
    
    def _parse_value(self, value: str) -> Any:
        """Parse a YAML value to appropriate Python type."""
        value = value.strip()
        
        # String with quotes
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return value[1:-1]
        
        # null/None
        if value.lower() in ('null', '~', ''):
            return None
        
        # Boolean
        if value.lower() in ('true', 'yes', 'on'):
            return True
        if value.lower() in ('false', 'no', 'off'):
            return False
        
        # Integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def save(self):
        """Save current config to file."""
        lines = ["# SynapseScanner Configuration", ""]
        
        for key, value in self._data.items():
            if isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
                lines.append("")
            elif value is None:
                lines.append(f"{key}: null")
            elif isinstance(value, bool):
                lines.append(f"{key}: {'true' if value else 'false'}")
            elif isinstance(value, (int, float)):
                lines.append(f"{key}: {value}")
            else:
                lines.append(f'{key}: "{value}"')
        
        Path(self.config_path).write_text('\n'.join(lines))
    
    # Property accessors
    @property
    def default_sources(self) -> List[str]:
        return self._data.get("default_sources", ["arxiv"])
    
    @default_sources.setter
    def default_sources(self, value: List[str]):
        self._data["default_sources"] = value
    
    @property
    def max_results(self) -> int:
        return self._data.get("max_results", 15)
    
    @max_results.setter
    def max_results(self, value: int):
        self._data["max_results"] = value
    
    @property
    def ai_provider(self) -> Optional[str]:
        return self._data.get("ai_provider")
    
    @ai_provider.setter
    def ai_provider(self, value: Optional[str]):
        self._data["ai_provider"] = value
    
    @property
    def ollama_model(self) -> str:
        return self._data.get("ollama_model", "llama3.2")
    
    @ollama_model.setter
    def ollama_model(self, value: str):
        self._data["ollama_model"] = value
    
    @property
    def ollama_url(self) -> str:
        return self._data.get("ollama_url", "http://localhost:11434")
    
    @ollama_url.setter
    def ollama_url(self, value: str):
        self._data["ollama_url"] = value
    
    @property
    def openai_model(self) -> str:
        return self._data.get("openai_model", "gpt-3.5-turbo")
    
    @openai_model.setter
    def openai_model(self, value: str):
        self._data["openai_model"] = value
    
    @property
    def webhook_url(self) -> Optional[str]:
        return self._data.get("webhook_url")
    
    @webhook_url.setter
    def webhook_url(self, value: Optional[str]):
        self._data["webhook_url"] = value
    
    @property
    def obsidian_vault(self) -> str:
        path = self._data.get("obsidian_vault", "~/SynapseNotes")
        return os.path.expanduser(path)
    
    @obsidian_vault.setter
    def obsidian_vault(self, value: str):
        self._data["obsidian_vault"] = value
    
    @property
    def cache_hours(self) -> int:
        return self._data.get("cache_hours", 24)
    
    @cache_hours.setter
    def cache_hours(self, value: int):
        self._data["cache_hours"] = value
    
    @property
    def default_depth(self) -> int:
        return self._data.get("default_depth", 0)
    
    @default_depth.setter
    def default_depth(self, value: int):
        self._data["default_depth"] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value by key."""
        return self._data.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a config value by key."""
        self._data[key] = value


# Global config instance
_config_instance: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """Get or create the global config instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config(config_path)
    return _config_instance
