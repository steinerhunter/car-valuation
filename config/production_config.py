#!/usr/bin/env python3
"""
Production Configuration Management for OME-89 Car Valuation System
Addresses configuration management gaps identified by reviewers
"""

import os
import json
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class APIConfig:
    """API configuration settings"""
    base_url: str = "https://api.apify.com/v2"
    scraper_id: str = "swerve~yad2-vehicles"
    timeout_seconds: int = 30
    max_concurrent_requests: int = 3
    rate_limit_delay: float = 2.0
    max_retries: int = 3
    cost_per_1000_results: float = 5.0

@dataclass
class SecurityConfig:
    """Security configuration settings"""
    mask_sensitive_logs: bool = True
    token_validation: bool = True
    input_sanitization: bool = True
    log_api_requests: bool = False  # Prevent token exposure
    max_log_size_mb: int = 100
    log_rotation_count: int = 5

@dataclass
class DataConfig:
    """Data processing configuration"""
    min_price_threshold: int = 10000
    max_price_threshold: int = 500000
    min_year: int = 2010
    max_year: int = 2025
    min_km: int = 0
    max_km: int = 500000
    quality_score_threshold: float = 0.8

@dataclass
class PathsConfig:
    """File and directory paths configuration"""
    base_dir: str = "."
    logs_dir: str = "logs"
    data_dir: str = "data" 
    config_dir: str = "config"
    cache_dir: str = "cache"
    reports_dir: str = "reports"
    backup_dir: str = "backups"

@dataclass
class MonitoringConfig:
    """Monitoring and health check configuration"""
    health_check_interval: int = 60
    metrics_retention_days: int = 30
    alert_thresholds: Dict[str, float] = None
    enable_performance_tracking: bool = True
    log_level: str = "INFO"

class ConfigurationManager:
    """Centralized configuration management"""
    
    def __init__(self, config_file: Optional[str] = None, environment: str = "development"):
        self.environment = environment
        self.config_file = config_file or self._get_default_config_file()
        self.config = self._load_configuration()
    
    def _get_default_config_file(self) -> str:
        """Get default configuration file based on environment"""
        config_files = {
            "development": "config/development.yaml",
            "staging": "config/staging.yaml", 
            "production": "config/production.yaml"
        }
        return config_files.get(self.environment, "config/default.yaml")
    
    def _load_configuration(self) -> Dict[str, Any]:
        """Load configuration from file with environment overrides"""
        
        # Default configuration
        default_config = self._get_default_configuration()
        
        # Load from file if exists
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                        file_config = yaml.safe_load(f)
                    else:
                        file_config = json.load(f)
                
                # Merge configurations
                default_config.update(file_config)
            except Exception as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")
        
        # Override with environment variables
        self._apply_environment_overrides(default_config)
        
        return default_config
    
    def _get_default_configuration(self) -> Dict[str, Any]:
        """Get default configuration values"""
        
        # Default alert thresholds
        default_thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 80.0,
            "disk_percent": 90.0,
            "response_time_ms": 5000.0
        }
        
        return {
            "api": asdict(APIConfig()),
            "security": asdict(SecurityConfig()),
            "data": asdict(DataConfig()),
            "paths": asdict(PathsConfig()),
            "monitoring": asdict(MonitoringConfig(alert_thresholds=default_thresholds))
        }
    
    def _apply_environment_overrides(self, config: Dict[str, Any]):
        """Apply environment variable overrides"""
        
        # API configuration overrides
        if os.getenv('APIFY_API_TOKEN'):
            config['api']['token'] = os.getenv('APIFY_API_TOKEN')
        
        if os.getenv('API_TIMEOUT'):
            config['api']['timeout_seconds'] = int(os.getenv('API_TIMEOUT'))
        
        if os.getenv('MAX_CONCURRENT_REQUESTS'):
            config['api']['max_concurrent_requests'] = int(os.getenv('MAX_CONCURRENT_REQUESTS'))
        
        # Paths overrides
        if os.getenv('CAR_VALUATION_BASE_DIR'):
            config['paths']['base_dir'] = os.getenv('CAR_VALUATION_BASE_DIR')
        
        if os.getenv('LOGS_DIR'):
            config['paths']['logs_dir'] = os.getenv('LOGS_DIR')
        
        if os.getenv('DATA_DIR'):
            config['paths']['data_dir'] = os.getenv('DATA_DIR')
        
        # Monitoring overrides
        if os.getenv('LOG_LEVEL'):
            config['monitoring']['log_level'] = os.getenv('LOG_LEVEL')
        
        if os.getenv('ENABLE_PERFORMANCE_TRACKING'):
            config['monitoring']['enable_performance_tracking'] = os.getenv('ENABLE_PERFORMANCE_TRACKING').lower() == 'true'
    
    def get_api_config(self) -> APIConfig:
        """Get API configuration"""
        api_dict = self.config.get('api', {})
        return APIConfig(**api_dict)
    
    def get_security_config(self) -> SecurityConfig:
        """Get security configuration"""
        security_dict = self.config.get('security', {})
        return SecurityConfig(**security_dict)
    
    def get_data_config(self) -> DataConfig:
        """Get data configuration"""
        data_dict = self.config.get('data', {})
        return DataConfig(**data_dict)
    
    def get_paths_config(self) -> PathsConfig:
        """Get paths configuration"""
        paths_dict = self.config.get('paths', {})
        
        # Resolve paths relative to base directory
        base_dir = Path(paths_dict.get('base_dir', '.'))
        resolved_paths = {}
        
        for key, path in paths_dict.items():
            if key != 'base_dir':
                resolved_paths[key] = str(base_dir / path)
            else:
                resolved_paths[key] = str(base_dir)
        
        return PathsConfig(**resolved_paths)
    
    def get_monitoring_config(self) -> MonitoringConfig:
        """Get monitoring configuration"""
        monitoring_dict = self.config.get('monitoring', {})
        return MonitoringConfig(**monitoring_dict)
    
    def ensure_directories_exist(self):
        """Create required directories if they don't exist"""
        paths = self.get_paths_config()
        
        required_dirs = [
            paths.logs_dir,
            paths.data_dir,
            paths.cache_dir,
            paths.reports_dir,
            paths.backup_dir
        ]
        
        for directory in required_dirs:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Ensured directory exists: {directory}")
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate current configuration and return issues"""
        issues = []
        warnings = []
        
        # Check API configuration
        api_config = self.get_api_config()
        if not hasattr(api_config, 'token') or not api_config.token:
            issues.append("Missing API token (APIFY_API_TOKEN environment variable)")
        
        if api_config.timeout_seconds < 10:
            warnings.append("API timeout is very low (<10 seconds)")
        
        if api_config.max_concurrent_requests > 10:
            warnings.append("High concurrent requests may hit rate limits")
        
        # Check paths configuration
        paths = self.get_paths_config()
        try:
            # Check if base directory is writable
            test_file = Path(paths.base_dir) / "test_write.tmp"
            test_file.write_text("test")
            test_file.unlink()
        except Exception:
            issues.append(f"Base directory is not writable: {paths.base_dir}")
        
        # Check data configuration
        data_config = self.get_data_config()
        if data_config.min_price_threshold >= data_config.max_price_threshold:
            issues.append("Invalid price thresholds: min >= max")
        
        if data_config.min_year >= data_config.max_year:
            issues.append("Invalid year range: min >= max")
        
        # Check monitoring configuration
        monitoring = self.get_monitoring_config()
        if monitoring.log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            issues.append(f"Invalid log level: {monitoring.log_level}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def save_current_configuration(self, output_file: str):
        """Save current configuration to file"""
        try:
            with open(output_file, 'w') as f:
                if output_file.endswith('.yaml') or output_file.endswith('.yml'):
                    yaml.safe_dump(self.config, f, default_flow_style=False)
                else:
                    json.dump(self.config, f, indent=2)
            
            print(f"✅ Configuration saved to: {output_file}")
        except Exception as e:
            print(f"❌ Failed to save configuration: {e}")

def create_production_config_files():
    """Create production configuration files"""
    
    # Production configuration
    production_config = {
        "api": {
            "base_url": "https://api.apify.com/v2",
            "scraper_id": "swerve~yad2-vehicles", 
            "timeout_seconds": 60,
            "max_concurrent_requests": 2,  # Conservative for production
            "rate_limit_delay": 3.0,       # Slower for production stability
            "max_retries": 5
        },
        "security": {
            "mask_sensitive_logs": True,
            "token_validation": True,
            "input_sanitization": True,
            "log_api_requests": False,
            "max_log_size_mb": 50,
            "log_rotation_count": 10
        },
        "data": {
            "min_price_threshold": 5000,
            "max_price_threshold": 1000000,
            "quality_score_threshold": 0.9  # Higher quality for production
        },
        "paths": {
            "base_dir": "/app",
            "logs_dir": "logs",
            "data_dir": "data",
            "cache_dir": "cache",
            "reports_dir": "reports",
            "backup_dir": "backups"
        },
        "monitoring": {
            "health_check_interval": 30,
            "metrics_retention_days": 90,
            "enable_performance_tracking": True,
            "log_level": "INFO",
            "alert_thresholds": {
                "cpu_percent": 75.0,
                "memory_percent": 75.0,
                "disk_percent": 85.0,
                "response_time_ms": 10000.0
            }
        }
    }
    
    # Development configuration
    development_config = {
        "api": {
            "timeout_seconds": 30,
            "max_concurrent_requests": 1,
            "rate_limit_delay": 1.0
        },
        "security": {
            "log_api_requests": True,  # More verbose in development
            "max_log_size_mb": 10
        },
        "monitoring": {
            "log_level": "DEBUG",
            "enable_performance_tracking": True
        }
    }
    
    # Create config directory
    os.makedirs("config", exist_ok=True)
    
    # Save configurations
    with open("config/production.yaml", "w") as f:
        yaml.safe_dump(production_config, f, default_flow_style=False)
    
    with open("config/development.yaml", "w") as f:
        yaml.safe_dump(development_config, f, default_flow_style=False)
    
    print("✅ Created production.yaml and development.yaml configuration files")

def test_configuration_management():
    """Test configuration management system"""
    print("⚙️ Testing Configuration Management")
    print("=" * 40)
    
    # Create sample config files
    create_production_config_files()
    
    # Test development configuration
    dev_config = ConfigurationManager(environment="development")
    dev_validation = dev_config.validate_configuration()
    print(f"✅ Development config valid: {dev_validation['valid']}")
    
    if dev_validation['warnings']:
        print(f"⚠️ Development warnings: {len(dev_validation['warnings'])}")
    
    # Test production configuration
    prod_config = ConfigurationManager(environment="production")
    prod_validation = prod_config.validate_configuration()
    print(f"✅ Production config valid: {prod_validation['valid']}")
    
    # Test directory creation
    prod_config.ensure_directories_exist()
    
    # Test configuration access
    api_config = prod_config.get_api_config()
    print(f"✅ API timeout: {api_config.timeout_seconds}s")
    
    paths_config = prod_config.get_paths_config()
    print(f"✅ Logs directory: {paths_config.logs_dir}")
    
    monitoring_config = prod_config.get_monitoring_config()
    print(f"✅ Log level: {monitoring_config.log_level}")
    
    return prod_config

if __name__ == "__main__":
    test_configuration_management()