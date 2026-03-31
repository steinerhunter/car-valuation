#!/bin/bash
# Stop car-valuation Enterprise Logging

echo "🛑 Stopping Enterprise Logging for car-valuation..."

cd "/home/omer/.openclaw/workspace/skills/car-valuation"

# Stop processes
if [ -f .enterprise-logs/dashboard.pid ]; then
    kill $(cat .enterprise-logs/dashboard.pid) 2>/dev/null
    rm .enterprise-logs/dashboard.pid
    echo "📊 Dashboard stopped"
fi

if [ -f .enterprise-logs/alerts.pid ]; then
    kill $(cat .enterprise-logs/alerts.pid) 2>/dev/null  
    rm .enterprise-logs/alerts.pid
    echo "🚨 Alert system stopped"
fi

echo "✅ Enterprise Logging System stopped"
