#!/usr/bin/env python3
"""
Universal Workflow Manager
=========================

Enterprise-grade development workflow manager that works with ANY project type:
- Web applications (React, Vue, Angular, Node.js)
- Backend APIs (Python, Go, Rust, Java)
- Mobile apps (React Native, Flutter)
- AI/ML projects (Python, Jupyter, PyTorch)
- DevOps projects (Terraform, Kubernetes)
- Desktop applications (Electron, Tauri)

Features:
- Project-type detection and optimization
- Universal logging and monitoring
- Automated PR creation with context
- Review agent spawning with project-specific instructions
- Performance tracking across different tech stacks
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import subprocess

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from logging_system import HeinrichLogger, get_logger, track_operation
except ImportError:
    # Fallback to basic logging if logging_system not available
    class BasicLogger:
        def info(self, msg, **kwargs): print(f"INFO: {msg}")
        def error(self, msg, **kwargs): print(f"ERROR: {msg}")
        def warning(self, msg, **kwargs): print(f"WARNING: {msg}")
        def operation(self, name, component=None, **kwargs):
            from contextlib import contextmanager
            @contextmanager
            def op():
                print(f"Starting {name}")
                yield
                print(f"Completed {name}")
            return op()
        def log_workflow_step(self, *args, **kwargs): pass
        def log_pr_event(self, *args, **kwargs): pass
        def shutdown(self): pass
    
    def get_logger(name="universal"):
        return BasicLogger()

class UniversalWorkflow:
    """
    Universal development workflow manager for ANY project type
    """
    
    def __init__(self, project_path: str = None):
        self.project_path = Path(project_path or os.getcwd()).resolve()
        self.project_name = self.project_path.name
        
        # Load project configuration
        self.config = self._load_project_config()
        self.project_type = self.config.get("project", {}).get("type", "general")
        
        # Setup logging
        logs_dir = self.project_path / ".enterprise-logs"
        logs_dir.mkdir(exist_ok=True)
        
        self.logger = get_logger(f"workflow_{self.project_name}")
        
        # Workflow state
        self.current_workflow = None
        self.workflow_history = []
        
        self.logger.info(f"🎩 Universal Workflow Manager initialized for {self.project_name}", extra={
            'component': 'workflow_manager',
            'operation': 'init',
            'metadata': {
                'project_type': self.project_type,
                'project_path': str(self.project_path)
            }
        })
    
    def _load_project_config(self) -> Dict[str, Any]:
        """Load project configuration"""
        config_file = self.project_path / ".enterprise-config" / "enterprise.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Could not load config: {e}")
        
        # Return default config
        return {
            "project": {
                "name": self.project_name,
                "type": self._detect_project_type(),
                "path": str(self.project_path)
            },
            "workflow": {
                "auto_pr_creation": True,
                "review_agent_spawning": True,
                "performance_thresholds": {
                    "max_response_time_ms": 2000,
                    "max_memory_mb": 1000
                }
            }
        }
    
    def _detect_project_type(self) -> str:
        """Auto-detect project type"""
        files = [f.name.lower() for f in self.project_path.glob("*")]
        
        if "package.json" in files:
            return "nodejs"
        elif "requirements.txt" in files or "pyproject.toml" in files:
            return "python" 
        elif "cargo.toml" in files:
            return "rust"
        elif "go.mod" in files:
            return "golang"
        elif "pubspec.yaml" in files:
            return "flutter"
        else:
            return "general"
    
    def start_feature_development(self, feature_name: str, description: str, priority: str = "medium") -> str:
        """Start new feature development with project-specific optimization"""
        workflow_id = f"{self.project_type}_{feature_name}_{int(time.time())}"
        
        with self.logger.operation("start_feature_development", "workflow",
                                 feature_name=feature_name, project_type=self.project_type) as op_id:
            
            self.current_workflow = {
                'workflow_id': workflow_id,
                'feature_name': feature_name,
                'description': description,
                'priority': priority,
                'project_type': self.project_type,
                'started_at': datetime.now().isoformat(),
                'phase': 'development',
                'correlation_id': op_id,
                'project_path': str(self.project_path)
            }
            
            self.logger.log_workflow_step(
                workflow_id, "start_development", "initiated",
                feature_name=feature_name,
                project_type=self.project_type,
                priority=priority
            )
            
            # Project-specific setup
            self._setup_project_environment()
            
            # Create feature branch if git repo exists
            if self._is_git_repo():
                try:
                    branch_name = self._create_feature_branch(feature_name)
                    self.current_workflow['branch_name'] = branch_name
                    
                    self.logger.info(f"🌿 Created feature branch: {branch_name}", extra={
                        'component': 'git',
                        'operation': 'create_branch',
                        'workflow_id': workflow_id,
                        'metadata': {'branch_name': branch_name}
                    })
                except Exception as e:
                    self.logger.warning(f"Could not create git branch: {e}", extra={
                        'component': 'git',
                        'workflow_id': workflow_id
                    })
            
            self.logger.info(f"🚀 Started {self.project_type} feature development: {feature_name}", extra={
                'component': 'workflow',
                'operation': 'feature_started',
                'workflow_id': workflow_id,
                'metadata': {
                    'feature_name': feature_name,
                    'project_type': self.project_type,
                    'priority': priority
                }
            })
            
            return workflow_id
    
    def _setup_project_environment(self):
        """Setup project-specific development environment"""
        setup_actions = {
            "nodejs": self._setup_nodejs_env,
            "python": self._setup_python_env,
            "rust": self._setup_rust_env,
            "golang": self._setup_golang_env,
            "flutter": self._setup_flutter_env
        }
        
        setup_func = setup_actions.get(self.project_type, self._setup_general_env)
        setup_func()
    
    def _setup_nodejs_env(self):
        """Setup Node.js development environment"""
        self.logger.info("🔧 Setting up Node.js environment", extra={'component': 'env_setup'})
        
        # Check if node_modules exists
        if not (self.project_path / "node_modules").exists():
            self.logger.info("📦 Installing Node.js dependencies", extra={'component': 'env_setup'})
            # Could run npm install here if needed
    
    def _setup_python_env(self):
        """Setup Python development environment"""
        self.logger.info("🐍 Setting up Python environment", extra={'component': 'env_setup'})
        
        # Check for virtual environment
        venv_paths = [
            self.project_path / "venv",
            self.project_path / ".venv",
            self.project_path / "env"
        ]
        
        has_venv = any(venv.exists() for venv in venv_paths)
        if not has_venv:
            self.logger.warning("🐍 No virtual environment detected", extra={'component': 'env_setup'})
    
    def _setup_rust_env(self):
        """Setup Rust development environment"""
        self.logger.info("🦀 Setting up Rust environment", extra={'component': 'env_setup'})
    
    def _setup_golang_env(self):
        """Setup Go development environment"""  
        self.logger.info("🐹 Setting up Go environment", extra={'component': 'env_setup'})
    
    def _setup_flutter_env(self):
        """Setup Flutter development environment"""
        self.logger.info("🎯 Setting up Flutter environment", extra={'component': 'env_setup'})
    
    def _setup_general_env(self):
        """Setup general development environment"""
        self.logger.info("⚙️ Setting up general environment", extra={'component': 'env_setup'})
    
    def simulate_development_work(self, files: List[str], duration_seconds: float = 2.0):
        """Simulate development work for demo purposes"""
        if not self.current_workflow:
            raise ValueError("No active workflow")
        
        workflow_id = self.current_workflow['workflow_id']
        
        with self.logger.operation("simulate_development", "development", workflow_id=workflow_id):
            self.logger.info(f"📝 Simulating development work on {len(files)} files", extra={
                'component': 'development',
                'operation': 'simulate_work',
                'workflow_id': workflow_id,
                'metadata': {'files': files}
            })
            
            # Simulate work for each file
            for file_path in files:
                self.logger.info(f"✏️ Working on: {file_path}", extra={
                    'component': 'development',
                    'operation': 'file_work',
                    'workflow_id': workflow_id,
                    'metadata': {'file_path': file_path}
                })
                time.sleep(duration_seconds / len(files))
            
            self.logger.info("✅ Development work simulation completed", extra={
                'component': 'development',
                'operation': 'work_completed',
                'workflow_id': workflow_id
            })
    
    def commit_changes(self, commit_message: str, files: List[str] = None) -> bool:
        """Commit changes with enhanced logging"""
        if not self.current_workflow:
            raise ValueError("No active workflow")
        
        workflow_id = self.current_workflow['workflow_id']
        
        with self.logger.operation("commit_changes", "git", workflow_id=workflow_id):
            if not self._is_git_repo():
                self.logger.warning("Not a git repository - skipping commit", extra={
                    'component': 'git',
                    'workflow_id': workflow_id
                })
                return False
            
            try:
                # Enhanced commit message with workflow context
                enhanced_message = f"""{commit_message}

🤖 Universal Workflow: {workflow_id}
📋 Project: {self.project_name} ({self.project_type})
🔧 Feature: {self.current_workflow['feature_name']}
⏰ Timestamp: {datetime.now().isoformat()}

Co-authored-by: Heinrich AI <heinrich@heinrich.bot>"""
                
                # Stage files
                if files:
                    for file in files:
                        subprocess.run(["git", "add", file], cwd=self.project_path, check=True)
                else:
                    subprocess.run(["git", "add", "."], cwd=self.project_path, check=True)
                
                # Commit
                subprocess.run(["git", "commit", "-m", enhanced_message], cwd=self.project_path, check=True)
                
                self.logger.log_workflow_step(
                    workflow_id, "commit", "completed",
                    commit_message=commit_message,
                    files_count=len(files) if files else "all"
                )
                
                # Update workflow state
                self.current_workflow['phase'] = 'committed'
                self.current_workflow['last_commit'] = {
                    'message': commit_message,
                    'timestamp': datetime.now().isoformat(),
                    'files': files
                }
                
                self.logger.info(f"✅ Committed changes: {commit_message}", extra={
                    'component': 'git',
                    'operation': 'commit_success',
                    'workflow_id': workflow_id
                })
                
                return True
                
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Git commit failed: {e}", extra={
                    'component': 'git',
                    'operation': 'commit_failed',
                    'workflow_id': workflow_id
                })
                return False
    
    def create_pr_with_review(self, pr_title: str = None, pr_description: str = None) -> Optional[str]:
        """Create PR and spawn review agent (GitHub integration)"""
        if not self.current_workflow:
            raise ValueError("No active workflow")
        
        workflow_id = self.current_workflow['workflow_id']
        
        with self.logger.operation("create_pr_with_review", "pr_workflow", workflow_id=workflow_id):
            if not self._has_github_remote():
                self.logger.warning("No GitHub remote found - skipping PR creation", extra={
                    'component': 'pr_workflow',
                    'workflow_id': workflow_id
                })
                return None
            
            # Generate PR details
            if not pr_title:
                pr_title = f"✨ {self.current_workflow['feature_name'].replace('-', ' ').title()}"
            
            if not pr_description:
                pr_description = self._generate_project_pr_description()
            
            try:
                # Push branch if exists
                if 'branch_name' in self.current_workflow:
                    subprocess.run([
                        "git", "push", "-u", "origin", self.current_workflow['branch_name']
                    ], cwd=self.project_path, check=True)
                
                # Try to create PR using gh CLI
                pr_cmd = [
                    "gh", "pr", "create",
                    "--title", pr_title,
                    "--body", pr_description,
                    "--head", self.current_workflow.get('branch_name', 'main'),
                    "--base", "main"
                ]
                
                result = subprocess.run(pr_cmd, cwd=self.project_path, 
                                      capture_output=True, text=True, check=True)
                pr_url = result.stdout.strip()
                
                self.current_workflow['pr_url'] = pr_url
                self.current_workflow['phase'] = 'pr_created'
                
                self.logger.log_pr_event(pr_url, "created",
                                       workflow_id=workflow_id,
                                       project_type=self.project_type)
                
                # Spawn review agent
                self._spawn_project_review_agent(pr_url)
                
                self.logger.info(f"✅ PR created: {pr_url}", extra={
                    'component': 'pr_workflow',
                    'operation': 'pr_created',
                    'workflow_id': workflow_id,
                    'metadata': {'pr_url': pr_url}
                })
                
                return pr_url
                
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                self.logger.warning(f"PR creation failed: {e}", extra={
                    'component': 'pr_workflow',
                    'workflow_id': workflow_id
                })
                
                # Provide manual instructions
                print(f"💡 Create PR manually at GitHub and then spawn review agent")
                return None
    
    def _generate_project_pr_description(self) -> str:
        """Generate project-type specific PR description"""
        base_description = f"""{self.current_workflow.get('description', '')}

## 🎩 Universal Enterprise Workflow

**🤖 Development Agent:** Heinrich AI  
**📋 Project Type:** {self.project_type}  
**🌿 Feature:** {self.current_workflow['feature_name']}  
**⚡ Priority:** {self.current_workflow['priority']}  
**⏰ Started:** {self.current_workflow['started_at']}  

## 🔍 {self.project_type.title()} Project Review Requirements

{self._get_project_review_requirements()}

## 🤖 Review Agent Instructions

**📋 Mission:** Comprehensive {self.project_type} project analysis

**🎯 Focus Areas:**
{self._get_project_focus_areas()}

**📊 Quality Standards:**
{self._get_project_quality_standards()}

---
**🎩 Universal Enterprise Workflow for {self.project_type} projects**"""
        
        return base_description
    
    def _get_project_review_requirements(self) -> str:
        """Get project-specific review requirements"""
        requirements = {
            "nodejs": """
### Node.js Specific Validation
- [ ] **Dependencies**: No unnecessary packages, secure versions
- [ ] **Performance**: Efficient async/await usage, no blocking operations
- [ ] **Security**: No hardcoded secrets, proper input validation
- [ ] **Testing**: Jest tests for new functionality
- [ ] **Code Style**: ESLint compliance, consistent formatting
""",
            "python": """
### Python Specific Validation  
- [ ] **Code Quality**: PEP 8 compliance, type hints where appropriate
- [ ] **Performance**: Efficient algorithms, proper resource management
- [ ] **Security**: No SQL injection, proper input sanitization
- [ ] **Testing**: pytest coverage for new functionality
- [ ] **Dependencies**: requirements.txt updated, secure versions
""",
            "rust": """
### Rust Specific Validation
- [ ] **Safety**: Memory safety guaranteed, no unsafe blocks without justification
- [ ] **Performance**: Optimal ownership patterns, minimal allocations
- [ ] **Error Handling**: Proper Result/Option usage, informative errors  
- [ ] **Testing**: Unit tests and doc tests for public APIs
- [ ] **Dependencies**: Minimal and well-maintained crates
""",
            "flutter": """
### Flutter Specific Validation
- [ ] **Performance**: Efficient widget builds, minimal rebuilds
- [ ] **UI/UX**: Material Design compliance, accessibility support
- [ ] **State Management**: Proper state management patterns
- [ ] **Testing**: Widget tests for UI components
- [ ] **Platform Support**: iOS and Android compatibility
"""
        }
        
        return requirements.get(self.project_type, """
### General Project Validation
- [ ] **Code Quality**: Clean, readable, well-documented code
- [ ] **Performance**: Efficient algorithms and resource usage
- [ ] **Security**: No vulnerabilities, secure coding practices
- [ ] **Testing**: Appropriate test coverage for new functionality
- [ ] **Documentation**: Clear documentation for public interfaces
""")
    
    def _get_project_focus_areas(self) -> str:
        """Get project-specific focus areas for review"""
        focus_areas = {
            "nodejs": """
1. **Async Patterns** - Proper Promise/async-await usage
2. **Security** - Express security middleware, input validation
3. **Performance** - Event loop optimization, memory usage
4. **Dependencies** - Package security, version management
5. **API Design** - RESTful patterns, error handling
""",
            "python": """
1. **Code Architecture** - Clean separation, SOLID principles
2. **Performance** - Algorithm efficiency, memory usage
3. **Security** - SQLAlchemy security, input validation
4. **Testing** - pytest patterns, mocking strategies
5. **Dependencies** - Virtual environment, security updates
""",
            "rust": """
1. **Memory Safety** - Ownership patterns, lifetime management
2. **Performance** - Zero-cost abstractions, optimal algorithms
3. **Error Handling** - Result patterns, error propagation
4. **Concurrency** - Safe concurrent patterns, async usage
5. **API Design** - Ergonomic interfaces, documentation
"""
        }
        
        return focus_areas.get(self.project_type, """
1. **Code Quality** - Architecture, readability, maintainability
2. **Performance** - Efficiency, resource usage, scalability
3. **Security** - Vulnerability assessment, secure patterns
4. **Testing** - Coverage, test quality, edge cases
5. **Documentation** - Clarity, completeness, examples
""")
    
    def _get_project_quality_standards(self) -> str:
        """Get project-specific quality standards"""
        standards = {
            "nodejs": """
- Functions under 20 lines, modules under 200 lines
- 100% async/await (no callbacks), proper error handling
- ESLint score 9.0+, Prettier formatting
- 80%+ test coverage with meaningful tests
- No security vulnerabilities (npm audit clean)
""",
            "python": """
- Functions under 30 lines, classes focused and cohesive
- Type hints for public interfaces, PEP 8 compliance
- Pylint score 8.0+, Black formatting
- 85%+ test coverage with pytest
- No security issues (safety check clean)
""",
            "rust": """
- Functions focused and single-purpose, minimal unsafe
- Comprehensive error handling with Result types
- Clippy warnings addressed, rustfmt formatting
- Doc tests for all public APIs, unit test coverage
- Cargo audit clean, dependency analysis
"""
        }
        
        return standards.get(self.project_type, """
- Clear, focused functions and clean architecture
- Comprehensive error handling and input validation
- Consistent code style and formatting
- Adequate test coverage for critical paths
- No known security vulnerabilities
""")
    
    def _spawn_project_review_agent(self, pr_url: str):
        """Spawn project-specific review agent"""
        self.logger.info(f"🤖 Spawning {self.project_type} review agent for {pr_url}", extra={
            'component': 'review_agent',
            'operation': 'spawn_agent',
            'workflow_id': self.current_workflow['workflow_id'],
            'metadata': {
                'pr_url': pr_url,
                'project_type': self.project_type
            }
        })
        
        # This would integrate with the actual agent spawning system
        # For now, just log the intention
        print(f"🤖 Review agent would be spawned for {self.project_type} project: {pr_url}")
    
    def test_alert_system(self):
        """Generate test alerts for demo purposes"""
        if not hasattr(self, 'logger'):
            return
        
        self.logger.info("🧪 Testing alert system", extra={'component': 'testing'})
        
        # Generate different types of test alerts
        test_alerts = [
            ("info", "Test info message for demo"),
            ("warning", "Test warning - high memory usage simulation"),
            ("error", "Test error - simulated API failure")
        ]
        
        for level, message in test_alerts:
            getattr(self.logger, level)(message, extra={
                'component': 'demo',
                'operation': 'test_alert',
                'workflow_id': self.current_workflow.get('workflow_id') if self.current_workflow else None
            })
            time.sleep(0.5)
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive workflow report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "project": {
                "name": self.project_name,
                "type": self.project_type,
                "path": str(self.project_path)
            },
            "workflow": self.current_workflow,
            "development_time_minutes": self._calculate_development_time(),
            "operations_count": len(self.workflow_history),
            "alerts_count": 3  # Demo value
        }
        
        # Save report
        reports_dir = self.project_path / ".enterprise-logs" / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / f"workflow_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"📊 Generated workflow report: {report_file.name}", extra={
            'component': 'reporting',
            'operation': 'generate_report'
        })
        
        return report
    
    def _calculate_development_time(self) -> float:
        """Calculate development time in minutes"""
        if not self.current_workflow:
            return 0
        
        start_time = datetime.fromisoformat(self.current_workflow['started_at'])
        return (datetime.now() - start_time).total_seconds() / 60
    
    def _is_git_repo(self) -> bool:
        """Check if current directory is a git repository"""
        return (self.project_path / ".git").exists()
    
    def _has_github_remote(self) -> bool:
        """Check if git repository has GitHub remote"""
        if not self._is_git_repo():
            return False
        
        try:
            result = subprocess.run(
                ["git", "remote", "-v"], 
                cwd=self.project_path, 
                capture_output=True, 
                text=True
            )
            return "github.com" in result.stdout
        except:
            return False
    
    def _create_feature_branch(self, feature_name: str) -> str:
        """Create and switch to feature branch"""
        branch_name = f"feature/{feature_name}"
        
        # Ensure we're on main and up to date
        subprocess.run(["git", "checkout", "main"], cwd=self.project_path, check=True)
        subprocess.run(["git", "pull"], cwd=self.project_path, check=True)
        
        # Create and switch to feature branch
        subprocess.run(["git", "checkout", "-b", branch_name], cwd=self.project_path, check=True)
        
        return branch_name
    
    def cleanup(self):
        """Cleanup workflow manager"""
        if hasattr(self.logger, 'shutdown'):
            self.logger.shutdown()

def main():
    """CLI interface for universal workflow manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Universal Enterprise Workflow Manager")
    parser.add_argument("action", choices=["start", "commit", "pr", "demo", "status"], 
                       help="Workflow action")
    parser.add_argument("--project-path", type=str, help="Project path (default: current directory)")
    parser.add_argument("--feature", type=str, help="Feature name")
    parser.add_argument("--description", type=str, help="Feature description")
    parser.add_argument("--message", type=str, help="Commit message")
    parser.add_argument("--priority", type=str, default="medium", 
                       choices=["low", "medium", "high", "critical"])
    
    args = parser.parse_args()
    
    # Initialize workflow manager
    workflow = UniversalWorkflow(args.project_path)
    
    try:
        if args.action == "start":
            if not args.feature or not args.description:
                print("❌ --feature and --description required for start")
                return 1
            
            workflow_id = workflow.start_feature_development(
                args.feature, args.description, args.priority
            )
            print(f"✅ Started {workflow.project_type} workflow: {workflow_id}")
            
        elif args.action == "commit":
            if not args.message:
                print("❌ --message required for commit")
                return 1
            
            success = workflow.commit_changes(args.message)
            if success:
                print("✅ Changes committed with enhanced context")
            else:
                print("❌ Commit failed")
                return 1
            
        elif args.action == "pr":
            pr_url = workflow.create_pr_with_review()
            if pr_url:
                print(f"✅ PR created: {pr_url}")
            else:
                print("⚠️ PR creation skipped (no GitHub remote or gh CLI)")
            
        elif args.action == "demo":
            print(f"🧪 Running demo for {workflow.project_type} project...")
            
            # Start demo workflow
            workflow_id = workflow.start_feature_development(
                "demo-feature",
                f"Demo feature for {workflow.project_type} project",
                "medium"
            )
            
            # Simulate work
            workflow.simulate_development_work([
                f"src/demo.{workflow._get_file_extension()}",
                f"tests/demo_test.{workflow._get_file_extension()}"
            ])
            
            # Commit
            workflow.commit_changes("Add demo feature")
            
            # Test alerts
            workflow.test_alert_system()
            
            # Generate report
            report = workflow.generate_report()
            
            print(f"✅ Demo completed for {workflow.project_type} project!")
            print(f"📊 Development time: {report['development_time_minutes']:.1f} minutes")
            
        elif args.action == "status":
            if workflow.current_workflow:
                w = workflow.current_workflow
                print(f"🔄 Active Workflow: {w['workflow_id']}")
                print(f"📂 Project: {workflow.project_name} ({workflow.project_type})")
                print(f"📋 Feature: {w['feature_name']}")
                print(f"⚡ Phase: {w['phase']}")
                print(f"⏰ Running: {workflow._calculate_development_time():.1f} minutes")
            else:
                print(f"📭 No active workflow in {workflow.project_name} ({workflow.project_type})")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    finally:
        workflow.cleanup()

if __name__ == "__main__":
    sys.exit(main())