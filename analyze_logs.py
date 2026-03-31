#!/usr/bin/env python3
"""
Heinrich Enterprise Logs Analyzer
Analyze and summarize the enterprise development logs
"""

import json
import os
from datetime import datetime
from collections import defaultdict, Counter

def analyze_development_logs():
    """Analyze the development activity logs"""
    
    log_file = '.enterprise-logs/car_valuation_20260331.jsonl'
    
    if not os.path.exists(log_file):
        return None
    
    activities = []
    components = Counter()
    levels = Counter()
    
    with open(log_file, 'r') as f:
        for line in f:
            entry = json.loads(line.strip())
            activities.append(entry)
            components[entry['component']] += 1
            levels[entry['level']] += 1
    
    return {
        'total_activities': len(activities),
        'components': dict(components),
        'levels': dict(levels),
        'timeline': activities
    }

def analyze_performance_logs():
    """Analyze performance metrics"""
    
    perf_file = '.enterprise-logs/performance_20260331.jsonl'
    
    if not os.path.exists(perf_file):
        return None
    
    metrics = []
    
    with open(perf_file, 'r') as f:
        for line in f:
            entry = json.loads(line.strip())
            metrics.append(entry['metrics'])
    
    if not metrics:
        return None
    
    # Calculate averages
    avg_analysis_time = sum(m['analysis_time_ms'] for m in metrics) / len(metrics)
    avg_vehicles_per_sec = sum(m['vehicles_per_second'] for m in metrics) / len(metrics)
    avg_memory_usage = sum(m['memory_usage_mb'] for m in metrics) / len(metrics)
    avg_confidence = sum(m['confidence_score'] for m in metrics) / len(metrics)
    total_cache_hits = sum(m['cache_hits'] for m in metrics)
    
    return {
        'total_measurements': len(metrics),
        'averages': {
            'analysis_time_ms': round(avg_analysis_time, 3),
            'vehicles_per_second': int(avg_vehicles_per_sec),
            'memory_usage_mb': round(avg_memory_usage, 1),
            'confidence_score': round(avg_confidence, 3)
        },
        'totals': {
            'cache_hits': total_cache_hits
        }
    }

def analyze_alerts():
    """Analyze alert system logs"""
    
    alert_file = '.enterprise-logs/alerts/alerts_20260331.jsonl'
    
    if not os.path.exists(alert_file):
        return None
    
    alerts = []
    alert_types = Counter()
    alert_levels = Counter()
    
    with open(alert_file, 'r') as f:
        for line in f:
            entry = json.loads(line.strip())
            alerts.append(entry)
            alert_types[entry['type']] += 1
            alert_levels[entry['level']] += 1
    
    resolved_count = sum(1 for a in alerts if a.get('resolved', False))
    
    return {
        'total_alerts': len(alerts),
        'resolved_alerts': resolved_count,
        'resolution_rate': round(resolved_count / len(alerts) * 100, 1) if alerts else 0,
        'alert_types': dict(alert_types),
        'alert_levels': dict(alert_levels)
    }

def generate_analysis_report():
    """Generate comprehensive analysis report"""
    
    print("🎩 Heinrich Enterprise Logs Analysis")
    print("=" * 50)
    
    # Development Activity Analysis
    dev_analysis = analyze_development_logs()
    if dev_analysis:
        print("\n📋 DEVELOPMENT ACTIVITY ANALYSIS:")
        print(f"  Total Activities: {dev_analysis['total_activities']}")
        print(f"  Components Active:")
        for component, count in dev_analysis['components'].items():
            print(f"    • {component}: {count} activities")
        
        print(f"  Activity Levels:")
        for level, count in dev_analysis['levels'].items():
            print(f"    • {level}: {count}")
    
    # Performance Analysis
    perf_analysis = analyze_performance_logs()
    if perf_analysis:
        print(f"\n📊 PERFORMANCE ANALYSIS:")
        print(f"  Total Measurements: {perf_analysis['total_measurements']}")
        print(f"  Average Performance:")
        for metric, value in perf_analysis['averages'].items():
            print(f"    • {metric}: {value}")
        print(f"  Cache Efficiency: {perf_analysis['totals']['cache_hits']} total hits")
    
    # Alert Analysis
    alert_analysis = analyze_alerts()
    if alert_analysis:
        print(f"\n🚨 ALERT SYSTEM ANALYSIS:")
        print(f"  Total Alerts: {alert_analysis['total_alerts']}")
        print(f"  Resolved: {alert_analysis['resolved_alerts']} ({alert_analysis['resolution_rate']}%)")
        print(f"  Alert Types:")
        for alert_type, count in alert_analysis['alert_types'].items():
            print(f"    • {alert_type}: {count}")
    
    # Summary Report
    summary_file = '.enterprise-logs/reports/daily_summary_20260331.json'
    if os.path.exists(summary_file):
        with open(summary_file, 'r') as f:
            summary = json.load(f)
        
        print(f"\n📈 PROJECT SUMMARY:")
        print(f"  Project: {summary['project']}")
        print(f"  Date: {summary['date']}")
        print(f"  Active Features: {', '.join(summary['feature_development']['active_features'])}")
        print(f"  Status: {summary['feature_development']['completion_status']}")
        
        print(f"\n🎯 ACHIEVEMENTS:")
        achievements = summary['feature_development']['performance_achievements']
        for key, value in achievements.items():
            print(f"    • {key.replace('_', ' ').title()}: {value}")
        
        print(f"\n🔧 SYSTEM STATUS:")
        for system, status in summary['system_health'].items():
            print(f"    • {system.replace('_', ' ').title()}: {status}")

def show_latest_activities():
    """Show the latest development activities"""
    
    print(f"\n⏰ LATEST DEVELOPMENT ACTIVITIES:")
    print("-" * 40)
    
    log_file = '.enterprise-logs/car_valuation_20260331.jsonl'
    if os.path.exists(log_file):
        activities = []
        with open(log_file, 'r') as f:
            for line in f:
                activities.append(json.loads(line.strip()))
        
        # Show last 3 activities
        for activity in activities[-3:]:
            timestamp = datetime.fromisoformat(activity['timestamp']).strftime('%H:%M:%S')
            print(f"[{timestamp}] {activity['level']} | {activity['component']} | {activity['message']}")

def main():
    """Main analysis function"""
    
    # Check if logs exist
    if not os.path.exists('.enterprise-logs'):
        print("❌ No enterprise logs found. Run generate_demo_logs.py first.")
        return
    
    # Generate comprehensive analysis
    generate_analysis_report()
    
    # Show latest activities
    show_latest_activities()
    
    print(f"\n🎯 Analysis complete! Logs location: .enterprise-logs/")

if __name__ == "__main__":
    main()