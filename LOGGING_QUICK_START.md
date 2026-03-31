# Heinrich Comprehensive Logging System - Quick Start

## 🚀 One-Time Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Logging System
```bash
python3 scripts/setup_logging_system.py
```

## 🎯 Daily Usage

### Start Development with Full Logging
```bash
# Option 1: Use enhanced workflow (RECOMMENDED)
python3 scripts/enhanced_workflow_with_logging.py start \
    --feature "my-feature" \
    --description "Feature description" \
    --priority high

# Option 2: Start monitoring manually
./start_logging.sh
```

### Monitor in Real-Time
```bash
# View real-time dashboard
python3 scripts/monitoring_dashboard.py

# View logs as they happen
tail -f logs/heinrich_$(date +%Y%m%d).log

# Monitor alerts
python3 scripts/alert_system.py --monitor
```

### Develop with Automatic Logging
```python
# All Heinrich development automatically logs:
from scripts.enhanced_workflow_with_logging import EnhancedHeinrichWorkflow

workflow = EnhancedHeinrichWorkflow()

# Everything is logged automatically
workflow_id = workflow.start_feature_development("feature", "description")
workflow.develop_feature(["file1.py", "file2.py"])
workflow.commit_changes("My changes")
workflow.create_pr_with_review()
```

### Analyze Performance
```bash
# Analyze last 24 hours
python3 scripts/log_analyzer.py --hours 24

# Focus on specific areas
python3 scripts/log_analyzer.py --performance
python3 scripts/log_analyzer.py --errors
python3 scripts/log_analyzer.py --workflows
```

## 📊 Understanding the System

### Log Files Structure
```
logs/
├── heinrich_20260331.jsonl     # Structured logs (machine-readable)
├── heinrich_20260331.log       # Human-readable logs
├── errors_20260331.log         # Error-only logs
├── performance_20260331.jsonl  # Performance metrics
├── alerts_20260331.jsonl       # Alert history
└── reports/                    # Analysis reports
    ├── analysis_report_*.json
    └── workflow_report_*.json
```

### Real-Time Dashboard
The monitoring dashboard shows:
- 📊 **System Metrics**: Operations, errors, response times, resource usage
- 🔄 **Active Workflows**: Current development work and status
- 📝 **Recent Events**: Last 10 log entries with details
- 🚨 **Recent Errors**: Error patterns and frequency
- 🤖 **Agent Communications**: Inter-agent message tracking

### Smart Alerts
Automatic alerts for:
- 🚨 **Critical Errors**: Immediate notification
- ⚠️ **High Error Rate**: More than 5 errors/minute
- 🐌 **Slow Operations**: Operations taking >5 seconds
- 🧠 **Memory Issues**: Usage above 1GB
- 🔄 **Workflow Failures**: Development workflow problems

## 🔧 Customization

### Adjust Alert Thresholds
Edit `config/logging_config.json`:
```json
{
  "alerts": {
    "thresholds": {
      "error_rate_per_minute": 5,
      "memory_usage_mb": 1000,
      "response_time_ms": 5000
    }
  }
}
```

### Add Custom Alert Rules
```python
from scripts.alert_system import SmartAlertSystem, AlertRule, AlertLevel

alert_system = SmartAlertSystem()
alert_system.add_rule(AlertRule(
    name="custom_rule",
    condition=lambda entry: entry.get("component") == "my_component",
    level=AlertLevel.WARNING,
    message_template="Custom alert: {message}"
))
```

### Extend Logging
```python
from scripts.logging_system import get_logger, track_operation

logger = get_logger("my_component")

# Simple logging
logger.info("Operation started", extra={
    'component': 'my_component',
    'operation': 'my_operation'
})

# Track operation performance automatically
with track_operation("my_operation", "my_component"):
    # Your code here - duration automatically tracked
    pass

# Function tracking decorator
@logger.track_function("my_component")
def my_function():
    # Function calls automatically logged with performance metrics
    pass
```

## 🧪 Testing & Debugging

### Run Demo
```bash
python3 demo_logging_system.py
```

### Test Alert System
```bash
python3 scripts/alert_system.py --test
```

### Generate Test Data
```python
from scripts.logging_system import get_logger

logger = get_logger("test")
logger.info("Test info message")
logger.warning("Test warning")
logger.error("Test error")
```

## 📈 Optimization

### Log Retention
- Logs automatically rotate daily
- Keep last 30 days by default
- Adjust in `config/logging_config.json`

### Performance Impact
- Minimal overhead: ~1-2ms per log entry
- Asynchronous processing where possible
- Configurable log levels to reduce noise

### Storage Management
```bash
# Clean old logs (older than 30 days)
find logs/ -name "*.log" -mtime +30 -delete
find logs/ -name "*.jsonl" -mtime +30 -delete

# Archive logs
tar -czf logs_archive_$(date +%Y%m).tar.gz logs/*.log logs/*.jsonl
```

## 🚨 Troubleshooting

### Common Issues

**"No logs appearing"**
- Check file permissions in logs/ directory
- Verify Python path includes scripts/
- Check for errors in console output

**"Dashboard not starting"**
- Install missing dependencies: `pip install psutil pandas`
- Check port availability (dashboard uses terminal)
- Verify log files exist

**"Alerts not working"**
- Check alert system is running: `ps aux | grep alert_system`
- Verify alert thresholds in config
- Check alert log files for errors

### Debug Mode
```bash
# Enable debug logging
export HEINRICH_LOG_LEVEL=DEBUG
python3 scripts/enhanced_workflow_with_logging.py status
```

## 🎯 Best Practices

1. **Always use enhanced workflow** for development
2. **Monitor dashboard during active development**
3. **Check alerts regularly** for issues
4. **Analyze logs weekly** for optimization opportunities
5. **Customize alert thresholds** based on your needs
6. **Keep log retention reasonable** to manage disk space

## 🔗 Integration with Existing Tools

### Linear Integration
- Workflow updates automatically sync with Linear
- Issue status updated based on development progress
- Comments added for major workflow events

### GitHub Integration
- PR creation includes comprehensive logging context
- Commit messages enhanced with workflow metadata
- Review agents receive full development context

### Slack Integration
- Critical alerts sent to configured Slack channels
- Workflow status updates for team awareness
- Error notifications for immediate attention

---

**🎩 Heinrich AI - Enterprise-Level Development with Comprehensive Observability**
