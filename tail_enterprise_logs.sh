#!/bin/bash

# Heinrich Enterprise Logs - Real-time Monitoring
echo "🎩 Heinrich Enterprise Logs - Real-time Monitoring"
echo "=================================================="

# Check if logs directory exists
if [ ! -d ".enterprise-logs" ]; then
    echo "❌ No enterprise logs found. Run generate_demo_logs.py first."
    exit 1
fi

echo "📂 Available log files:"
find .enterprise-logs -name "*.log" -o -name "*.jsonl" | head -10

echo -e "\n📋 Human-readable log (latest entries):"
echo "========================================="
if [ -f ".enterprise-logs/car_valuation_20260331.log" ]; then
    tail -10 .enterprise-logs/car_valuation_20260331.log
else
    echo "No readable log file found"
fi

echo -e "\n📊 Performance metrics (latest):"
echo "================================="
if [ -f ".enterprise-logs/performance_20260331.jsonl" ]; then
    echo "Latest performance entry:"
    tail -1 .enterprise-logs/performance_20260331.jsonl | python3 -c "
import json, sys
try:
    data = json.loads(sys.stdin.read())
    print(f'⚡ Speed: {data[\"metrics\"][\"vehicles_per_second\"]} vehicles/sec')
    print(f'💾 Memory: {data[\"metrics\"][\"memory_usage_mb\"]} MB')
    print(f'🎯 Confidence: {data[\"metrics\"][\"confidence_score\"]:.3f}')
    print(f'⏰ Time: {data[\"timestamp\"]}')
except:
    print('Error parsing performance data')
"
fi

echo -e "\n🚨 Recent alerts:"
echo "=================="
if [ -f ".enterprise-logs/alerts/alerts_20260331.jsonl" ]; then
    tail -2 .enterprise-logs/alerts/alerts_20260331.jsonl | python3 -c "
import json, sys
for line in sys.stdin:
    try:
        alert = json.loads(line.strip())
        status = '✅' if alert.get('resolved', False) else '⚠️'
        print(f'{status} {alert[\"level\"]} | {alert[\"type\"]} | {alert[\"message\"]}')
    except:
        pass
"
fi

echo -e "\n🎯 Quick Summary:"
echo "================="
python3 -c "
import json, os
try:
    with open('.enterprise-logs/reports/daily_summary_20260331.json', 'r') as f:
        summary = json.load(f)
    
    print(f'📊 Project: {summary[\"project\"]}')
    print(f'📈 Features: {summary[\"feature_development\"][\"completion_status\"]}')
    print(f'🚀 Performance: {summary[\"feature_development\"][\"performance_achievements\"][\"processing_speed\"]}')
    print(f'⭐ Quality Score: {summary[\"feature_development\"][\"performance_achievements\"][\"code_quality_score\"]}')
    print(f'📝 Files Created: {summary[\"metrics\"][\"files_created\"]}')
    print(f'💻 Lines of Code: {summary[\"metrics\"][\"lines_of_code\"]}')
except:
    print('Summary not available')
"

echo -e "\n💡 Monitor commands:"
echo "===================="
echo "📖 View full readable log: cat .enterprise-logs/car_valuation_20260331.log"
echo "📊 Analyze logs: python3 analyze_logs.py"
echo "🔍 Watch performance: tail -f .enterprise-logs/performance_20260331.jsonl"
echo "🚨 Monitor alerts: tail -f .enterprise-logs/alerts/alerts_20260331.jsonl"