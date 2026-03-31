#!/usr/bin/env python3
"""
Heinrich Multi-Agent Development Logging System
============================================

Comprehensive logging infrastructure with real-time monitoring,
structured logging, performance metrics, and intelligent alerting.

Features:
- Multi-level logging (DEBUG → CRITICAL)
- Structured JSON logging with metadata
- Real-time monitoring and alerts
- Performance tracking and profiling
- Workflow correlation across agents
- Error aggregation and analysis
- Resource usage monitoring
"""

import os
import json
import logging
import time
import traceback
import psutil
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
from dataclasses import dataclass, asdict
import functools

# Logging levels with colors for console output
LOG_COLORS = {
    'DEBUG': '\033[36m',     # Cyan
    'INFO': '\033[32m',      # Green
    'WARNING': '\033[33m',   # Yellow
    'ERROR': '\033[31m',     # Red
    'CRITICAL': '\033[91m',  # Bright Red
    'RESET': '\033[0m'       # Reset
}

@dataclass
class LogEntry:
    """Structured log entry with comprehensive metadata"""
    timestamp: str
    level: str
    logger_name: str
    message: str
    agent_id: str = "heinrich"
    session_id: str = "main"
    workflow_id: Optional[str] = None
    component: str = "general"
    operation: Optional[str] = None
    duration_ms: Optional[float] = None
    memory_mb: Optional[float] = None
    cpu_percent: Optional[float] = None
    error_type: Optional[str] = None
    error_traceback: Optional[str] = None
    metadata: Dict[str, Any] = None
    correlation_id: Optional[str] = None

class HeinrichLogger:
    """
    Advanced logging system with real-time monitoring and analytics
    """
    
    def __init__(self, name: str, log_dir: str = None):
        self.name = name
        self.log_dir = Path(log_dir or "/home/omer/.openclaw/workspace/skills/car-valuation/logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Core logging setup
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Performance tracking
        self.operation_stack = []
        self.performance_log = []
        
        # Real-time monitoring
        self.monitoring_active = False
        self.alert_thresholds = {
            'error_rate': 0.1,      # 10% error rate
            'memory_mb': 1000,      # 1GB memory usage
            'response_time_ms': 5000  # 5 second response time
        }
        
        # Setup handlers
        self._setup_handlers()
        
        # Start background monitoring
        self._start_monitoring()
        
        # Session metadata
        self.session_metadata = {
            'started_at': datetime.now().isoformat(),
            'process_id': os.getpid(),
            'hostname': os.uname().nodename if hasattr(os, 'uname') else 'unknown'
        }
        
        self.info("🚀 Heinrich Logger initialized", extra={
            'component': 'logging_system',
            'operation': 'init',
            'metadata': self.session_metadata
        })
    
    def _setup_handlers(self):
        """Setup multiple log handlers for different output formats"""
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # 1. Detailed JSON file handler
        json_handler = logging.FileHandler(
            self.log_dir / f"heinrich_{datetime.now().strftime('%Y%m%d')}.jsonl"
        )
        json_handler.setLevel(logging.DEBUG)
        json_handler.setFormatter(self._get_json_formatter())
        
        # 2. Human-readable file handler
        text_handler = logging.FileHandler(
            self.log_dir / f"heinrich_{datetime.now().strftime('%Y%m%d')}.log"
        )
        text_handler.setLevel(logging.INFO)
        text_handler.setFormatter(self._get_text_formatter())
        
        # 3. Console handler with colors
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(self._get_console_formatter())
        
        # 4. Error-only handler for quick debugging
        error_handler = logging.FileHandler(
            self.log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(self._get_text_formatter())
        
        # 5. Performance metrics handler
        perf_handler = logging.FileHandler(
            self.log_dir / f"performance_{datetime.now().strftime('%Y%m%d')}.jsonl"
        )
        perf_handler.setLevel(logging.DEBUG)
        perf_handler.addFilter(lambda record: hasattr(record, 'duration_ms'))
        perf_handler.setFormatter(self._get_json_formatter())
        
        # Add all handlers
        self.logger.addHandler(json_handler)
        self.logger.addHandler(text_handler)
        self.logger.addHandler(console_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(perf_handler)
    
    def _get_json_formatter(self):
        """JSON formatter for structured logging"""
        class JSONFormatter(logging.Formatter):
            def format(self, record):
                # Get system metrics
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                cpu_percent = process.cpu_percent()
                
                # Create log entry
                entry = LogEntry(
                    timestamp=datetime.fromtimestamp(record.created).isoformat(),
                    level=record.levelname,
                    logger_name=record.name,
                    message=record.getMessage(),
                    agent_id=getattr(record, 'agent_id', 'heinrich'),
                    session_id=getattr(record, 'session_id', 'main'),
                    workflow_id=getattr(record, 'workflow_id', None),
                    component=getattr(record, 'component', 'general'),
                    operation=getattr(record, 'operation', None),
                    duration_ms=getattr(record, 'duration_ms', None),
                    memory_mb=memory_mb,
                    cpu_percent=cpu_percent,
                    error_type=getattr(record, 'error_type', None),
                    error_traceback=getattr(record, 'error_traceback', None),
                    metadata=getattr(record, 'metadata', None),
                    correlation_id=getattr(record, 'correlation_id', None)
                )
                
                return json.dumps(asdict(entry), ensure_ascii=False)
        
        return JSONFormatter()
    
    def _get_text_formatter(self):
        """Human-readable formatter"""
        return logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def _get_console_formatter(self):
        """Colored console formatter"""
        class ColoredFormatter(logging.Formatter):
            def format(self, record):
                color = LOG_COLORS.get(record.levelname, '')
                reset = LOG_COLORS['RESET']
                
                # Add component info if available
                component = getattr(record, 'component', '')
                comp_info = f" [{component}]" if component else ""
                
                # Add operation info if available
                operation = getattr(record, 'operation', '')
                op_info = f" {operation}" if operation else ""
                
                formatted = f"{color}%(levelname)-8s{reset} | %(name)s{comp_info}{op_info} | %(message)s"
                
                formatter = logging.Formatter(formatted, datefmt='%H:%M:%S')
                return formatter.format(record)
        
        return ColoredFormatter()
    
    def _start_monitoring(self):
        """Start background monitoring thread"""
        def monitor():
            self.monitoring_active = True
            while self.monitoring_active:
                try:
                    self._check_system_health()
                    time.sleep(10)  # Check every 10 seconds
                except Exception as e:
                    self.error(f"Monitoring error: {e}", extra={'component': 'monitoring'})
                    time.sleep(30)  # Back off on error
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def _check_system_health(self):
        """Monitor system health and send alerts"""
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        cpu_percent = process.cpu_percent()
        
        # Check memory usage
        if memory_mb > self.alert_thresholds['memory_mb']:
            self.warning(
                f"High memory usage: {memory_mb:.1f} MB",
                extra={
                    'component': 'monitoring',
                    'operation': 'memory_check',
                    'metadata': {'threshold': self.alert_thresholds['memory_mb']}
                }
            )
        
        # Check recent error rate
        recent_errors = self._get_recent_error_rate()
        if recent_errors > self.alert_thresholds['error_rate']:
            self.warning(
                f"High error rate: {recent_errors:.1%}",
                extra={
                    'component': 'monitoring',
                    'operation': 'error_rate_check',
                    'metadata': {'error_rate': recent_errors}
                }
            )
    
    def _get_recent_error_rate(self):
        """Calculate error rate in the last 5 minutes"""
        # This is a simplified implementation
        # In production, you'd read from the actual log files
        return 0.0
    
    # Enhanced logging methods with metadata support
    def debug(self, message, **kwargs):
        """Debug level logging"""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message, **kwargs):
        """Info level logging"""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message, **kwargs):
        """Warning level logging"""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message, **kwargs):
        """Error level logging with automatic traceback capture"""
        if 'error_traceback' not in kwargs:
            kwargs['error_traceback'] = traceback.format_exc()
        self.logger.error(message, extra=kwargs)
    
    def critical(self, message, **kwargs):
        """Critical level logging"""
        if 'error_traceback' not in kwargs:
            kwargs['error_traceback'] = traceback.format_exc()
        self.logger.critical(message, extra=kwargs)
    
    # Context managers for operation tracking
    @contextmanager
    def operation(self, operation_name: str, component: str = None, **metadata):
        """Context manager for tracking operation performance"""
        start_time = time.time()
        operation_id = f"{operation_name}_{int(start_time * 1000)}"
        
        # Start operation
        self.info(
            f"🔄 Starting {operation_name}",
            extra={
                'component': component or 'general',
                'operation': operation_name,
                'correlation_id': operation_id,
                'metadata': metadata
            }
        )
        
        try:
            yield operation_id
            
            # Success
            duration_ms = (time.time() - start_time) * 1000
            self.info(
                f"✅ Completed {operation_name} in {duration_ms:.1f}ms",
                extra={
                    'component': component or 'general',
                    'operation': operation_name,
                    'duration_ms': duration_ms,
                    'correlation_id': operation_id,
                    'metadata': metadata
                }
            )
            
            # Check for slow operations
            if duration_ms > self.alert_thresholds['response_time_ms']:
                self.warning(
                    f"Slow operation: {operation_name} took {duration_ms:.1f}ms",
                    extra={
                        'component': component or 'performance',
                        'operation': operation_name,
                        'duration_ms': duration_ms,
                        'correlation_id': operation_id
                    }
                )
            
        except Exception as e:
            # Error
            duration_ms = (time.time() - start_time) * 1000
            self.error(
                f"❌ Failed {operation_name} after {duration_ms:.1f}ms: {str(e)}",
                extra={
                    'component': component or 'general',
                    'operation': operation_name,
                    'duration_ms': duration_ms,
                    'error_type': type(e).__name__,
                    'correlation_id': operation_id,
                    'metadata': metadata
                }
            )
            raise
    
    # Decorator for automatic function logging
    def track_function(self, component: str = None):
        """Decorator to automatically log function execution"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                func_name = f"{func.__module__}.{func.__name__}"
                with self.operation(func_name, component):
                    return func(*args, **kwargs)
            return wrapper
        return decorator
    
    def log_workflow_step(self, workflow_id: str, step: str, status: str, **metadata):
        """Log workflow step with correlation"""
        self.info(
            f"🔄 Workflow {workflow_id}: {step} - {status}",
            extra={
                'component': 'workflow',
                'operation': step,
                'workflow_id': workflow_id,
                'metadata': {'status': status, **metadata}
            }
        )
    
    def log_agent_communication(self, from_agent: str, to_agent: str, message_type: str, **metadata):
        """Log inter-agent communication"""
        self.info(
            f"🤖 {from_agent} → {to_agent}: {message_type}",
            extra={
                'component': 'agent_communication',
                'operation': message_type,
                'metadata': {
                    'from_agent': from_agent,
                    'to_agent': to_agent,
                    **metadata
                }
            }
        )
    
    def log_pr_event(self, pr_url: str, event: str, **metadata):
        """Log PR-related events"""
        self.info(
            f"📋 PR Event: {event}",
            extra={
                'component': 'pr_workflow',
                'operation': event,
                'metadata': {'pr_url': pr_url, **metadata}
            }
        )
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str = None):
        """Log performance metrics"""
        self.info(
            f"📊 {metric_name}: {value}" + (f" {unit}" if unit else ""),
            extra={
                'component': 'performance',
                'operation': 'metric',
                'metadata': {
                    'metric_name': metric_name,
                    'value': value,
                    'unit': unit
                }
            }
        )
    
    def shutdown(self):
        """Graceful shutdown"""
        self.monitoring_active = False
        self.info("🛑 Heinrich Logger shutting down", extra={'component': 'logging_system'})
        
        # Close handlers
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)

# Global logger instance
_global_logger = None

def get_logger(name: str = "heinrich") -> HeinrichLogger:
    """Get or create global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = HeinrichLogger(name)
    return _global_logger

# Convenience functions
def log_info(message, **kwargs):
    get_logger().info(message, **kwargs)

def log_error(message, **kwargs):
    get_logger().error(message, **kwargs)

def log_warning(message, **kwargs):
    get_logger().warning(message, **kwargs)

def track_operation(operation_name: str, component: str = None, **metadata):
    """Context manager for tracking operations"""
    return get_logger().operation(operation_name, component, **metadata)

def track_function(component: str = None):
    """Decorator for automatic function logging"""
    return get_logger().track_function(component)

# Example usage
if __name__ == "__main__":
    logger = HeinrichLogger("test")
    
    # Test different log levels
    logger.debug("Debug message", component="test", metadata={"test": True})
    logger.info("Info message", component="test", operation="demo")
    logger.warning("Warning message", component="test")
    
    # Test operation tracking
    with logger.operation("test_operation", "test_component", test_param="value"):
        time.sleep(0.1)
        logger.info("Inside operation")
    
    # Test function tracking
    @logger.track_function("test_component")
    def test_function():
        logger.info("Inside tracked function")
        return "success"
    
    result = test_function()
    logger.info(f"Function result: {result}")
    
    # Test error logging
    try:
        raise ValueError("Test error")
    except Exception:
        logger.error("Error occurred", component="test")
    
    logger.shutdown()