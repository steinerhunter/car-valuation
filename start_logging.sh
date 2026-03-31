#!/bin/bash
# Heinrich Logging System Startup Script

echo "🎩 Starting Heinrich Comprehensive Logging System..."

# Create logs directory if it doesn't exist
mkdir -p logs

# Start monitoring dashboard in background
echo "📊 Starting monitoring dashboard..."
python3 scripts/monitoring_dashboard.py &
DASHBOARD_PID=$!

# Start alert system in background  
echo "🚨 Starting alert system..."
python3 scripts/alert_system.py --monitor &
ALERT_PID=$!

echo "✅ Heinrich Logging System started!"
echo "📊 Dashboard PID: $DASHBOARD_PID"
echo "🚨 Alert System PID: $ALERT_PID"
echo ""
echo "💡 To view logs in real-time:"
echo "   tail -f logs/heinrich_$(date +%Y%m%d).log"
echo ""
echo "💡 To analyze logs:"
echo "   python3 scripts/log_analyzer.py --hours 24"
echo ""
echo "💡 To stop monitoring:"
echo "   kill $DASHBOARD_PID $ALERT_PID"

# Save PIDs for easy stopping
echo $DASHBOARD_PID > logs/dashboard.pid
echo $ALERT_PID > logs/alerts.pid
