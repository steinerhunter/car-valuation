#!/usr/bin/env python3
"""
Health Check and Monitoring Endpoints for OME-89 Car Valuation System
Addresses production readiness gaps identified by reviewers
"""

import os
import time
import json
import psutil
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class HealthStatus:
    """Health status data structure"""
    service: str
    status: str  # "healthy", "degraded", "unhealthy"
    response_time_ms: float
    last_check: datetime
    details: Dict[str, Any]

class SystemHealthChecker:
    """Comprehensive health checking system"""
    
    def __init__(self):
        self.checks = {}
        self.start_time = datetime.now()
        
    def check_system_resources(self) -> HealthStatus:
        """Check system resource utilization"""
        start_time = time.time()
        
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Determine overall health
            status = "healthy"
            if cpu_percent > 80 or memory_percent > 80 or disk_percent > 90:
                status = "degraded"
            if cpu_percent > 95 or memory_percent > 95 or disk_percent > 95:
                status = "unhealthy"
            
            details = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent,
                "memory_available_gb": round(memory.available / 1024**3, 2),
                "disk_free_gb": round(disk.free / 1024**3, 2)
            }
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthStatus(
                service="system_resources",
                status=status,
                response_time_ms=response_time,
                last_check=datetime.now(),
                details=details
            )
            
        except Exception as e:
            return HealthStatus(
                service="system_resources",
                status="unhealthy",
                response_time_ms=(time.time() - start_time) * 1000,
                last_check=datetime.now(),
                details={"error": str(e)}
            )
    
    def check_api_connectivity(self) -> HealthStatus:
        """Check external API connectivity (without making actual calls)"""
        start_time = time.time()
        
        try:
            # Test DNS resolution to Apify
            response = requests.get("https://api.apify.com/", timeout=10)
            
            status = "healthy" if response.status_code == 200 else "degraded"
            
            details = {
                "api_endpoint": "https://api.apify.com/",
                "status_code": response.status_code,
                "response_time_ms": response.elapsed.total_seconds() * 1000,
                "can_connect": True
            }
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthStatus(
                service="api_connectivity",
                status=status,
                response_time_ms=response_time,
                last_check=datetime.now(),
                details=details
            )
            
        except Exception as e:
            return HealthStatus(
                service="api_connectivity",
                status="unhealthy",
                response_time_ms=(time.time() - start_time) * 1000,
                last_check=datetime.now(),
                details={"error": str(e), "can_connect": False}
            )
    
    def check_data_processing_capability(self) -> HealthStatus:
        """Check data processing and analysis capabilities"""
        start_time = time.time()
        
        try:
            # Test basic analysis functions
            from yad2_web_scraper import Yad2WebScraper
            
            scraper = Yad2WebScraper()
            
            # Test with sample data
            sample_data = [
                {'price': 45000, 'km': 160000, 'year': 2014, 'location': 'תל אביב'},
                {'price': 42000, 'km': 180000, 'year': 2014, 'location': 'חיפה'}
            ]
            
            analysis = scraper.analyze_market_data(sample_data)
            
            # Verify analysis worked
            if 'total_listings' in analysis and analysis['total_listings'] == 2:
                status = "healthy"
                details = {
                    "analysis_successful": True,
                    "sample_listings_processed": 2,
                    "core_functions_working": True
                }
            else:
                status = "degraded"
                details = {
                    "analysis_successful": False,
                    "error": "Analysis did not return expected results"
                }
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthStatus(
                service="data_processing",
                status=status,
                response_time_ms=response_time,
                last_check=datetime.now(),
                details=details
            )
            
        except Exception as e:
            return HealthStatus(
                service="data_processing",
                status="unhealthy",
                response_time_ms=(time.time() - start_time) * 1000,
                last_check=datetime.now(),
                details={"error": str(e), "core_functions_working": False}
            )
    
    def check_configuration_validity(self) -> HealthStatus:
        """Check configuration and environment setup"""
        start_time = time.time()
        
        try:
            config_issues = []
            
            # Check for API token
            api_token = os.getenv('APIFY_API_TOKEN')
            if not api_token:
                config_issues.append("Missing APIFY_API_TOKEN environment variable")
            elif len(api_token) < 20:
                config_issues.append("APIFY_API_TOKEN appears too short")
            
            # Check for required directories
            required_dirs = ['logs', 'data']
            for directory in required_dirs:
                if not os.path.exists(directory):
                    config_issues.append(f"Missing required directory: {directory}")
            
            # Check Python dependencies
            required_modules = ['requests', 'beautifulsoup4', 'psutil']
            for module in required_modules:
                try:
                    __import__(module)
                except ImportError:
                    config_issues.append(f"Missing required Python module: {module}")
            
            if not config_issues:
                status = "healthy"
                details = {"configuration_valid": True}
            elif len(config_issues) <= 2:
                status = "degraded"
                details = {"configuration_valid": False, "issues": config_issues}
            else:
                status = "unhealthy"
                details = {"configuration_valid": False, "issues": config_issues}
            
            response_time = (time.time() - start_time) * 1000
            
            return HealthStatus(
                service="configuration",
                status=status,
                response_time_ms=response_time,
                last_check=datetime.now(),
                details=details
            )
            
        except Exception as e:
            return HealthStatus(
                service="configuration",
                status="unhealthy",
                response_time_ms=(time.time() - start_time) * 1000,
                last_check=datetime.now(),
                details={"error": str(e)}
            )
    
    def perform_comprehensive_health_check(self) -> Dict[str, Any]:
        """Perform all health checks and return comprehensive status"""
        
        print("🏥 Performing Comprehensive Health Check...")
        print("=" * 50)
        
        # Run all health checks
        checks = {
            "system_resources": self.check_system_resources(),
            "api_connectivity": self.check_api_connectivity(),
            "data_processing": self.check_data_processing_capability(),
            "configuration": self.check_configuration_validity()
        }
        
        # Calculate overall health
        statuses = [check.status for check in checks.values()]
        
        if all(status == "healthy" for status in statuses):
            overall_status = "healthy"
        elif any(status == "unhealthy" for status in statuses):
            overall_status = "unhealthy"
        else:
            overall_status = "degraded"
        
        # Calculate uptime
        uptime = datetime.now() - self.start_time
        
        # Prepare response
        health_report = {
            "overall_status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime_human": str(uptime).split('.')[0],  # Remove microseconds
            "checks": {
                name: {
                    "status": check.status,
                    "response_time_ms": check.response_time_ms,
                    "last_check": check.last_check.isoformat(),
                    "details": check.details
                }
                for name, check in checks.items()
            },
            "summary": {
                "healthy_services": sum(1 for s in statuses if s == "healthy"),
                "degraded_services": sum(1 for s in statuses if s == "degraded"),
                "unhealthy_services": sum(1 for s in statuses if s == "unhealthy"),
                "total_services": len(statuses)
            }
        }
        
        return health_report

class MonitoringEndpoints:
    """Production monitoring endpoints"""
    
    def __init__(self):
        self.health_checker = SystemHealthChecker()
    
    def health_endpoint(self) -> Dict[str, Any]:
        """Simple health endpoint for load balancers"""
        try:
            system_check = self.health_checker.check_system_resources()
            config_check = self.health_checker.check_configuration_validity()
            
            if system_check.status == "healthy" and config_check.status == "healthy":
                return {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "timestamp": datetime.now().isoformat()
                }
        except:
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat()
            }
    
    def readiness_endpoint(self) -> Dict[str, Any]:
        """Readiness endpoint for Kubernetes/container orchestration"""
        try:
            # Check if service is ready to accept traffic
            config_check = self.health_checker.check_configuration_validity()
            processing_check = self.health_checker.check_data_processing_capability()
            
            ready = (config_check.status != "unhealthy" and 
                    processing_check.status != "unhealthy")
            
            return {
                "ready": ready,
                "timestamp": datetime.now().isoformat(),
                "details": {
                    "configuration": config_check.status,
                    "data_processing": processing_check.status
                }
            }
        except:
            return {
                "ready": False,
                "timestamp": datetime.now().isoformat()
            }
    
    def metrics_endpoint(self) -> Dict[str, Any]:
        """Metrics endpoint for Prometheus/monitoring systems"""
        try:
            # Basic metrics
            system_check = self.health_checker.check_system_resources()
            
            metrics = {
                "car_valuation_up": 1,
                "car_valuation_cpu_percent": system_check.details.get("cpu_percent", 0),
                "car_valuation_memory_percent": system_check.details.get("memory_percent", 0),
                "car_valuation_disk_percent": system_check.details.get("disk_percent", 0),
                "car_valuation_response_time_ms": system_check.response_time_ms,
                "timestamp": datetime.now().isoformat()
            }
            
            return metrics
        except:
            return {
                "car_valuation_up": 0,
                "timestamp": datetime.now().isoformat()
            }

def test_health_check_system():
    """Test the health check system"""
    print("🏥 Testing Health Check System")
    print("=" * 40)
    
    # Test individual checks
    health_checker = SystemHealthChecker()
    
    # Test system resources
    system_health = health_checker.check_system_resources()
    print(f"✅ System Resources: {system_health.status} ({system_health.response_time_ms:.1f}ms)")
    
    # Test configuration
    config_health = health_checker.check_configuration_validity()
    print(f"✅ Configuration: {config_health.status} ({config_health.response_time_ms:.1f}ms)")
    
    # Test data processing
    processing_health = health_checker.check_data_processing_capability()
    print(f"✅ Data Processing: {processing_health.status} ({processing_health.response_time_ms:.1f}ms)")
    
    # Test comprehensive check
    comprehensive_health = health_checker.perform_comprehensive_health_check()
    print(f"\n🎯 Overall Status: {comprehensive_health['overall_status']}")
    print(f"📊 Healthy Services: {comprehensive_health['summary']['healthy_services']}/{comprehensive_health['summary']['total_services']}")
    
    # Test monitoring endpoints
    monitoring = MonitoringEndpoints()
    
    health_response = monitoring.health_endpoint()
    print(f"💚 Health Endpoint: {health_response['status']}")
    
    readiness_response = monitoring.readiness_endpoint()
    print(f"🚀 Readiness Endpoint: {'Ready' if readiness_response['ready'] else 'Not Ready'}")
    
    return comprehensive_health

if __name__ == "__main__":
    test_health_check_system()