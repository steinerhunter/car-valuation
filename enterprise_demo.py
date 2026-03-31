#!/usr/bin/env python3
"""
Enterprise Logging Demo for car-valuation
===========================================

Demonstrates the enterprise logging system with python project specifics.
"""

import sys
import os
import time
from pathlib import Path

# Add enterprise scripts to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / ".enterprise-scripts"))

try:
    from workflow_manager import UniversalWorkflow
    
    def run_demo():
        print("🎩 Enterprise Logging Demo - car-valuation")
        print("Project Type: python")
        print("=" * 60)
        
        # Initialize workflow for this project
        workflow = UniversalWorkflow(str(project_root))
        
        try:
            # Demo feature development
            print("\n1️⃣ Starting feature development...")
            workflow_id = workflow.start_feature_development(
                "demo-feature",
                f"Demo feature for python project",
                "medium"
            )
            time.sleep(2)
            
            print("\n2️⃣ Simulating development work...")
            workflow.simulate_development_work([
                "src/component.py",
                "tests/test_component.py"
            ])
            time.sleep(1)
            
            print("\n3️⃣ Committing changes...")
            workflow.commit_changes("Add demo feature with enterprise logging")
            time.sleep(1)
            
            print("\n4️⃣ Generating test alerts...")
            workflow.test_alert_system()
            time.sleep(2)
            
            print("\n5️⃣ Generating analytics report...")
            report = workflow.generate_report()
            
            print(f"\n📊 Demo Results:")
            print(f"Development Time: {report.get('development_time_minutes', 0):.1f} minutes")
            print(f"Operations Logged: {report.get('operations_count', 0)}")
            print(f"Alerts Generated: {report.get('alerts_count', 0)}")
            
            print(f"\n💡 Check .enterprise-logs/ for detailed logs and reports")
            
        except KeyboardInterrupt:
            print("\n🛑 Demo interrupted")
        except Exception as e:
            print(f"❌ Demo error: {e}")
        finally:
            workflow.cleanup()
            print("\n✅ Demo completed")
    
    if __name__ == "__main__":
        run_demo()
        
except ImportError as e:
    print("❌ Enterprise logging scripts not found. Run setup first:")
    print("python3 -m enterprise_logging.setup")
    sys.exit(1)
