#!/bin/bash
# car-valuation Enterprise Logging System

echo "🎩 Starting Enterprise Logging for car-valuation..."
echo "Project Type: python"

cd "/home/omer/.openclaw/workspace/skills/car-valuation"

# Ensure logs directory exists
mkdir -p .enterprise-logs

# Start monitoring dashboard
echo "📊 Starting monitoring dashboard..."
python3 .enterprise-scripts/monitoring_dashboard.py --project-path . &
DASHBOARD_PID=$!

# Start alert system
echo "🚨 Starting alert system..."  
python3 .enterprise-scripts/alert_system.py --project-path . --monitor &
ALERT_PID=$!

# Save PIDs
echo $DASHBOARD_PID > .enterprise-logs/dashboard.pid
echo $ALERT_PID > .enterprise-logs/alerts.pid

echo "✅ Enterprise Logging System started!"
echo ""
echo "💡 View logs: tail -f .enterprise-logs/car-valuation_$(date +%Y%m%d).log"
echo "💡 Analyze: python3 .enterprise-scripts/log_analyzer.py --hours 24"
echo "💡 Stop: ./enterprise_stop.sh"
