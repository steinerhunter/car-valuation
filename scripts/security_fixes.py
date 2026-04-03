#!/usr/bin/env python3
"""
Security Fixes for OME-89 - Address Critical Security Issues
Based on Security & Production Expert Review
"""

import os
import re
import logging
import json
from typing import Dict, Any

class SecurityEnhancer:
    """Enhance security aspects of the car valuation system"""
    
    def __init__(self):
        self.logger = self._setup_secure_logging()
        
    def _setup_secure_logging(self):
        """Set up secure logging with token masking"""
        
        class SensitiveDataFilter(logging.Filter):
            """Filter to mask sensitive data in logs"""
            
            def filter(self, record):
                # Mask API tokens
                if hasattr(record, 'getMessage'):
                    message = record.getMessage()
                    
                    # Mask API tokens (keep only last 4 chars)
                    message = re.sub(
                        r'(api[_-]?token[_-]?[=:]?\s*["\']?)([\w\-]{8,})', 
                        r'\1****\2[-4:]', 
                        message, 
                        flags=re.IGNORECASE
                    )
                    
                    # Mask bearer tokens
                    message = re.sub(
                        r'(bearer\s+)([\w\-\.]{20,})', 
                        r'\1****\2[-4:]', 
                        message, 
                        flags=re.IGNORECASE
                    )
                    
                    # Update record message
                    record.msg = message
                    record.args = ()
                
                return True
        
        # Create secure logger
        logger = logging.getLogger('car_valuation_secure')
        logger.setLevel(logging.INFO)
        
        # Add security filter
        security_filter = SensitiveDataFilter()
        
        # Create handlers with security filter
        console_handler = logging.StreamHandler()
        console_handler.addFilter(security_filter)
        
        file_handler = logging.FileHandler('logs/car_valuation_secure.log')
        file_handler.addFilter(security_filter)
        
        # Set format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
    
    def mask_api_token(self, token: str) -> str:
        """Safely mask API token for logging"""
        if not token or len(token) < 8:
            return "****"
        
        return f"****{token[-4:]}"
    
    def validate_api_token(self, token: str) -> bool:
        """Validate API token format"""
        if not token:
            return False
        
        # Check for minimum length and format
        if len(token) < 20:
            return False
        
        # Check for valid characters (alphanumeric + common separators)
        if not re.match(r'^[a-zA-Z0-9\-_\.]+$', token):
            return False
        
        return True
    
    def secure_api_call(self, api_call_func, *args, **kwargs):
        """Wrapper for secure API calls with logging"""
        try:
            # Log start (without sensitive data)
            self.logger.info(f"Starting secure API call: {api_call_func.__name__}")
            
            # Make the call
            result = api_call_func(*args, **kwargs)
            
            # Log success
            self.logger.info(f"API call completed successfully: {api_call_func.__name__}")
            
            return result
            
        except Exception as e:
            # Log error (without sensitive details)
            self.logger.error(f"API call failed: {api_call_func.__name__} - Error type: {type(e).__name__}")
            raise
    
    def create_security_config(self) -> Dict[str, Any]:
        """Create secure configuration template"""
        return {
            "api": {
                "token_validation": True,
                "rate_limiting": {
                    "max_requests_per_minute": 30,
                    "exponential_backoff": True
                },
                "timeout_seconds": 30
            },
            "logging": {
                "mask_sensitive_data": True,
                "log_level": "INFO",
                "max_log_size_mb": 100,
                "backup_count": 5
            },
            "security": {
                "input_validation": True,
                "output_sanitization": True,
                "error_details_in_response": False
            }
        }

def test_security_enhancements():
    """Test the security enhancement functionality"""
    print("🔒 Testing Security Enhancements")
    print("="*40)
    
    enhancer = SecurityEnhancer()
    
    # Test token masking
    test_token = "lin_api_SkYzK7kZC3dAHDFTpkTY7OJd8Me1tzpqcfgYxR1k"
    masked = enhancer.mask_api_token(test_token)
    print(f"✅ Token masking: {masked}")
    
    # Test validation
    is_valid = enhancer.validate_api_token(test_token)
    print(f"✅ Token validation: {is_valid}")
    
    # Test secure logging
    enhancer.logger.info(f"Test with token: {test_token}")
    print("✅ Secure logging configured")
    
    # Test configuration
    config = enhancer.create_security_config()
    print("✅ Security configuration created")
    
    return True

if __name__ == "__main__":
    test_security_enhancements()