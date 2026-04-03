#!/usr/bin/env python3
"""
Heinrich Log Analysis Tools
=========================

Advanced log analysis and debugging tools for Heinrich's multi-agent workflow:
- Performance analysis and bottleneck detection
- Error correlation and root cause analysis
- Workflow timeline reconstruction
- Agent communication patterns
- Resource usage trends
- Automated insights and recommendations
"""

import json
import re
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import pandas as pd

class LogAnalyzer:
    """
    Comprehensive log analysis system for debugging and optimization
    """
    
    def __init__(self, log_dir: str = None):
        self.log_dir = Path(log_dir or "/home/omer/.openclaw/workspace/skills/car-valuation/logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Analysis results storage
        self.log_entries = []
        self.error_patterns = defaultdict(int)
        self.performance_data = []
        self.workflow_timelines = {}
        self.agent_communications = []
        
        print("🔍 Heinrich Log Analyzer initialized")
        print(f"📂 Analyzing logs from: {self.log_dir}")
    
    def load_logs(self, date_filter: str = None, hours: int = 24):
        """
        Load and parse log files
        
        Args:
            date_filter: Date in YYYYMMDD format, defaults to today
            hours: Number of hours to look back
        """
        if not date_filter:
            date_filter = datetime.now().strftime('%Y%m%d')
        
        log_file = self.log_dir / f"heinrich_{date_filter}.jsonl"
        
        if not log_file.exists():
            print(f"❌ Log file not found: {log_file}")
            return False
        
        print(f"📖 Loading logs from: {log_file}")
        
        # Load entries
        cutoff_time = datetime.now() - timedelta(hours=hours)
        loaded_count = 0
        
        self.log_entries = []
        
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    
                    # Parse timestamp
                    timestamp_str = entry.get('timestamp', '')
                    if timestamp_str:
                        entry_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                        if entry_time >= cutoff_time:
                            self.log_entries.append(entry)
                            loaded_count += 1
                    
                except json.JSONDecodeError:
                    continue
        
        print(f"✅ Loaded {loaded_count} log entries from last {hours} hours")
        self._categorize_entries()
        return True
    
    def _categorize_entries(self):
        """Categorize log entries for analysis"""
        self.error_patterns = defaultdict(int)
        self.performance_data = []
        self.workflow_timelines = {}
        self.agent_communications = []
        
        for entry in self.log_entries:
            # Categorize errors
            if entry.get('level') in ['ERROR', 'CRITICAL']:
                error_type = entry.get('error_type', 'Unknown')
                component = entry.get('component', 'Unknown')
                self.error_patterns[f"{component}:{error_type}"] += 1
            
            # Collect performance data
            if entry.get('duration_ms'):
                self.performance_data.append({
                    'timestamp': entry.get('timestamp'),
                    'operation': entry.get('operation'),
                    'component': entry.get('component'),
                    'duration_ms': entry.get('duration_ms'),
                    'memory_mb': entry.get('memory_mb'),
                    'cpu_percent': entry.get('cpu_percent')
                })
            
            # Track workflow timelines
            workflow_id = entry.get('workflow_id')
            if workflow_id:
                if workflow_id not in self.workflow_timelines:
                    self.workflow_timelines[workflow_id] = []
                self.workflow_timelines[workflow_id].append(entry)
            
            # Track agent communications
            if entry.get('component') == 'agent_communication':
                self.agent_communications.append(entry)
    
    def analyze_performance(self) -> Dict:
        """Comprehensive performance analysis"""
        if not self.performance_data:
            return {"status": "no_performance_data"}
        
        print("⚡ Analyzing performance metrics...")
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(self.performance_data)
        
        analysis = {
            "total_operations": len(df),
            "time_range": {
                "start": df['timestamp'].min(),
                "end": df['timestamp'].max()
            },
            "duration_stats": {
                "mean_ms": df['duration_ms'].mean(),
                "median_ms": df['duration_ms'].median(),
                "p95_ms": df['duration_ms'].quantile(0.95),
                "p99_ms": df['duration_ms'].quantile(0.99),
                "max_ms": df['duration_ms'].max(),
                "min_ms": df['duration_ms'].min()
            },
            "component_performance": {},
            "operation_performance": {},
            "slowest_operations": [],
            "resource_usage": {},
            "bottlenecks": []
        }
        
        # Performance by component
        for component in df['component'].unique():
            if pd.isna(component):
                continue
            component_df = df[df['component'] == component]
            analysis["component_performance"][component] = {
                "count": len(component_df),
                "avg_duration_ms": component_df['duration_ms'].mean(),
                "max_duration_ms": component_df['duration_ms'].max()
            }
        
        # Performance by operation
        for operation in df['operation'].unique():
            if pd.isna(operation):
                continue
            operation_df = df[df['operation'] == operation]
            analysis["operation_performance"][operation] = {
                "count": len(operation_df),
                "avg_duration_ms": operation_df['duration_ms'].mean(),
                "max_duration_ms": operation_df['duration_ms'].max()
            }
        
        # Slowest operations (top 10)
        slowest = df.nlargest(10, 'duration_ms')
        analysis["slowest_operations"] = [
            {
                "operation": row['operation'],
                "component": row['component'], 
                "duration_ms": row['duration_ms'],
                "timestamp": row['timestamp']
            }
            for _, row in slowest.iterrows()
        ]
        
        # Resource usage analysis
        if 'memory_mb' in df.columns:
            analysis["resource_usage"]["memory"] = {
                "avg_mb": df['memory_mb'].mean(),
                "max_mb": df['memory_mb'].max(),
                "trend": "increasing" if df['memory_mb'].iloc[-1] > df['memory_mb'].iloc[0] else "stable"
            }
        
        # Identify bottlenecks
        bottlenecks = []
        
        # Operations consistently above 1 second
        slow_operations = df[df['duration_ms'] > 1000]
        if not slow_operations.empty:
            for operation in slow_operations['operation'].value_counts().head(5).index:
                bottlenecks.append({
                    "type": "slow_operation",
                    "operation": operation,
                    "avg_duration_ms": slow_operations[slow_operations['operation'] == operation]['duration_ms'].mean(),
                    "frequency": len(slow_operations[slow_operations['operation'] == operation])
                })
        
        analysis["bottlenecks"] = bottlenecks
        
        return analysis
    
    def analyze_errors(self) -> Dict:
        """Comprehensive error analysis"""
        errors = [entry for entry in self.log_entries if entry.get('level') in ['ERROR', 'CRITICAL']]
        
        if not errors:
            return {"status": "no_errors", "message": "No errors found in log range"}
        
        print("🚨 Analyzing error patterns...")
        
        analysis = {
            "total_errors": len(errors),
            "error_rate_per_hour": len(errors) / (len(self.log_entries) / 3600) if self.log_entries else 0,
            "error_patterns": dict(self.error_patterns),
            "error_timeline": [],
            "top_error_components": {},
            "error_correlation": {},
            "root_causes": []
        }
        
        # Error timeline (group by hour)
        timeline = defaultdict(int)
        for error in errors:
            timestamp = datetime.fromisoformat(error.get('timestamp', ''))
            hour_key = timestamp.strftime('%Y-%m-%d %H:00')
            timeline[hour_key] += 1
        
        analysis["error_timeline"] = [{"hour": k, "count": v} for k, v in sorted(timeline.items())]
        
        # Top error components
        component_errors = Counter(error.get('component', 'Unknown') for error in errors)
        analysis["top_error_components"] = dict(component_errors.most_common(10))
        
        # Error correlation analysis
        # Look for patterns where errors occur together
        error_sequences = []
        for i in range(len(errors) - 1):
            curr_error = errors[i]
            next_error = errors[i + 1]
            
            curr_time = datetime.fromisoformat(curr_error.get('timestamp', ''))
            next_time = datetime.fromisoformat(next_error.get('timestamp', ''))
            
            # If errors occur within 5 minutes, they might be related
            if (next_time - curr_time).total_seconds() <= 300:
                error_sequences.append({
                    "first": {
                        "component": curr_error.get('component'),
                        "operation": curr_error.get('operation'),
                        "message": curr_error.get('message', '')[:100]
                    },
                    "second": {
                        "component": next_error.get('component'),
                        "operation": next_error.get('operation'), 
                        "message": next_error.get('message', '')[:100]
                    },
                    "time_gap_seconds": (next_time - curr_time).total_seconds()
                })
        
        analysis["error_correlation"]["sequences"] = error_sequences[:10]  # Top 10
        
        # Identify potential root causes
        root_causes = []
        
        # Frequent error patterns
        for pattern, count in self.error_patterns.most_common(5):
            if count > 1:
                root_causes.append({
                    "type": "frequent_pattern",
                    "pattern": pattern,
                    "occurrences": count,
                    "recommendation": f"Investigate {pattern} - occurs {count} times"
                })
        
        # Memory-related errors
        memory_errors = [e for e in errors if 'memory' in e.get('message', '').lower()]
        if memory_errors:
            root_causes.append({
                "type": "memory_issue",
                "count": len(memory_errors),
                "recommendation": "Check memory usage patterns and potential leaks"
            })
        
        analysis["root_causes"] = root_causes
        
        return analysis
    
    def analyze_workflows(self) -> Dict:
        """Analyze workflow execution patterns"""
        if not self.workflow_timelines:
            return {"status": "no_workflows", "message": "No workflows found in logs"}
        
        print("🔄 Analyzing workflow patterns...")
        
        analysis = {
            "total_workflows": len(self.workflow_timelines),
            "workflow_details": {},
            "average_duration": 0,
            "success_rate": 0,
            "failure_patterns": [],
            "bottleneck_steps": []
        }
        
        total_duration = 0
        successful_workflows = 0
        step_durations = defaultdict(list)
        
        for workflow_id, events in self.workflow_timelines.items():
            # Sort events by timestamp
            events.sort(key=lambda x: x.get('timestamp', ''))
            
            if not events:
                continue
            
            start_time = datetime.fromisoformat(events[0].get('timestamp', ''))
            end_time = datetime.fromisoformat(events[-1].get('timestamp', ''))
            
            duration_seconds = (end_time - start_time).total_seconds()
            total_duration += duration_seconds
            
            # Check if workflow was successful (no errors in final steps)
            final_events = events[-3:]  # Check last 3 events
            has_errors = any(e.get('level') in ['ERROR', 'CRITICAL'] for e in final_events)
            
            if not has_errors:
                successful_workflows += 1
            
            # Analyze step durations
            for i in range(len(events) - 1):
                curr_event = events[i]
                next_event = events[i + 1]
                
                curr_time = datetime.fromisoformat(curr_event.get('timestamp', ''))
                next_time = datetime.fromisoformat(next_event.get('timestamp', ''))
                
                step_duration = (next_time - curr_time).total_seconds()
                operation = curr_event.get('operation', 'unknown')
                step_durations[operation].append(step_duration)
            
            analysis["workflow_details"][workflow_id] = {
                "duration_seconds": duration_seconds,
                "steps": len(events),
                "successful": not has_errors,
                "start_time": events[0].get('timestamp'),
                "end_time": events[-1].get('timestamp')
            }
        
        # Calculate averages
        if self.workflow_timelines:
            analysis["average_duration"] = total_duration / len(self.workflow_timelines)
            analysis["success_rate"] = successful_workflows / len(self.workflow_timelines)
        
        # Identify bottleneck steps
        bottlenecks = []
        for step, durations in step_durations.items():
            if len(durations) > 1:  # At least 2 occurrences
                avg_duration = statistics.mean(durations)
                if avg_duration > 5:  # Steps taking more than 5 seconds
                    bottlenecks.append({
                        "step": step,
                        "avg_duration_seconds": avg_duration,
                        "max_duration_seconds": max(durations),
                        "occurrences": len(durations)
                    })
        
        analysis["bottleneck_steps"] = sorted(bottlenecks, 
                                             key=lambda x: x["avg_duration_seconds"], 
                                             reverse=True)[:10]
        
        return analysis
    
    def analyze_agent_communications(self) -> Dict:
        """Analyze inter-agent communication patterns"""
        if not self.agent_communications:
            return {"status": "no_communications", "message": "No agent communications found"}
        
        print("🤖 Analyzing agent communication patterns...")
        
        communication_patterns = defaultdict(int)
        message_types = defaultdict(int)
        
        for comm in self.agent_communications:
            metadata = comm.get('metadata', {})
            from_agent = metadata.get('from_agent', 'unknown')
            to_agent = metadata.get('to_agent', 'unknown') 
            message_type = comm.get('operation', 'unknown')
            
            communication_patterns[f"{from_agent} → {to_agent}"] += 1
            message_types[message_type] += 1
        
        analysis = {
            "total_communications": len(self.agent_communications),
            "communication_patterns": dict(communication_patterns),
            "message_types": dict(message_types),
            "most_active_agents": {},
            "communication_timeline": []
        }
        
        return analysis
    
    def generate_insights(self, performance_analysis: Dict, error_analysis: Dict, workflow_analysis: Dict) -> List[str]:
        """Generate actionable insights from analysis"""
        insights = []
        
        # Performance insights
        if performance_analysis.get("duration_stats"):
            p95_duration = performance_analysis["duration_stats"]["p95_ms"]
            if p95_duration > 2000:
                insights.append(f"🐌 95% of operations take longer than 2 seconds (P95: {p95_duration:.1f}ms). Consider optimization.")
        
        # Memory insights
        resource_usage = performance_analysis.get("resource_usage", {})
        if "memory" in resource_usage:
            if resource_usage["memory"]["max_mb"] > 1000:
                insights.append(f"🧠 High memory usage detected: {resource_usage['memory']['max_mb']:.1f}MB. Check for memory leaks.")
        
        # Error insights
        if error_analysis.get("total_errors", 0) > 0:
            error_rate = error_analysis.get("error_rate_per_hour", 0)
            if error_rate > 5:
                insights.append(f"🚨 High error rate: {error_rate:.1f} errors per hour. Review error patterns.")
        
        # Workflow insights
        if workflow_analysis.get("success_rate", 1.0) < 0.8:
            insights.append(f"⚠️ Low workflow success rate: {workflow_analysis['success_rate']:.1%}. Check failure patterns.")
        
        # Bottleneck insights
        bottlenecks = performance_analysis.get("bottlenecks", [])
        if bottlenecks:
            worst_bottleneck = bottlenecks[0]
            insights.append(f"🚫 Bottleneck detected: {worst_bottleneck['operation']} averages {worst_bottleneck['avg_duration_ms']:.1f}ms")
        
        return insights
    
    def run_full_analysis(self, hours: int = 24) -> Dict:
        """Run comprehensive analysis"""
        print("🔬 Starting comprehensive log analysis...")
        
        # Load logs
        if not self.load_logs(hours=hours):
            return {"error": "Failed to load logs"}
        
        # Run all analyses
        performance = self.analyze_performance()
        errors = self.analyze_errors()
        workflows = self.analyze_workflows()
        communications = self.analyze_agent_communications()
        
        # Generate insights
        insights = self.generate_insights(performance, errors, workflows)
        
        # Compile final report
        report = {
            "analysis_timestamp": datetime.now().isoformat(),
            "time_range_hours": hours,
            "log_entries_analyzed": len(self.log_entries),
            "performance": performance,
            "errors": errors,
            "workflows": workflows,
            "communications": communications,
            "insights": insights,
            "summary": {
                "health_status": "healthy" if not errors.get("total_errors", 0) else "issues_detected",
                "performance_status": "good" if performance.get("duration_stats", {}).get("p95_ms", 0) < 2000 else "needs_optimization",
                "error_count": errors.get("total_errors", 0),
                "workflow_success_rate": workflows.get("success_rate", 1.0)
            }
        }
        
        # Save report
        report_file = self.log_dir / f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Analysis complete! Report saved to: {report_file}")
        
        return report
    
    def print_summary(self, report: Dict):
        """Print human-readable analysis summary"""
        print("\n" + "="*80)
        print("🔍 HEINRICH LOG ANALYSIS SUMMARY")
        print("="*80)
        
        summary = report.get("summary", {})
        print(f"📊 Health Status: {summary.get('health_status', 'unknown')}")
        print(f"⚡ Performance: {summary.get('performance_status', 'unknown')}")
        print(f"❌ Errors Found: {summary.get('error_count', 0)}")
        print(f"✅ Workflow Success Rate: {summary.get('workflow_success_rate', 0):.1%}")
        
        # Print insights
        insights = report.get("insights", [])
        if insights:
            print(f"\n💡 KEY INSIGHTS:")
            for i, insight in enumerate(insights[:10], 1):
                print(f"   {i}. {insight}")
        
        # Print top issues
        errors = report.get("errors", {})
        if errors.get("total_errors", 0) > 0:
            print(f"\n🚨 TOP ERROR PATTERNS:")
            error_patterns = errors.get("error_patterns", {})
            for i, (pattern, count) in enumerate(list(error_patterns.items())[:5], 1):
                print(f"   {i}. {pattern}: {count} occurrences")
        
        # Print performance bottlenecks
        performance = report.get("performance", {})
        bottlenecks = performance.get("bottlenecks", [])
        if bottlenecks:
            print(f"\n🐌 PERFORMANCE BOTTLENECKS:")
            for i, bottleneck in enumerate(bottlenecks[:5], 1):
                print(f"   {i}. {bottleneck['operation']}: {bottleneck['avg_duration_ms']:.1f}ms average")
        
        print("\n" + "="*80)

def main():
    """CLI interface for log analysis"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Heinrich Log Analysis")
    parser.add_argument("--hours", type=int, default=24, help="Hours of logs to analyze")
    parser.add_argument("--performance", action="store_true", help="Focus on performance analysis")
    parser.add_argument("--errors", action="store_true", help="Focus on error analysis")
    parser.add_argument("--workflows", action="store_true", help="Focus on workflow analysis")
    
    args = parser.parse_args()
    
    analyzer = LogAnalyzer()
    
    if args.performance:
        analyzer.load_logs(hours=args.hours)
        performance = analyzer.analyze_performance()
        print(json.dumps(performance, indent=2))
    elif args.errors:
        analyzer.load_logs(hours=args.hours)
        errors = analyzer.analyze_errors()
        print(json.dumps(errors, indent=2))
    elif args.workflows:
        analyzer.load_logs(hours=args.hours)
        workflows = analyzer.analyze_workflows()
        print(json.dumps(workflows, indent=2))
    else:
        # Full analysis
        report = analyzer.run_full_analysis(hours=args.hours)
        analyzer.print_summary(report)

if __name__ == "__main__":
    main()