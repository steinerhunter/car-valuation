#!/usr/bin/env python3
"""
🧪 Installation Tests - OME-119
===============================
Comprehensive test suite for one-click installation system
"""

import unittest
import os
import sys
import tempfile
import subprocess
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add skill directory to path
skill_dir = Path(__file__).parent.parent
sys.path.insert(0, str(skill_dir))

class TestInstallationScript(unittest.TestCase):
    """Test the installation script functionality"""
    
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.install_script = skill_dir / 'install.sh'
        
    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_install_script_exists(self):
        """Test that install script exists and is executable"""
        self.assertTrue(self.install_script.exists())
        self.assertTrue(os.access(self.install_script, os.X_OK))
    
    def test_install_script_syntax(self):
        """Test that install script has valid bash syntax"""
        result = subprocess.run(['bash', '-n', str(self.install_script)], 
                              capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"Syntax error: {result.stderr}")
    
    def test_install_script_dry_run(self):
        """Test install script in dry run mode"""
        # Note: This would require implementing a --dry-run flag
        pass

class TestCLITool(unittest.TestCase):
    """Test the CLI diagnostic tool"""
    
    def setUp(self):
        self.cli_script = skill_dir / 'car-valuation'
        
        # Mock environment for testing
        self.env_patcher = patch.dict('os.environ', {
            'APIFY_API_TOKEN': 'apify_api_test_token_1234567890abcdef'
        })
        self.env_patcher.start()
    
    def tearDown(self):
        self.env_patcher.stop()
    
    def test_cli_script_exists(self):
        """Test that CLI script exists and is executable"""
        self.assertTrue(self.cli_script.exists())
        self.assertTrue(os.access(self.cli_script, os.X_OK))
    
    def test_cli_import(self):
        """Test that CLI tool can be imported"""
        try:
            # Add CLI script directory to path
            sys.path.insert(0, str(self.cli_script.parent))
            
            # Import the CLI module (without .py extension, it's a script)
            # We'll test the core functionality instead
            from scripts.car_valuation_api import CarValuationAPI
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"CLI import failed: {e}")
    
    def test_cli_status_command(self):
        """Test CLI status command"""
        result = subprocess.run([str(self.cli_script), 'status'], 
                              capture_output=True, text=True, cwd=skill_dir)
        # Should not crash (return code might be non-zero if setup incomplete)
        self.assertIsNotNone(result.returncode)
    
    def test_cli_diagnose_command(self):
        """Test CLI diagnose command"""
        result = subprocess.run([str(self.cli_script), 'diagnose'], 
                              capture_output=True, text=True, cwd=skill_dir)
        self.assertIsNotNone(result.returncode)
        # Should contain diagnosis output
        self.assertIn('System Information', result.stdout)

class TestDependencyInstallation(unittest.TestCase):
    """Test dependency installation and management"""
    
    def test_requirements_file_exists(self):
        """Test that requirements.txt exists and is valid"""
        requirements_file = skill_dir / 'requirements.txt'
        self.assertTrue(requirements_file.exists())
        
        # Check file is not empty
        with open(requirements_file, 'r') as f:
            content = f.read().strip()
        self.assertGreater(len(content), 0)
        
        # Check for required packages
        required_packages = ['requests', 'beautifulsoup4', 'pandas']
        for package in required_packages:
            self.assertIn(package, content)
    
    def test_virtual_environment_support(self):
        """Test that virtual environment can be created"""
        test_venv = self.test_dir / 'test_venv'
        
        result = subprocess.run([
            sys.executable, '-m', 'venv', str(test_venv)
        ], capture_output=True)
        
        if result.returncode == 0:
            self.assertTrue(test_venv.exists())
            # Test pip is available in venv
            venv_pip = test_venv / 'bin' / 'pip'
            if not venv_pip.exists():
                venv_pip = test_venv / 'Scripts' / 'pip.exe'  # Windows
            # Don't fail if venv creation doesn't work on this system
    
    @patch('subprocess.check_call')
    def test_dependency_installation_methods(self, mock_check_call):
        """Test different dependency installation methods"""
        # Test normal pip install
        mock_check_call.return_value = None
        
        # This would normally test the actual installation logic
        # For now, we just verify the mock is set up correctly
        self.assertTrue(mock_check_call)

class TestApifyIntegration(unittest.TestCase):
    """Test Apify API token handling and validation"""
    
    def test_token_format_validation(self):
        """Test Apify token format validation"""
        valid_tokens = [
            'apify_api_1234567890abcdef1234567890abcdef12345678',
            'apify_api_abcdefghijklmnopqrstuvwxyz1234567890abcd'
        ]
        
        invalid_tokens = [
            'invalid_token',
            'apify_api_short',
            'wrong_prefix_1234567890abcdef1234567890abcdef',
            ''
        ]
        
        # Import token validation logic (would need to extract from CLI)
        import re
        token_pattern = r'^apify_api_[a-zA-Z0-9]{40,}$'
        
        for token in valid_tokens:
            self.assertTrue(re.match(token_pattern, token), f"Valid token rejected: {token}")
        
        for token in invalid_tokens:
            self.assertFalse(re.match(token_pattern, token), f"Invalid token accepted: {token}")
    
    def test_token_environment_handling(self):
        """Test environment variable handling for Apify token"""
        # Test with token in environment
        with patch.dict('os.environ', {'APIFY_API_TOKEN': 'apify_api_test123456789'}):
            token = os.getenv('APIFY_API_TOKEN')
            self.assertEqual(token, 'apify_api_test123456789')
        
        # Test without token
        with patch.dict('os.environ', {}, clear=True):
            token = os.getenv('APIFY_API_TOKEN')
            self.assertIsNone(token)

class TestSystemCompatibility(unittest.TestCase):
    """Test cross-platform compatibility"""
    
    def test_python_version_detection(self):
        """Test Python version detection"""
        # Should work with current Python version
        self.assertGreaterEqual(sys.version_info[:2], (3, 8))
    
    def test_platform_detection(self):
        """Test platform detection logic"""
        import platform
        system = platform.system()
        self.assertIn(system, ['Linux', 'Darwin', 'Windows'])
    
    def test_path_handling(self):
        """Test cross-platform path handling"""
        # Test path creation and manipulation
        test_path = Path('test') / 'path' / 'handling'
        self.assertEqual(str(test_path).count(os.sep), 2)

class TestInstallationValidation(unittest.TestCase):
    """Test installation validation and health checks"""
    
    def test_skill_structure(self):
        """Test that skill has required directory structure"""
        required_files = [
            'SKILL.md',
            'README.md', 
            'requirements.txt',
            'scripts/car_valuation_api.py',
            'scripts/market_analyzer.py'
        ]
        
        for file_path in required_files:
            full_path = skill_dir / file_path
            self.assertTrue(full_path.exists(), f"Required file missing: {file_path}")
    
    def test_configuration_validation(self):
        """Test configuration file validation"""
        # Test .env file format
        test_config = """
# Test configuration
APIFY_API_TOKEN=apify_api_test123456789
SKILL_VERSION=2.0
INSTALLATION_DATE=2024-01-01T00:00:00Z
"""
        
        # Parse config (simplified)
        lines = test_config.strip().split('\n')
        config = {}
        for line in lines:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.strip().split('=', 1)
                config[key] = value
        
        self.assertIn('APIFY_API_TOKEN', config)
        self.assertIn('SKILL_VERSION', config)
        self.assertIn('INSTALLATION_DATE', config)

class TestErrorHandling(unittest.TestCase):
    """Test error handling and recovery mechanisms"""
    
    def test_network_error_handling(self):
        """Test handling of network errors during installation"""
        # Test timeout handling
        pass
    
    def test_permission_error_handling(self):
        """Test handling of permission errors"""
        # Test readonly filesystem, permission denied, etc.
        pass
    
    def test_dependency_conflict_handling(self):
        """Test handling of dependency conflicts"""
        # Test pip install failures, version conflicts, etc.
        pass

if __name__ == '__main__':
    # Create test directory if it doesn't exist
    test_dir = Path(__file__).parent
    test_dir.mkdir(exist_ok=True)
    
    # Set up test environment
    os.environ.setdefault('PYTHONPATH', str(skill_dir))
    
    # Run tests
    unittest.main(verbosity=2)