#!/bin/bash
# Heinrich Logging System Stop Script

echo "🛑 Stopping Heinrich Logging System..."

# Stop dashboard if running
if [ -f logs/dashboard.pid ]; then
    DASHBOARD_PID=$(cat logs/dashboard.pid)
    if ps -p $DASHBOARD_PID > /dev/null; then
        kill $DASHBOARD_PID
        echo "📊 Dashboard stopped"
    fi
    rm logs/dashboard.pid
fi

# Stop alert system if running
if [ -f logs/alerts.pid ]; then
    ALERT_PID=$(cat logs/alerts.pid)
    if ps -p $ALERT_PID > /dev/null; then
        kill $ALERT_PID
        echo "🚨 Alert system stopped"
    fi
    rm logs/alerts.pid
fi

echo "✅ Heinrich Logging System stopped"
