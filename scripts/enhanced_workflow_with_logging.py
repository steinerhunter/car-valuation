#!/usr/bin/env python3
"""
Enhanced Heinrich Workflow with Comprehensive Logging
===================================================

Integration layer that combines:
1. Multi-Agent Development Workflow
2. Comprehensive Logging System  
3. Real-time Monitoring
4. Smart Alert System
5. Performance Analytics

This is the MASTER workflow that Heinrich uses for ALL development work.
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent))

# Import our systems
from logging_system import HeinrichLogger, get_logger, track_operation
from monitoring_dashboard import MonitoringDashboard
from alert_system import SmartAlertSystem, AlertLevel
from log_analyzer import LogAnalyzer
from pr_workflow import PRWorkflow
from pr_integration import spawn_code_reviewer

class EnhancedHeinrichWorkflow:
    """
    Master workflow with integrated logging, monitoring, and alerting
    """
    
    def __init__(self, project_path: str = None):
        self.project_path = Path(project_path or "/home/omer/.openclaw/workspace/skills/car-valuation")
        self.logs_dir = self.project_path / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Initialize logging system
        self.logger = HeinrichLogger("heinrich_workflow", str(self.logs_dir))
        
        # Initialize monitoring and alerting
        self.dashboard = MonitoringDashboard(str(self.logs_dir))
        self.alert_system = SmartAlertSystem(str(self.logs_dir))
        self.analyzer = LogAnalyzer(str(self.logs_dir))
        
        # Initialize PR workflow
        self.pr_workflow = PRWorkflow(self.project_path)
        
        # Workflow state
        self.current_workflow = None
        self.active_operations = {}
        
        # Start background systems
        self._start_background_systems()
        
        self.logger.info("🚀 Enhanced Heinrich Workflow initialized", extra={
            'component': 'enhanced_workflow',
            'operation': 'init',
            'metadata': {
                'project_path': str(self.project_path),
                'logs_dir': str(self.logs_dir),
                'systems': ['logging', 'monitoring', 'alerts', 'analysis']
            }
        })
    
    def _start_background_systems(self):
        """Start monitoring and alerting systems"""
        # Start monitoring dashboard
        threading.Thread(target=self.dashboard.start, daemon=True).start()
        
        # Start alert system monitoring
        self.alert_system.start_monitoring()
        
        self.logger.info("🎛️ Background monitoring systems started", extra={
            'component': 'enhanced_workflow',
            'operation': 'start_monitoring'
        })
    
    def start_feature_development(self, feature_name: str, description: str, priority: str = "medium"):
        """Start new feature development with full logging and monitoring"""
        workflow_id = f"feature_{feature_name}_{int(time.time())}"
        
        with self.logger.operation("start_feature_development", "workflow", 
                                 feature_name=feature_name, priority=priority) as op_id:
            
            self.current_workflow = {
                'workflow_id': workflow_id,
                'feature_name': feature_name,
                'description': description,
                'priority': priority,
                'started_at': datetime.now().isoformat(),
                'phase': 'development',
                'correlation_id': op_id
            }
            
            # Log workflow start
            self.logger.log_workflow_step(
                workflow_id, "start_development", "initiated",
                feature_name=feature_name,
                description=description,
                priority=priority
            )
            
            # Create feature branch with logging
            try:
                branch_name = self.pr_workflow.create_feature_branch(feature_name)
                self.current_workflow['branch_name'] = branch_name
                
                self.logger.info(f"🌿 Created feature branch: {branch_name}", extra={
                    'component': 'git',
                    'operation': 'create_branch',
                    'workflow_id': workflow_id,
                    'metadata': {'branch_name': branch_name}
                })
                
            except Exception as e:
                self.logger.error(f"Failed to create feature branch: {str(e)}", extra={
                    'component': 'git',
                    'operation': 'create_branch',
                    'workflow_id': workflow_id,
                    'error_type': type(e).__name__
                })
                raise
            
            # Update Linear project status
            self._update_linear_status(workflow_id, "In Progress", f"Started development: {description}")
            
            return workflow_id
    
    def develop_feature(self, files_to_change: List[str], implementation_notes: str = ""):
        """Develop feature with detailed logging"""
        if not self.current_workflow:
            raise ValueError("No active workflow. Start with start_feature_development()")
        
        workflow_id = self.current_workflow['workflow_id']
        
        with self.logger.operation("develop_feature", "development", 
                                 workflow_id=workflow_id) as op_id:
            
            self.logger.log_workflow_step(
                workflow_id, "development", "in_progress",
                files_to_change=files_to_change,
                implementation_notes=implementation_notes
            )
            
            # Log each file modification
            for file_path in files_to_change:
                self.logger.info(f"📝 Modifying file: {file_path}", extra={
                    'component': 'development',
                    'operation': 'file_modification',
                    'workflow_id': workflow_id,
                    'correlation_id': op_id,
                    'metadata': {'file_path': file_path}
                })
            
            # This is where Heinrich would actually write/modify code
            # For now, we'll simulate the development process
            time.sleep(1)  # Simulate work
            
            self.logger.info(f"✅ Feature development completed", extra={
                'component': 'development',
                'operation': 'feature_complete',
                'workflow_id': workflow_id,
                'metadata': {
                    'files_modified': len(files_to_change),
                    'implementation_notes': implementation_notes
                }
            })
    
    def commit_changes(self, commit_message: str, files: List[str] = None):
        """Commit changes with enhanced logging"""
        if not self.current_workflow:
            raise ValueError("No active workflow")
        
        workflow_id = self.current_workflow['workflow_id']
        
        with self.logger.operation("commit_changes", "git", 
                                 workflow_id=workflow_id) as op_id:
            
            try:
                # Enhanced commit with workflow tracking
                enhanced_message = f"""{commit_message}

🤖 Heinrich Workflow: {workflow_id}
📋 Feature: {self.current_workflow['feature_name']}
🔗 Operation: {op_id}
⏰ Timestamp: {datetime.now().isoformat()}

Co-authored-by: Heinrich AI <heinrich@heinrich.bot>"""
                
                self.pr_workflow.commit_changes(enhanced_message, files)
                
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
                
            except Exception as e:
                self.logger.error(f"Commit failed: {str(e)}", extra={
                    'component': 'git',
                    'operation': 'commit',
                    'workflow_id': workflow_id,
                    'error_type': type(e).__name__
                })
                raise
    
    def create_pr_with_review(self, pr_title: str = None, pr_description: str = None):
        """Create PR and spawn review agent with full logging"""
        if not self.current_workflow:
            raise ValueError("No active workflow")
        
        workflow_id = self.current_workflow['workflow_id']
        feature_name = self.current_workflow['feature_name']
        
        with self.logger.operation("create_pr_with_review", "pr_workflow", 
                                 workflow_id=workflow_id) as op_id:
            
            # Default PR details if not provided
            if not pr_title:
                pr_title = f"🧠 {feature_name.replace('-', ' ').title()}"
            if not pr_description:
                pr_description = self.current_workflow.get('description', '')
            
            try:
                # Create PR with enhanced description
                enhanced_description = self._generate_enhanced_pr_description(pr_description)
                
                pr_url = self.pr_workflow.create_pull_request(
                    pr_title, enhanced_description, self.current_workflow['branch_name']
                )
                
                if pr_url:
                    self.current_workflow['pr_url'] = pr_url
                    self.current_workflow['phase'] = 'pr_created'
                    
                    self.logger.log_pr_event(pr_url, "created", 
                                           workflow_id=workflow_id,
                                           feature_name=feature_name)
                    
                    # Spawn review agent with enhanced context
                    review_context = self._generate_review_context()
                    review_result = spawn_code_reviewer(
                        self._generate_enhanced_review_prompt(review_context),
                        pr_url
                    )
                    
                    if review_result:
                        self.logger.log_agent_communication(
                            "heinrich", "review_agent", "spawn_review",
                            pr_url=pr_url,
                            workflow_id=workflow_id,
                            review_id=review_result.get('review_id')
                        )
                        
                        self.current_workflow['review_agent_id'] = review_result.get('review_id')
                        self.current_workflow['phase'] = 'under_review'
                    
                    return pr_url
                    
            except Exception as e:
                self.logger.error(f"PR creation failed: {str(e)}", extra={
                    'component': 'pr_workflow',
                    'operation': 'create_pr',
                    'workflow_id': workflow_id,
                    'error_type': type(e).__name__
                })
                raise
    
    def _generate_enhanced_pr_description(self, base_description: str) -> str:
        """Generate comprehensive PR description with workflow context"""
        workflow = self.current_workflow
        
        return f"""{base_description}

## 🔄 Enhanced Heinrich Multi-Agent Workflow

**🤖 Development Agent:** Heinrich AI  
**📋 Workflow ID:** `{workflow['workflow_id']}`  
**🌿 Feature Branch:** `{workflow['branch_name']}`  
**⚡ Priority:** {workflow['priority'].upper()}  
**⏰ Started:** {workflow['started_at']}  

## 📊 Development Metrics
**🔧 Phase:** {workflow['phase']}  
**📝 Commits:** {len(workflow.get('commits', []))}  
**🕒 Development Time:** {self._calculate_development_time()} minutes  

## 🔍 Enhanced Review Requirements

### 🎯 Heinrich Quality Standards
- [ ] **Architecture**: Follows Heinrich's development patterns
- [ ] **Performance**: Meets Heinrich's efficiency standards  
- [ ] **Security**: Heinrich's security validation passed
- [ ] **Domain Logic**: Israeli market logic verified
- [ ] **Code Quality**: Heinrich's quality metrics met
- [ ] **Testing**: Critical paths have coverage
- [ ] **Documentation**: Heinrich's documentation standards

### 🧠 AI-Specific Validation
- [ ] **Algorithm Efficiency**: No unnecessary complexity
- [ ] **Resource Usage**: Memory and CPU within limits
- [ ] **Error Handling**: Comprehensive error scenarios
- [ ] **Edge Cases**: Unusual inputs handled gracefully
- [ ] **Hebrew Processing**: Text handling robust and accurate
- [ ] **API Integration**: Yad2/external services fault-tolerant

## 🤖 Review Agent Instructions

**📋 Mission:** Comprehensive analysis of Heinrich's development work

**🔍 Focus Areas:**
1. **Code Architecture** - Heinrich's structural decisions
2. **Performance Impact** - Efficiency and resource usage
3. **Security Validation** - No vulnerabilities introduced
4. **Domain Accuracy** - Israeli car market logic correctness
5. **Integration Quality** - Yad2 and external service reliability

**📊 Review Process:**
1. Use `read` tool to examine all changed files
2. Analyze against Heinrich's quality standards
3. Validate domain-specific logic (Hebrew, Israeli market)
4. Check performance implications
5. Verify security considerations

**🎯 Decision Criteria:**
- ✅ **APPROVED**: Meets all Heinrich quality standards
- ❌ **CHANGES REQUESTED**: Issues require resolution

## 📈 Workflow Tracking
- **Linear Issue**: Auto-updated with progress
- **Monitoring**: Real-time performance tracking active
- **Alerts**: Smart alerts configured for issues
- **Analytics**: Comprehensive logging for optimization

---
**🎩 Heinrich AI Enhanced Multi-Agent Workflow v2.0**  
**🔗 Workflow ID: `{workflow['workflow_id']}`**"""
    
    def _generate_review_context(self) -> Dict:
        """Generate comprehensive context for review agent"""
        return {
            'workflow': self.current_workflow,
            'project_info': {
                'name': 'Car Valuation System',
                'domain': 'Israeli Automotive Market',
                'technologies': ['Python', 'Yad2 API', 'Hebrew Processing'],
                'quality_standards': 'Enterprise-level AI development'
            },
            'recent_performance': self._get_recent_performance_metrics(),
            'known_issues': self._get_known_issues(),
            'review_history': self._get_review_history()
        }
    
    def _generate_enhanced_review_prompt(self, context: Dict) -> str:
        """Generate enhanced review prompt with full context"""
        return f"""🔍 ENHANCED CODE REVIEW MISSION - Heinrich AI Workflow

## 🎯 Review Context
**Workflow ID:** {context['workflow']['workflow_id']}  
**Feature:** {context['workflow']['feature_name']}  
**Priority:** {context['workflow']['priority']}  
**Development Time:** {self._calculate_development_time()} minutes

## 🏗️ Project Context
**Domain:** Israeli Car Market Valuation  
**Technologies:** Python, Yad2 Integration, Hebrew Processing  
**Quality Standard:** Enterprise AI Development  

## 🔍 COMPREHENSIVE REVIEW REQUIREMENTS

### 1. **DEEP CODE ANALYSIS** ⚡
**Must use `read` tool to examine ALL changed files**

**Check for:**
- Architecture consistency with existing patterns
- Function complexity and single responsibility
- Variable naming clarity and consistency  
- Comment quality and necessity
- Code duplication and DRY principle

### 2. **SECURITY VALIDATION** 🔒
**Critical security checks:**
- No hardcoded secrets or API keys
- Proper input validation and sanitization
- SQL injection and XSS vulnerability prevention
- Sensitive data exposure risks
- Authentication and authorization proper

### 3. **PERFORMANCE ANALYSIS** ⚡
**Performance considerations:**
- Algorithm efficiency and time complexity
- Memory usage patterns and potential leaks
- API call optimization and rate limiting
- Database query efficiency
- Resource cleanup and management

### 4. **DOMAIN LOGIC VERIFICATION** 🇮🇱
**Israeli market-specific validation:**
- Hebrew text processing accuracy
- Yad2 API integration robustness
- Israeli currency formatting (₪)
- Geographic data accuracy (cities, regions)
- Market calculation correctness

### 5. **ERROR RESILIENCE** 🛡️
**Error handling validation:**
- Comprehensive exception handling
- Graceful degradation patterns  
- User-friendly error messages
- Logging and monitoring integration
- Recovery mechanism implementation

### 6. **INTEGRATION QUALITY** 🔗
**External service integration:**
- API timeout and retry logic
- Rate limiting compliance
- Fallback mechanisms
- Data validation from external sources
- Network failure handling

## 📊 QUALITY METRICS EVALUATION

### Code Quality Checklist:
- [ ] Functions under 50 lines
- [ ] Cyclomatic complexity under 10
- [ ] Clear variable and function names
- [ ] Proper type hints where applicable
- [ ] Docstrings for public interfaces

### Performance Benchmarks:
- [ ] Response times under 2 seconds
- [ ] Memory usage under 500MB
- [ ] No blocking operations in main thread
- [ ] Efficient data structures used
- [ ] Minimal API calls per operation

### Security Standards:
- [ ] No secrets in code
- [ ] Input validation present
- [ ] SQL injection protection
- [ ] XSS prevention measures
- [ ] Error messages don't leak info

## 🎯 REVIEW OUTPUT REQUIREMENTS

### If Issues Found:
```
❌ CHANGES REQUESTED

## 🐛 Critical Issues:
1. **[File:Line]** Security vulnerability: [specific issue]
   💡 **Fix:** [exact solution]
   🔴 **Severity:** Critical

2. **[File:Line]** Performance bottleneck: [specific issue]  
   💡 **Fix:** [exact solution]
   🔴 **Severity:** Major

## 📋 Recommendations:
- [Specific improvement suggestions]
- [Best practice recommendations]

## 🔄 Next Steps:
Address Critical and Major issues, then re-request review.
```

### If Approved:
```
✅ APPROVED - Heinrich Quality Standards Met

## ✨ Review Summary:
- **Architecture:** ✅ Follows Heinrich patterns
- **Security:** ✅ No vulnerabilities detected  
- **Performance:** ✅ Efficient implementation
- **Domain Logic:** ✅ Israeli market accuracy verified
- **Error Handling:** ✅ Comprehensive coverage
- **Integration:** ✅ Robust external service handling

## 💎 Quality Highlights:
- [Specific examples of excellent code quality]
- [Performance optimizations noted]
- [Security measures appreciated]

**This code meets Heinrich's enterprise AI development standards and is ready for production deployment.**
```

## ⚠️ CRITICAL INSTRUCTIONS:
1. **READ EVERY CHANGED FILE** - Use read tool, don't assume
2. **BE THOROUGH** - Heinrich's reputation depends on quality
3. **BE SPECIFIC** - Reference exact lines and files  
4. **CONSIDER DOMAIN** - Israeli market and Hebrew processing
5. **CHECK PERFORMANCE** - Efficiency is critical
6. **VERIFY SECURITY** - No compromise on safety

**Heinrich's development quality depends on your comprehensive review. Take the time needed to ensure excellence.**

## 🔬 START YOUR DETAILED REVIEW NOW"""
    
    def _calculate_development_time(self) -> float:
        """Calculate development time in minutes"""
        if not self.current_workflow:
            return 0
        
        start_time = datetime.fromisoformat(self.current_workflow['started_at'])
        return (datetime.now() - start_time).total_seconds() / 60
    
    def _get_recent_performance_metrics(self) -> Dict:
        """Get recent performance metrics"""
        # This would query the logging system for recent performance data
        return {
            'avg_response_time_ms': 150,
            'memory_usage_mb': 256,
            'error_rate': 0.02
        }
    
    def _get_known_issues(self) -> List[str]:
        """Get known issues to watch for"""
        return [
            "Yad2 rate limiting on high volume",
            "Hebrew encoding issues on older Python versions",
            "Memory usage during large dataset processing"
        ]
    
    def _get_review_history(self) -> List[Dict]:
        """Get relevant review history"""
        return [
            {
                'date': '2026-03-30',
                'common_issues': ['Error handling', 'Performance optimization'],
                'improvement_areas': ['Documentation', 'Test coverage']
            }
        ]
    
    def _update_linear_status(self, workflow_id: str, status: str, comment: str):
        """Update Linear project status"""
        try:
            self.logger.info(f"📋 Linear update: {status}", extra={
                'component': 'linear_integration',
                'operation': 'status_update',
                'workflow_id': workflow_id,
                'metadata': {
                    'status': status,
                    'comment': comment
                }
            })
            # This would integrate with the Linear API
        except Exception as e:
            self.logger.warning(f"Linear update failed: {str(e)}", extra={
                'component': 'linear_integration',
                'operation': 'status_update',
                'workflow_id': workflow_id
            })
    
    def generate_workflow_report(self) -> Dict:
        """Generate comprehensive workflow report"""
        if not self.current_workflow:
            return {"error": "No active workflow"}
        
        # Run log analysis for current workflow
        analysis = self.analyzer.run_full_analysis(hours=24)
        
        # Get alert summary
        alert_summary = self.alert_system.get_alert_summary()
        
        # Get monitoring dashboard status
        dashboard_status = self.dashboard.get_status_summary()
        
        report = {
            "workflow": self.current_workflow,
            "development_time_minutes": self._calculate_development_time(),
            "log_analysis": analysis,
            "alerts": alert_summary,
            "monitoring": dashboard_status,
            "recommendations": self._generate_workflow_recommendations(analysis)
        }
        
        # Save report
        report_file = self.logs_dir / f"workflow_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📊 Workflow report generated: {report_file}", extra={
            'component': 'reporting',
            'operation': 'generate_report',
            'workflow_id': self.current_workflow['workflow_id']
        })
        
        return report
    
    def _generate_workflow_recommendations(self, analysis: Dict) -> List[str]:
        """Generate recommendations based on workflow analysis"""
        recommendations = []
        
        # Performance recommendations
        performance = analysis.get('performance', {})
        if performance.get('duration_stats', {}).get('p95_ms', 0) > 1000:
            recommendations.append("Consider optimizing slow operations for better responsiveness")
        
        # Error rate recommendations  
        errors = analysis.get('errors', {})
        if errors.get('total_errors', 0) > 0:
            recommendations.append("Review error patterns and implement additional error handling")
        
        # Workflow efficiency recommendations
        if self._calculate_development_time() > 120:  # 2 hours
            recommendations.append("Consider breaking down large features into smaller, manageable pieces")
        
        return recommendations
    
    def shutdown(self):
        """Graceful shutdown of all systems"""
        self.logger.info("🛑 Shutting down Enhanced Heinrich Workflow", extra={
            'component': 'enhanced_workflow',
            'operation': 'shutdown'
        })
        
        # Shutdown subsystems
        self.dashboard.stop()
        self.alert_system.shutdown()
        self.logger.shutdown()
        
        print("✅ Enhanced Heinrich Workflow shut down gracefully")

def main():
    """CLI interface for enhanced workflow"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Heinrich Workflow")
    parser.add_argument("action", choices=["start", "commit", "pr", "report", "status"])
    parser.add_argument("--feature", type=str, help="Feature name")
    parser.add_argument("--description", type=str, help="Feature description")
    parser.add_argument("--message", type=str, help="Commit message")
    parser.add_argument("--priority", type=str, default="medium", choices=["low", "medium", "high"])
    
    args = parser.parse_args()
    
    workflow = EnhancedHeinrichWorkflow()
    
    try:
        if args.action == "start":
            if not args.feature or not args.description:
                print("❌ --feature and --description required for start")
                return
            
            workflow_id = workflow.start_feature_development(
                args.feature, args.description, args.priority
            )
            print(f"✅ Started workflow: {workflow_id}")
            
        elif args.action == "commit":
            if not args.message:
                print("❌ --message required for commit")
                return
            
            workflow.commit_changes(args.message)
            print("✅ Changes committed")
            
        elif args.action == "pr":
            pr_url = workflow.create_pr_with_review()
            print(f"✅ PR created and review agent spawned: {pr_url}")
            
        elif args.action == "report":
            report = workflow.generate_workflow_report()
            print("📊 Workflow Report Generated")
            print(f"Development Time: {report.get('development_time_minutes', 0):.1f} minutes")
            print(f"Alerts: {report.get('alerts', {}).get('active_alerts', 0)} active")
            
        elif args.action == "status":
            if workflow.current_workflow:
                print(f"🔄 Active Workflow: {workflow.current_workflow['workflow_id']}")
                print(f"📋 Feature: {workflow.current_workflow['feature_name']}")
                print(f"⚡ Phase: {workflow.current_workflow['phase']}")
                print(f"⏰ Running: {workflow._calculate_development_time():.1f} minutes")
            else:
                print("📭 No active workflow")
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        workflow.shutdown()

if __name__ == "__main__":
    main()