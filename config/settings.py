from pydantic import BaseModel, HttpUrl, Field
from typing import Dict, Optional
import yaml
import os
from pathlib import Path

class ServiceConfig(BaseModel):
    repo_url: HttpUrl
    compose_file: str
    service_name: str
    port_key: str
    uri_format: str
    env_vars: Dict[str, Optional[str]] = Field(default_factory=dict)
    defaults: Dict[str, Optional[str]] = Field(default_factory=dict)
    health_check: Optional[Dict[str, str]] = None

class AppConfig(BaseModel):
    services: Dict[str, ServiceConfig]
    base_dir: str = str(Path.home() / ".sin")
    wait_timeout: int = 30

def load_config(config_file: str = "services.yml") -> AppConfig:
    default_config_path = Path(__file__).parent / config_file
    config_path = os.getenv("SIN_CONFIG", str(default_config_path))
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, "r") as f:
        config_data = yaml.safe_load(f)
    
    return AppConfig(**config_data)