#!/usr/bin/env python3
"""
Demo Heinrich Workflow with Comprehensive Logging
===============================================

This script demonstrates the full logging system in action:
1. Feature development simulation
2. Real-time monitoring  
3. Alert generation
4. Performance analysis
5. Report generation
"""

import sys
import time
from pathlib import Path

# Add scripts to path
sys.path.append(str(Path(__file__).parent / "scripts"))

from enhanced_workflow_with_logging import EnhancedHeinrichWorkflow

def run_demo():
    """Run comprehensive logging demo"""
    print("🎩 Heinrich Logging System Demo")
    print("=" * 50)
    
    # Initialize enhanced workflow
    workflow = EnhancedHeinrichWorkflow()
    
    try:
        # Step 1: Start feature development
        print("\n1️⃣ Starting feature development...")
        workflow_id = workflow.start_feature_development(
            "demo-feature",
            "Demonstrate comprehensive logging system",
            "high"
        )
        print(f"✅ Started workflow: {workflow_id}")
        time.sleep(2)
        
        # Step 2: Simulate development work
        print("\n2️⃣ Simulating development work...")
        workflow.develop_feature(
            ["scripts/demo_feature.py", "README.md"],
            "Implementing demo feature with logging integration"
        )
        time.sleep(3)
        
        # Step 3: Commit changes
        print("\n3️⃣ Committing changes...")
        workflow.commit_changes("🧪 Add demo feature with comprehensive logging")
        time.sleep(1)
        
        # Step 4: Create PR with review
        print("\n4️⃣ Creating PR and spawning review agent...")
        try:
            pr_url = workflow.create_pr_with_review()
            print(f"✅ PR created: {pr_url}")
        except Exception as e:
            print(f"⚠️ PR creation skipped (GitHub not configured): {e}")
        
        # Step 5: Generate performance issues for alerts
        print("\n5️⃣ Generating test alerts...")
        workflow.logger.warning("Demo warning alert", extra={
            'component': 'demo',
            'operation': 'test_alert'
        })
        
        workflow.logger.error("Demo error alert", extra={
            'component': 'demo', 
            'operation': 'test_error'
        })
        
        time.sleep(2)
        
        # Step 6: Generate workflow report
        print("\n6️⃣ Generating comprehensive report...")
        report = workflow.generate_workflow_report()
        
        print(f"\n📊 Demo Complete!")
        print(f"Development Time: {report.get('development_time_minutes', 0):.1f} minutes")
        print(f"Log Entries: {report.get('log_analysis', {}).get('log_entries_analyzed', 0)}")
        print(f"Alerts Generated: {report.get('alerts', {}).get('active_alerts', 0)}")
        
        print(f"\n💡 Check the logs directory for detailed logs and reports")
        print(f"📁 Logs: {workflow.logs_dir}")
        
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"❌ Demo error: {e}")
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        workflow.shutdown()
        print("✅ Demo completed")

if __name__ == "__main__":
    run_demo()
