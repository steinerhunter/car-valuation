#!/usr/bin/env python3
"""
Heinrich Real-Time Monitoring Dashboard
=====================================

Live dashboard for monitoring Heinrich's development workflow:
- Real-time log streaming
- Performance metrics
- Agent communication tracking  
- Workflow progress visualization
- Error detection and alerting
"""

import os
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, deque
from typing import Dict, List, Optional, Any
import subprocess

class MonitoringDashboard:
    """
    Real-time monitoring dashboard for Heinrich's multi-agent workflow
    """
    
    def __init__(self, log_dir: str = None):
        self.log_dir = Path(log_dir or "/home/omer/.openclaw/workspace/skills/car-valuation/logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Monitoring state
        self.is_running = False
        self.last_positions = {}  # File positions for tailing
        
        # Real-time metrics
        self.metrics = {
            'total_operations': 0,
            'active_workflows': set(),
            'error_count': 0,
            'warning_count': 0,
            'average_response_time': 0.0,
            'memory_usage_mb': 0.0,
            'cpu_usage_percent': 0.0
        }
        
        # Recent events (last 100)
        self.recent_events = deque(maxlen=100)
        self.recent_errors = deque(maxlen=50)
        self.recent_performance = deque(maxlen=50)
        
        # Agent communication tracking
        self.agent_communications = deque(maxlen=50)
        self.workflow_status = {}
        
        # Alert thresholds
        self.alert_thresholds = {
            'error_rate_per_minute': 5,
            'memory_usage_mb': 1000,
            'cpu_usage_percent': 80,
            'response_time_ms': 5000
        }
        
        print("🖥️ Heinrich Monitoring Dashboard initialized")
        print(f"📂 Log directory: {self.log_dir}")
    
    def start(self):
        """Start real-time monitoring"""
        self.is_running = True
        
        # Start monitoring threads
        threading.Thread(target=self._tail_logs, daemon=True).start()
        threading.Thread(target=self._update_system_metrics, daemon=True).start()
        
        print("🚀 Real-time monitoring started")
        self._display_dashboard()
    
    def stop(self):
        """Stop monitoring"""
        self.is_running = False
        print("🛑 Monitoring stopped")
    
    def _tail_logs(self):
        """Continuously monitor log files for new entries"""
        while self.is_running:
            try:
                # Monitor JSON log file
                json_log = self.log_dir / f"heinrich_{datetime.now().strftime('%Y%m%d')}.jsonl"
                if json_log.exists():
                    self._process_new_log_entries(json_log)
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                print(f"❌ Error tailing logs: {e}")
                time.sleep(5)
    
    def _process_new_log_entries(self, log_file: Path):
        """Process new log entries from file"""
        try:
            # Get file position
            file_key = str(log_file)
            current_pos = self.last_positions.get(file_key, 0)
            
            with open(log_file, 'r') as f:
                f.seek(current_pos)
                
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                        
                    try:
                        entry = json.loads(line)
                        self._process_log_entry(entry)
                    except json.JSONDecodeError:
                        continue
                
                # Update position
                self.last_positions[file_key] = f.tell()
                
        except Exception as e:
            print(f"❌ Error processing log entries: {e}")
    
    def _process_log_entry(self, entry: Dict):
        """Process a single log entry"""
        # Update metrics
        self.metrics['total_operations'] += 1
        
        level = entry.get('level', '')
        if level == 'ERROR':
            self.metrics['error_count'] += 1
            self.recent_errors.append(entry)
        elif level == 'WARNING':
            self.metrics['warning_count'] += 1
        
        # Track workflows
        workflow_id = entry.get('workflow_id')
        if workflow_id:
            self.metrics['active_workflows'].add(workflow_id)
            self._update_workflow_status(workflow_id, entry)
        
        # Track performance
        duration_ms = entry.get('duration_ms')
        if duration_ms:
            self.recent_performance.append(entry)
            self._update_performance_metrics()
        
        # Track agent communication
        component = entry.get('component', '')
        if component == 'agent_communication':
            self.agent_communications.append(entry)
        
        # Track recent events
        self.recent_events.append(entry)
        
        # Check for alerts
        self._check_alerts(entry)
    
    def _update_workflow_status(self, workflow_id: str, entry: Dict):
        """Update workflow status tracking"""
        operation = entry.get('operation', '')
        timestamp = entry.get('timestamp', '')
        
        if workflow_id not in self.workflow_status:
            self.workflow_status[workflow_id] = {
                'created_at': timestamp,
                'steps': [],
                'current_status': 'active',
                'last_update': timestamp
            }
        
        workflow = self.workflow_status[workflow_id]
        workflow['steps'].append({
            'operation': operation,
            'timestamp': timestamp,
            'level': entry.get('level', ''),
            'message': entry.get('message', '')
        })
        workflow['last_update'] = timestamp
    
    def _update_performance_metrics(self):
        """Update performance metrics from recent data"""
        if not self.recent_performance:
            return
            
        # Calculate average response time
        durations = [e.get('duration_ms', 0) for e in self.recent_performance if e.get('duration_ms')]
        if durations:
            self.metrics['average_response_time'] = sum(durations) / len(durations)
    
    def _update_system_metrics(self):
        """Update system resource metrics"""
        while self.is_running:
            try:
                import psutil
                process = psutil.Process()
                
                self.metrics['memory_usage_mb'] = process.memory_info().rss / 1024 / 1024
                self.metrics['cpu_usage_percent'] = process.cpu_percent()
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                print(f"❌ Error updating system metrics: {e}")
                time.sleep(10)
    
    def _check_alerts(self, entry: Dict):
        """Check entry against alert thresholds"""
        level = entry.get('level', '')
        
        # Critical/Error alerts
        if level in ['ERROR', 'CRITICAL']:
            self._send_alert(f"🚨 {level}: {entry.get('message', 'Unknown error')}", entry)
        
        # Performance alerts
        duration_ms = entry.get('duration_ms')
        if duration_ms and duration_ms > self.alert_thresholds['response_time_ms']:
            self._send_alert(f"⚠️ Slow operation: {duration_ms:.1f}ms", entry)
        
        # Memory alerts
        memory_mb = entry.get('memory_mb')
        if memory_mb and memory_mb > self.alert_thresholds['memory_usage_mb']:
            self._send_alert(f"⚠️ High memory usage: {memory_mb:.1f}MB", entry)
    
    def _send_alert(self, message: str, entry: Dict):
        """Send alert (can be extended to Slack, email, etc.)"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        alert_msg = f"[{timestamp}] {message}"
        
        # For now, just print to console
        print(f"\n🔔 ALERT: {alert_msg}")
        
        # Could extend to:
        # - Send Slack message
        # - Send email
        # - Write to dedicated alert log
        # - Trigger webhook
    
    def _display_dashboard(self):
        """Display real-time dashboard in terminal"""
        while self.is_running:
            try:
                # Clear screen
                os.system('clear' if os.name == 'posix' else 'cls')
                
                # Display header
                print("=" * 80)
                print("🎩 Heinrich Multi-Agent Development Monitoring Dashboard")
                print("=" * 80)
                print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print()
                
                # Display metrics
                self._display_metrics()
                print()
                
                # Display active workflows
                self._display_workflows()
                print()
                
                # Display recent events
                self._display_recent_events()
                print()
                
                # Display recent errors
                if self.recent_errors:
                    self._display_recent_errors()
                    print()
                
                # Display agent communications
                if self.agent_communications:
                    self._display_agent_communications()
                    print()
                
                print("Press Ctrl+C to stop monitoring")
                print("-" * 80)
                
                time.sleep(2)  # Update every 2 seconds
                
            except KeyboardInterrupt:
                self.stop()
                break
            except Exception as e:
                print(f"❌ Dashboard error: {e}")
                time.sleep(5)
    
    def _display_metrics(self):
        """Display key metrics"""
        print("📊 SYSTEM METRICS:")
        print(f"   🔢 Total Operations: {self.metrics['total_operations']}")
        print(f"   🔄 Active Workflows: {len(self.metrics['active_workflows'])}")
        print(f"   ❌ Errors: {self.metrics['error_count']}")
        print(f"   ⚠️  Warnings: {self.metrics['warning_count']}")
        print(f"   ⚡ Avg Response Time: {self.metrics['average_response_time']:.1f}ms")
        print(f"   🧠 Memory Usage: {self.metrics['memory_usage_mb']:.1f}MB")
        print(f"   🔥 CPU Usage: {self.metrics['cpu_usage_percent']:.1f}%")
    
    def _display_workflows(self):
        """Display active workflow status"""
        print("🔄 ACTIVE WORKFLOWS:")
        if not self.workflow_status:
            print("   No active workflows")
            return
        
        for workflow_id, workflow in list(self.workflow_status.items())[-5:]:  # Last 5
            last_step = workflow['steps'][-1] if workflow['steps'] else {}
            print(f"   📋 {workflow_id}")
            print(f"      📊 Status: {workflow.get('current_status', 'unknown')}")
            print(f"      🔧 Last: {last_step.get('operation', 'unknown')}")
            print(f"      ⏰ Updated: {workflow.get('last_update', 'unknown')}")
    
    def _display_recent_events(self):
        """Display recent log events"""
        print("📝 RECENT EVENTS (last 10):")
        recent = list(self.recent_events)[-10:]
        
        for event in recent:
            timestamp = event.get('timestamp', '')[:19]  # Remove microseconds
            level = event.get('level', '')
            component = event.get('component', '')
            operation = event.get('operation', '')
            message = event.get('message', '')[:50] + '...' if len(event.get('message', '')) > 50 else event.get('message', '')
            
            level_symbol = {
                'DEBUG': '🔍',
                'INFO': 'ℹ️',
                'WARNING': '⚠️',
                'ERROR': '❌',
                'CRITICAL': '🚨'
            }.get(level, '📝')
            
            comp_op = f"{component}.{operation}" if component and operation else component or operation or ""
            print(f"   {level_symbol} {timestamp[-8:]} | {comp_op:<20} | {message}")
    
    def _display_recent_errors(self):
        """Display recent errors"""
        print("🚨 RECENT ERRORS (last 5):")
        recent_errors = list(self.recent_errors)[-5:]
        
        for error in recent_errors:
            timestamp = error.get('timestamp', '')[:19]
            component = error.get('component', '')
            message = error.get('message', '')[:60] + '...' if len(error.get('message', '')) > 60 else error.get('message', '')
            print(f"   ❌ {timestamp[-8:]} | {component:<15} | {message}")
    
    def _display_agent_communications(self):
        """Display recent agent communications"""
        print("🤖 AGENT COMMUNICATIONS (last 5):")
        recent_comms = list(self.agent_communications)[-5:]
        
        for comm in recent_comms:
            timestamp = comm.get('timestamp', '')[:19]
            message = comm.get('message', '')
            metadata = comm.get('metadata', {})
            from_agent = metadata.get('from_agent', 'unknown')
            to_agent = metadata.get('to_agent', 'unknown')
            
            print(f"   🤖 {timestamp[-8:]} | {from_agent} → {to_agent} | {message}")
    
    def get_status_summary(self):
        """Get current status summary"""
        return {
            'timestamp': datetime.now().isoformat(),
            'metrics': dict(self.metrics),
            'active_workflows': len(self.workflow_status),
            'recent_errors': len(self.recent_errors),
            'recent_events': len(self.recent_events),
            'alert_status': 'healthy' if self.metrics['error_count'] == 0 else 'issues_detected'
        }
    
    def export_logs(self, hours: int = 24):
        """Export logs from last N hours for analysis"""
        since = datetime.now() - timedelta(hours=hours)
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'time_range_hours': hours,
            'summary': self.get_status_summary(),
            'events': list(self.recent_events),
            'errors': list(self.recent_errors),
            'performance': list(self.recent_performance),
            'workflows': dict(self.workflow_status)
        }
        
        export_file = self.log_dir / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Logs exported to: {export_file}")
        return export_file

def main():
    """Run monitoring dashboard"""
    dashboard = MonitoringDashboard()
    
    try:
        dashboard.start()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down monitoring dashboard...")
        dashboard.stop()

if __name__ == "__main__":
    main()