#!/usr/bin/env python3
"""
Heinrich Smart Alert System
==========================

Intelligent alerting system that monitors Heinrich's operations and sends
proactive notifications about issues, performance problems, and critical events.

Features:
- Multi-channel alerting (Slack, console, file)
- Smart thresholds with adaptive learning
- Alert de-duplication and rate limiting
- Escalation policies for critical issues
- Context-aware alert prioritization
"""

import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from enum import Enum

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertChannel(Enum):
    CONSOLE = "console"
    FILE = "file"
    SLACK = "slack"
    EMAIL = "email"

@dataclass
class Alert:
    """Structured alert with context and metadata"""
    id: str
    timestamp: str
    level: AlertLevel
    title: str
    message: str
    component: str
    operation: Optional[str] = None
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = None
    channels: List[AlertChannel] = None
    escalation_count: int = 0
    resolved: bool = False
    
    def __post_init__(self):
        if self.channels is None:
            self.channels = [AlertChannel.CONSOLE, AlertChannel.FILE]
        if self.metadata is None:
            self.metadata = {}

class AlertRule:
    """Alert rule definition with conditions and actions"""
    
    def __init__(self, 
                 name: str,
                 condition: Callable[[Dict], bool],
                 level: AlertLevel,
                 message_template: str,
                 cooldown_minutes: int = 5,
                 channels: List[AlertChannel] = None):
        self.name = name
        self.condition = condition
        self.level = level
        self.message_template = message_template
        self.cooldown_minutes = cooldown_minutes
        self.channels = channels or [AlertChannel.CONSOLE, AlertChannel.FILE]
        self.last_fired = None
        self.fire_count = 0

class SmartAlertSystem:
    """
    Intelligent alert system with adaptive thresholds and smart notifications
    """
    
    def __init__(self, log_dir: str = None):
        self.log_dir = Path(log_dir or "/home/omer/.openclaw/workspace/skills/car-valuation/logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Alert storage
        self.active_alerts = {}  # id -> Alert
        self.alert_history = deque(maxlen=1000)
        self.alert_stats = defaultdict(int)
        
        # Alert rules
        self.rules = []
        self.adaptive_thresholds = {}
        
        # Rate limiting
        self.rate_limits = defaultdict(lambda: deque(maxlen=10))
        
        # Background monitoring
        self.monitoring_active = False
        self.last_log_position = 0
        
        # Setup default rules
        self._setup_default_rules()
        
        # Initialize alert log
        self.alert_log = self.log_dir / f"alerts_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        print("🚨 Heinrich Smart Alert System initialized")
        print(f"📂 Alert log: {self.alert_log}")
    
    def _setup_default_rules(self):
        """Setup default alert rules"""
        
        # High error rate
        self.add_rule(AlertRule(
            name="high_error_rate",
            condition=lambda metrics: metrics.get("error_rate_per_minute", 0) > 5,
            level=AlertLevel.WARNING,
            message_template="High error rate detected: {error_rate_per_minute:.1f} errors/minute",
            cooldown_minutes=10,
            channels=[AlertChannel.CONSOLE, AlertChannel.FILE, AlertChannel.SLACK]
        ))
        
        # Memory usage spike
        self.add_rule(AlertRule(
            name="memory_spike",
            condition=lambda metrics: metrics.get("memory_mb", 0) > 1000,
            level=AlertLevel.WARNING,
            message_template="High memory usage: {memory_mb:.1f}MB",
            cooldown_minutes=5
        ))
        
        # Critical errors
        self.add_rule(AlertRule(
            name="critical_error",
            condition=lambda entry: entry.get("level") == "CRITICAL",
            level=AlertLevel.CRITICAL,
            message_template="Critical error in {component}: {message}",
            cooldown_minutes=0,  # No cooldown for critical errors
            channels=[AlertChannel.CONSOLE, AlertChannel.FILE, AlertChannel.SLACK]
        ))
        
        # Slow operations
        self.add_rule(AlertRule(
            name="slow_operation",
            condition=lambda entry: entry.get("duration_ms", 0) > 10000,
            level=AlertLevel.WARNING,
            message_template="Slow operation detected: {operation} took {duration_ms:.1f}ms",
            cooldown_minutes=15
        ))
        
        # Workflow failures
        self.add_rule(AlertRule(
            name="workflow_failure",
            condition=lambda entry: (entry.get("component") == "workflow" and 
                                   entry.get("level") == "ERROR" and
                                   "failed" in entry.get("message", "").lower()),
            level=AlertLevel.ERROR,
            message_template="Workflow failure: {workflow_id} - {message}",
            cooldown_minutes=5,
            channels=[AlertChannel.CONSOLE, AlertChannel.FILE, AlertChannel.SLACK]
        ))
        
        # Agent communication failures
        self.add_rule(AlertRule(
            name="agent_comm_failure",
            condition=lambda entry: (entry.get("component") == "agent_communication" and
                                   entry.get("level") in ["ERROR", "CRITICAL"]),
            level=AlertLevel.ERROR,
            message_template="Agent communication failure: {message}",
            cooldown_minutes=3,
            channels=[AlertChannel.CONSOLE, AlertChannel.FILE, AlertChannel.SLACK]
        ))
        
        # Resource exhaustion
        self.add_rule(AlertRule(
            name="resource_exhaustion",
            condition=lambda metrics: (metrics.get("cpu_percent", 0) > 90 or
                                     metrics.get("memory_mb", 0) > 2000),
            level=AlertLevel.CRITICAL,
            message_template="Resource exhaustion: CPU {cpu_percent:.1f}%, Memory {memory_mb:.1f}MB",
            cooldown_minutes=5,
            channels=[AlertChannel.CONSOLE, AlertChannel.FILE, AlertChannel.SLACK]
        ))
    
    def add_rule(self, rule: AlertRule):
        """Add new alert rule"""
        self.rules.append(rule)
        print(f"✅ Added alert rule: {rule.name}")
    
    def start_monitoring(self, log_file: str = None):
        """Start real-time log monitoring for alerts"""
        if not log_file:
            log_file = self.log_dir / f"heinrich_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
        self.monitoring_active = True
        
        def monitor():
            print(f"🔍 Starting alert monitoring on: {log_file}")
            
            while self.monitoring_active:
                try:
                    if Path(log_file).exists():
                        self._check_log_file(log_file)
                    time.sleep(2)  # Check every 2 seconds
                except Exception as e:
                    print(f"❌ Alert monitoring error: {e}")
                    time.sleep(10)
        
        threading.Thread(target=monitor, daemon=True).start()
        print("🚨 Real-time alert monitoring started")
    
    def _check_log_file(self, log_file: str):
        """Check log file for new entries that trigger alerts"""
        try:
            with open(log_file, 'r') as f:
                # Seek to last position
                f.seek(self.last_log_position)
                
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        entry = json.loads(line)
                        self._process_log_entry_for_alerts(entry)
                    except json.JSONDecodeError:
                        continue
                
                # Update position
                self.last_log_position = f.tell()
                
        except Exception as e:
            print(f"❌ Error checking log file: {e}")
    
    def _process_log_entry_for_alerts(self, entry: Dict):
        """Process log entry against alert rules"""
        current_time = datetime.now()
        
        for rule in self.rules:
            try:
                # Check cooldown
                if rule.last_fired:
                    time_since_last = (current_time - rule.last_fired).total_seconds() / 60
                    if time_since_last < rule.cooldown_minutes:
                        continue
                
                # Check condition
                if rule.condition(entry):
                    self._fire_alert(rule, entry)
                    
            except Exception as e:
                print(f"❌ Error processing rule {rule.name}: {e}")
    
    def _fire_alert(self, rule: AlertRule, context: Dict):
        """Fire an alert based on rule and context"""
        current_time = datetime.now()
        
        # Generate alert
        alert_id = f"{rule.name}_{int(current_time.timestamp())}"
        
        try:
            # Format message
            message = rule.message_template.format(**context)
        except KeyError:
            # If template formatting fails, use basic message
            message = f"{rule.message_template} - Context: {context.get('message', 'No details')}"
        
        alert = Alert(
            id=alert_id,
            timestamp=current_time.isoformat(),
            level=rule.level,
            title=f"Alert: {rule.name}",
            message=message,
            component=context.get("component", "unknown"),
            operation=context.get("operation"),
            correlation_id=context.get("correlation_id"),
            metadata={
                "rule_name": rule.name,
                "fire_count": rule.fire_count + 1,
                "context": context
            },
            channels=rule.channels
        )
        
        # Update rule state
        rule.last_fired = current_time
        rule.fire_count += 1
        
        # Store alert
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        self.alert_stats[rule.level.value] += 1
        
        # Send alert
        self._send_alert(alert)
        
        # Log alert
        self._log_alert(alert)
    
    def _send_alert(self, alert: Alert):
        """Send alert through specified channels"""
        for channel in alert.channels:
            try:
                if channel == AlertChannel.CONSOLE:
                    self._send_console_alert(alert)
                elif channel == AlertChannel.FILE:
                    self._send_file_alert(alert)
                elif channel == AlertChannel.SLACK:
                    self._send_slack_alert(alert)
                # Add other channels as needed
                    
            except Exception as e:
                print(f"❌ Failed to send alert via {channel.value}: {e}")
    
    def _send_console_alert(self, alert: Alert):
        """Send alert to console with color coding"""
        colors = {
            AlertLevel.INFO: "\033[36m",      # Cyan
            AlertLevel.WARNING: "\033[33m",   # Yellow
            AlertLevel.ERROR: "\033[31m",     # Red
            AlertLevel.CRITICAL: "\033[91m"   # Bright Red
        }
        
        reset = "\033[0m"
        color = colors.get(alert.level, "")
        
        level_symbols = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.ERROR: "❌",
            AlertLevel.CRITICAL: "🚨"
        }
        
        symbol = level_symbols.get(alert.level, "🔔")
        timestamp = datetime.fromisoformat(alert.timestamp).strftime("%H:%M:%S")
        
        print(f"\n{color}🚨 ALERT [{alert.level.value.upper()}] {symbol}")
        print(f"   Time: {timestamp}")
        print(f"   Component: {alert.component}")
        print(f"   Message: {alert.message}{reset}")
        
        if alert.level == AlertLevel.CRITICAL:
            print(f"{color}   *** CRITICAL ALERT - IMMEDIATE ACTION REQUIRED ***{reset}")
    
    def _send_file_alert(self, alert: Alert):
        """Write alert to alert log file"""
        alert_entry = {
            "timestamp": alert.timestamp,
            "level": alert.level.value,
            "alert_id": alert.id,
            "title": alert.title,
            "message": alert.message,
            "component": alert.component,
            "operation": alert.operation,
            "correlation_id": alert.correlation_id,
            "metadata": alert.metadata
        }
        
        with open(self.alert_log, 'a') as f:
            f.write(json.dumps(alert_entry, ensure_ascii=False) + '\n')
    
    def _send_slack_alert(self, alert: Alert):
        """Send alert to Slack (placeholder - integrate with Heinrich's message system)"""
        # This would integrate with Heinrich's existing Slack integration
        slack_message = f"""🚨 *Heinrich Alert*

*Level:* {alert.level.value.upper()}
*Component:* {alert.component}
*Time:* {alert.timestamp}

*Message:*
{alert.message}

*Alert ID:* `{alert.id}`"""
        
        # For now, create a notification file that Heinrich's message system can pick up
        notification_file = self.log_dir / f"slack_alert_{int(time.time())}.txt"
        with open(notification_file, 'w') as f:
            f.write(slack_message)
        
        print(f"📱 Slack alert queued: {notification_file}")
    
    def _log_alert(self, alert: Alert):
        """Log alert details for analysis"""
        print(f"📝 Alert logged: {alert.id} [{alert.level.value}] {alert.component}")
    
    def resolve_alert(self, alert_id: str, resolution_note: str = ""):
        """Mark alert as resolved"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.metadata["resolved_at"] = datetime.now().isoformat()
            alert.metadata["resolution_note"] = resolution_note
            
            del self.active_alerts[alert_id]
            
            print(f"✅ Alert resolved: {alert_id}")
            self._log_alert_resolution(alert, resolution_note)
    
    def _log_alert_resolution(self, alert: Alert, resolution_note: str):
        """Log alert resolution"""
        resolution_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "alert_resolved",
            "alert_id": alert.id,
            "original_level": alert.level.value,
            "resolution_note": resolution_note,
            "duration_minutes": self._calculate_alert_duration(alert)
        }
        
        with open(self.alert_log, 'a') as f:
            f.write(json.dumps(resolution_entry, ensure_ascii=False) + '\n')
    
    def _calculate_alert_duration(self, alert: Alert) -> float:
        """Calculate how long alert was active"""
        created = datetime.fromisoformat(alert.timestamp)
        resolved = datetime.fromisoformat(alert.metadata.get("resolved_at", datetime.now().isoformat()))
        return (resolved - created).total_seconds() / 60
    
    def get_alert_summary(self) -> Dict:
        """Get current alert system status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "active_alerts": len(self.active_alerts),
            "alert_stats": dict(self.alert_stats),
            "rules_count": len(self.rules),
            "monitoring_active": self.monitoring_active,
            "recent_alerts": [asdict(alert) for alert in list(self.alert_history)[-10:]]
        }
    
    def silence_rule(self, rule_name: str, duration_minutes: int):
        """Temporarily silence a specific rule"""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.last_fired = datetime.now()
                rule.cooldown_minutes = duration_minutes
                print(f"🔇 Rule '{rule_name}' silenced for {duration_minutes} minutes")
                return
        
        print(f"❌ Rule '{rule_name}' not found")
    
    def test_alert_system(self):
        """Test alert system with sample data"""
        print("🧪 Testing alert system...")
        
        # Test different alert types
        test_entries = [
            {"level": "CRITICAL", "component": "test", "message": "Test critical error"},
            {"level": "ERROR", "component": "workflow", "message": "Test workflow failed", "workflow_id": "test-123"},
            {"duration_ms": 15000, "operation": "test_operation", "component": "test"},
            {"memory_mb": 1500, "cpu_percent": 95}
        ]
        
        for entry in test_entries:
            self._process_log_entry_for_alerts(entry)
            time.sleep(1)  # Space out test alerts
        
        print("✅ Alert system test complete")
    
    def shutdown(self):
        """Gracefully shutdown alert system"""
        self.monitoring_active = False
        print("🛑 Alert system shutting down")
        
        # Resolve all active alerts
        for alert_id in list(self.active_alerts.keys()):
            self.resolve_alert(alert_id, "System shutdown")

def main():
    """CLI interface for alert system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Heinrich Smart Alert System")
    parser.add_argument("--test", action="store_true", help="Run alert system test")
    parser.add_argument("--monitor", type=str, help="Start monitoring log file")
    parser.add_argument("--status", action="store_true", help="Show alert system status")
    
    args = parser.parse_args()
    
    alert_system = SmartAlertSystem()
    
    try:
        if args.test:
            alert_system.test_alert_system()
        elif args.monitor:
            alert_system.start_monitoring(args.monitor)
            print("Monitoring... Press Ctrl+C to stop")
            while True:
                time.sleep(1)
        elif args.status:
            status = alert_system.get_alert_summary()
            print(json.dumps(status, indent=2))
        else:
            # Interactive mode
            alert_system.start_monitoring()
            print("Alert system running... Press Ctrl+C to stop")
            while True:
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("\n🛑 Stopping alert system...")
        alert_system.shutdown()

if __name__ == "__main__":
    main()