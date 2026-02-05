"""
Alerts - Monitors system performance and sends alerts for issues.
"""
import time
from typing import Dict, List, Callable, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import logging


@dataclass
class Alert:
    """Alert data structure"""
    timestamp: datetime
    severity: str  # "info", "warning", "critical"
    message: str
    metric_name: str
    current_value: float
    threshold: float
    resolved: bool = False


class AlertSystem:
    """Monitors system performance and sends alerts for issues"""
    
    def __init__(self, performance_tracker=None):
        self.performance_tracker = performance_tracker
        self.alerts: List[Alert] = []
        self.max_alerts = 1000
        self.alert_handlers: List[Callable[[Alert], None]] = []
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)
        
        # Default alert rules
        self._setup_default_alert_rules()
    
    def _setup_default_alert_rules(self):
        """Setup default alert rules"""
        self.alert_rules = {
            "high_cpu_usage": {
                "metric": "cpu_percent",
                "threshold": 85.0,
                "severity": "warning",
                "comparison": "greater_than"
            },
            "critical_cpu_usage": {
                "metric": "cpu_percent",
                "threshold": 95.0,
                "severity": "critical",
                "comparison": "greater_than"
            },
            "high_memory_usage": {
                "metric": "memory_percent",
                "threshold": 80.0,
                "severity": "warning",
                "comparison": "greater_than"
            },
            "critical_memory_usage": {
                "metric": "memory_percent",
                "threshold": 90.0,
                "severity": "critical",
                "comparison": "greater_than"
            },
            "low_memory_available": {
                "metric": "memory_available_gb",
                "threshold": 2.0,
                "severity": "warning",
                "comparison": "less_than"
            },
            "critical_low_memory": {
                "metric": "memory_available_gb",
                "threshold": 1.0,
                "severity": "critical",
                "comparison": "less_than"
            },
            "slow_response_time": {
                "metric": "response_time_ms",
                "threshold": 5000.0,
                "severity": "warning",
                "comparison": "greater_than"
            },
            "critical_response_time": {
                "metric": "response_time_ms",
                "threshold": 10000.0,
                "severity": "critical",
                "comparison": "greater_than"
            },
            "low_cache_hit_rate": {
                "metric": "cache_hit_rate",
                "threshold": 0.5,
                "severity": "warning",
                "comparison": "less_than"
            }
        }
    
    def add_alert_handler(self, handler: Callable[[Alert], None]):
        """Add a handler function for alerts"""
        self.alert_handlers.append(handler)
    
    def remove_alert_handler(self, handler: Callable[[Alert], None]):
        """Remove an alert handler"""
        if handler in self.alert_handlers:
            self.alert_handlers.remove(handler)
    
    def add_alert_rule(self, name: str, metric: str, threshold: float, 
                      severity: str, comparison: str = "greater_than"):
        """Add a custom alert rule"""
        self.alert_rules[name] = {
            "metric": metric,
            "threshold": threshold,
            "severity": severity,
            "comparison": comparison
        }
    
    def remove_alert_rule(self, name: str):
        """Remove an alert rule"""
        if name in self.alert_rules:
            del self.alert_rules[name]
    
    def check_alerts(self) -> List[Alert]:
        """Check current metrics against alert rules and generate alerts"""
        if not self.performance_tracker:
            return []
        
        current_metrics = self.performance_tracker.get_current_metrics()
        if not current_metrics:
            return []
        
        new_alerts = []
        
        for rule_name, rule in self.alert_rules.items():
            metric_name = rule["metric"]
            threshold = rule["threshold"]
            severity = rule["severity"]
            comparison = rule["comparison"]
            
            if metric_name in current_metrics:
                current_value = current_metrics[metric_name]
                
                # Check if alert condition is met
                alert_condition = False
                if comparison == "greater_than":
                    alert_condition = current_value > threshold
                elif comparison == "less_than":
                    alert_condition = current_value < threshold
                elif comparison == "equal_to":
                    alert_condition = current_value == threshold
                
                if alert_condition:
                    # Check if we already have an active alert for this rule
                    existing_alert = self._find_active_alert(rule_name, metric_name)
                    if not existing_alert:
                        # Create new alert
                        alert = Alert(
                            timestamp=datetime.now(),
                            severity=severity,
                            message=f"{metric_name} ({current_value}) {comparison} threshold ({threshold})",
                            metric_name=metric_name,
                            current_value=current_value,
                            threshold=threshold
                        )
                        new_alerts.append(alert)
                        self._store_alert(alert)
                        self._notify_handlers(alert)
        
        return new_alerts
    
    def _find_active_alert(self, rule_name: str, metric_name: str) -> Alert:
        """Find an active alert for a specific rule"""
        for alert in reversed(self.alerts):  # Check most recent first
            if (not alert.resolved and 
                alert.metric_name == metric_name and
                f"{alert.metric_name} (" in alert.message):
                return alert
        return None
    
    def _store_alert(self, alert: Alert):
        """Store an alert in history"""
        self.alerts.append(alert)
        if len(self.alerts) > self.max_alerts:
            self.alerts.pop(0)
        
        self.logger.warning(f"ALERT [{alert.severity.upper()}]: {alert.message}")
    
    def _notify_handlers(self, alert: Alert):
        """Notify all alert handlers"""
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Error in alert handler: {e}")
    
    def resolve_alert(self, alert: Alert):
        """Mark an alert as resolved"""
        alert.resolved = True
        self.logger.info(f"ALERT RESOLVED: {alert.message}")
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unresolved) alerts"""
        return [alert for alert in self.alerts if not alert.resolved]
    
    def get_alerts_by_severity(self, severity: str) -> List[Alert]:
        """Get alerts by severity level"""
        return [alert for alert in self.alerts if alert.severity == severity]
    
    def get_recent_alerts(self, limit: int = 50) -> List[Alert]:
        """Get recent alerts"""
        return self.alerts[-limit:]
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts.clear()
    
    def get_alert_summary(self) -> Dict[str, int]:
        """Get a summary of alert counts by severity"""
        active_alerts = self.get_active_alerts()
        
        summary = {
            "total_active": len(active_alerts),
            "critical": len([a for a in active_alerts if a.severity == "critical"]),
            "warning": len([a for a in active_alerts if a.severity == "warning"]),
            "info": len([a for a in active_alerts if a.severity == "info"])
        }
        
        return summary


# Example alert handlers
def console_alert_handler(alert: Alert):
    """Simple console alert handler"""
    severity_symbol = {
        "info": "ℹ️",
        "warning": "⚠️",
        "critical": "🚨"
    }.get(alert.severity, "•")
    
    print(f"{severity_symbol} ALERT [{alert.severity.upper()}]: {alert.message}")


def log_alert_handler(alert: Alert):
    """Logging alert handler"""
    logger = logging.getLogger("alerts")
    log_method = {
        "info": logger.info,
        "warning": logger.warning,
        "critical": logger.critical
    }.get(alert.severity, logger.info)
    
    log_method(f"ALERT: {alert.message}")


# Example usage
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create alert system
    alert_system = AlertSystem()
    
    # Add handlers
    alert_system.add_alert_handler(console_alert_handler)
    alert_system.add_alert_handler(log_alert_handler)
    
    # Add a custom alert rule
    alert_system.add_alert_rule(
        name="high_disk_usage",
        metric="disk_usage_percent",
        threshold=80.0,
        severity="warning"
    )
    
    print("Alert system initialized with default rules:")
    for name, rule in alert_system.alert_rules.items():
        print(f"  - {name}: {rule['metric']} {rule['comparison']} {rule['threshold']} ({rule['severity']})")