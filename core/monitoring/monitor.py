#!/usr/bin/env python3
"""
RooCode Monitoring Service
Real-time monitoring, metrics collection, and alerting system
Version: 1.0
Created: 2025-06-29
"""

import json
import time
import yaml
import psutil
import docker
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('roocode.monitor')

@dataclass
class MetricValue:
    """Represents a metric value with timestamp."""
    value: float
    timestamp: datetime
    unit: str = ""
    tags: Dict[str, str] = None

@dataclass
class Alert:
    """Represents an alert condition."""
    name: str
    condition: str
    severity: str
    message: str
    triggered_at: datetime
    resolved_at: Optional[datetime] = None

class MetricsCollector:
    """Collects system and application metrics."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.docker_client = None
        self.metrics_history = {}
        
        # Initialize Docker client if available
        try:
            self.docker_client = docker.from_env()
        except Exception as e:
            logger.warning(f"Docker client not available: {e}")
    
    def collect_system_metrics(self) -> Dict[str, MetricValue]:
        """Collect system-level metrics."""
        metrics = {}
        
        if self.config.get('system_metrics', {}).get('enabled', True):
            # CPU metrics
            if self.config['system_metrics'].get('collect_cpu', True):
                cpu_percent = psutil.cpu_percent(interval=1)
                metrics['system.cpu_usage'] = MetricValue(
                    value=cpu_percent,
                    timestamp=datetime.now(),
                    unit="%"
                )
            
            # Memory metrics
            if self.config['system_metrics'].get('collect_memory', True):
                memory = psutil.virtual_memory()
                metrics['system.memory_usage'] = MetricValue(
                    value=memory.percent,
                    timestamp=datetime.now(),
                    unit="%"
                )
                metrics['system.memory_available'] = MetricValue(
                    value=memory.available / (1024**3),  # GB
                    timestamp=datetime.now(),
                    unit="GB"
                )
            
            # Disk metrics
            if self.config['system_metrics'].get('collect_disk', True):
                disk = psutil.disk_usage('/')
                metrics['system.disk_usage'] = MetricValue(
                    value=(disk.used / disk.total) * 100,
                    timestamp=datetime.now(),
                    unit="%"
                )
                metrics['system.disk_free'] = MetricValue(
                    value=disk.free / (1024**3),  # GB
                    timestamp=datetime.now(),
                    unit="GB"
                )
        
        return metrics
    
    def collect_docker_metrics(self) -> Dict[str, MetricValue]:
        """Collect Docker container metrics."""
        metrics = {}
        
        if not self.docker_client or not self.config.get('docker_metrics', {}).get('enabled', True):
            return metrics
        
        try:
            containers = self.docker_client.containers.list()
            
            # Container count
            metrics['docker.container_count'] = MetricValue(
                value=len(containers),
                timestamp=datetime.now(),
                unit="count"
            )
            
            # Container-specific metrics
            for container in containers:
                try:
                    stats = container.stats(stream=False)
                    container_name = container.name
                    
                    # CPU usage
                    cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                               stats['precpu_stats']['cpu_usage']['total_usage']
                    system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                                  stats['precpu_stats']['system_cpu_usage']
                    
                    if system_delta > 0:
                        cpu_percent = (cpu_delta / system_delta) * 100.0
                        metrics[f'docker.{container_name}.cpu_usage'] = MetricValue(
                            value=cpu_percent,
                            timestamp=datetime.now(),
                            unit="%"
                        )
                    
                    # Memory usage
                    memory_usage = stats['memory_stats']['usage']
                    memory_limit = stats['memory_stats']['limit']
                    memory_percent = (memory_usage / memory_limit) * 100
                    
                    metrics[f'docker.{container_name}.memory_usage'] = MetricValue(
                        value=memory_percent,
                        timestamp=datetime.now(),
                        unit="%"
                    )
                    
                except Exception as e:
                    logger.warning(f"Failed to collect stats for container {container.name}: {e}")
        
        except Exception as e:
            logger.error(f"Failed to collect Docker metrics: {e}")
        
        return metrics
    
    def collect_application_metrics(self) -> Dict[str, MetricValue]:
        """Collect application-specific metrics."""
        metrics = {}
        
        if not self.config.get('application_metrics', {}).get('enabled', True):
            return metrics
        
        # Check for log files and extract metrics
        project_root = Path(__file__).parent.parent.parent
        
        # Check workflow execution logs
        history_dir = project_root / "core" / "history"
        if history_dir.exists():
            log_files = list(history_dir.glob("*.runlog.yaml"))
            
            # Count recent workflows
            recent_workflows = 0
            for log_file in log_files:
                try:
                    # Check if file is from last 24 hours
                    if (datetime.now() - datetime.fromtimestamp(log_file.stat().st_mtime)) < timedelta(hours=24):
                        recent_workflows += 1
                except Exception:
                    continue
            
            metrics['application.workflows_24h'] = MetricValue(
                value=recent_workflows,
                timestamp=datetime.now(),
                unit="count"
            )
        
        # Check vocabulary file
        vocab_file = project_root / "core" / "vocab" / "vocab.yaml"
        if vocab_file.exists():
            try:
                with open(vocab_file, 'r', encoding='utf-8') as f:
                    vocab_data = yaml.safe_load(f)
                    intent_count = len(vocab_data.get('intents', []))
                    
                    metrics['application.vocabulary_size'] = MetricValue(
                        value=intent_count,
                        timestamp=datetime.now(),
                        unit="count"
                    )
            except Exception as e:
                logger.warning(f"Failed to read vocabulary file: {e}")
        
        return metrics
    
    def collect_all_metrics(self) -> Dict[str, MetricValue]:
        """Collect all configured metrics."""
        all_metrics = {}
        
        # Collect system metrics
        all_metrics.update(self.collect_system_metrics())
        
        # Collect Docker metrics
        all_metrics.update(self.collect_docker_metrics())
        
        # Collect application metrics
        all_metrics.update(self.collect_application_metrics())
        
        # Store in history
        for metric_name, metric_value in all_metrics.items():
            if metric_name not in self.metrics_history:
                self.metrics_history[metric_name] = []
            
            self.metrics_history[metric_name].append(metric_value)
            
            # Keep only recent history (last 1000 points)
            if len(self.metrics_history[metric_name]) > 1000:
                self.metrics_history[metric_name] = self.metrics_history[metric_name][-1000:]
        
        return all_metrics

class AlertManager:
    """Manages alerts and notifications."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.active_alerts = {}
        self.alert_history = []
    
    def evaluate_alerts(self, metrics: Dict[str, MetricValue]) -> List[Alert]:
        """Evaluate alert conditions against current metrics."""
        triggered_alerts = []
        
        if not self.config.get('alerting', {}).get('enabled', True):
            return triggered_alerts
        
        alert_rules = self.config.get('alerting', {}).get('alert_rules', [])
        
        for rule in alert_rules:
            alert_name = rule['name']
            condition = rule['condition']
            severity = rule['severity']
            message = rule['message']
            
            try:
                # Simple condition evaluation (extend for more complex conditions)
                if self._evaluate_condition(condition, metrics):
                    if alert_name not in self.active_alerts:
                        alert = Alert(
                            name=alert_name,
                            condition=condition,
                            severity=severity,
                            message=message,
                            triggered_at=datetime.now()
                        )
                        
                        self.active_alerts[alert_name] = alert
                        triggered_alerts.append(alert)
                        self.alert_history.append(alert)
                        
                        logger.warning(f"Alert triggered: {alert_name} - {message}")
                else:
                    # Resolve alert if it was active
                    if alert_name in self.active_alerts:
                        self.active_alerts[alert_name].resolved_at = datetime.now()
                        del self.active_alerts[alert_name]
                        logger.info(f"Alert resolved: {alert_name}")
            
            except Exception as e:
                logger.error(f"Failed to evaluate alert rule {alert_name}: {e}")
        
        return triggered_alerts
    
    def _evaluate_condition(self, condition: str, metrics: Dict[str, MetricValue]) -> bool:
        """Evaluate a simple alert condition."""
        # Simple condition parser (extend for more complex conditions)
        # Example: "system.cpu_usage > 90"
        
        try:
            parts = condition.split()
            if len(parts) != 3:
                return False
            
            metric_name, operator, threshold = parts
            threshold = float(threshold)
            
            if metric_name in metrics:
                metric_value = metrics[metric_name].value
                
                if operator == '>':
                    return metric_value > threshold
                elif operator == '<':
                    return metric_value < threshold
                elif operator == '>=':
                    return metric_value >= threshold
                elif operator == '<=':
                    return metric_value <= threshold
                elif operator == '==':
                    return metric_value == threshold
                elif operator == '!=':
                    return metric_value != threshold
        
        except Exception:
            pass
        
        return False

class MonitoringService:
    """Main monitoring service."""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.metrics_collector = MetricsCollector(self.config['monitoring'])
        self.alert_manager = AlertManager(self.config)
        self.running = False
        self.metrics_data = {}
        
        # Create monitoring data directory
        self.data_dir = Path(self.config['monitoring']['storage_path'])
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load monitoring configuration."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config from {self.config_path}: {e}")
            return {'monitoring': {'enabled': False}}
    
    def start(self):
        """Start the monitoring service."""
        if not self.config['monitoring'].get('enabled', True):
            logger.info("Monitoring is disabled in configuration")
            return
        
        logger.info("Starting RooCode monitoring service")
        self.running = True
        
        # Start metrics collection thread
        metrics_thread = threading.Thread(target=self._metrics_collection_loop)
        metrics_thread.daemon = True
        metrics_thread.start()
        
        # Start web server for dashboard
        if self.config['monitoring'].get('dashboard', {}).get('enabled', True):
            dashboard_thread = threading.Thread(target=self._start_dashboard_server)
            dashboard_thread.daemon = True
            dashboard_thread.start()
        
        logger.info("Monitoring service started successfully")
    
    def stop(self):
        """Stop the monitoring service."""
        logger.info("Stopping monitoring service")
        self.running = False
    
    def _metrics_collection_loop(self):
        """Main metrics collection loop."""
        interval = self.config['monitoring'].get('collection_interval_seconds', 30)
        
        while self.running:
            try:
                # Collect metrics
                metrics = self.metrics_collector.collect_all_metrics()
                self.metrics_data = metrics
                
                # Evaluate alerts
                self.alert_manager.evaluate_alerts(metrics)
                
                # Save metrics to file
                self._save_metrics(metrics)
                
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
            
            time.sleep(interval)
    
    def _save_metrics(self, metrics: Dict[str, MetricValue]):
        """Save metrics to file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            metrics_file = self.data_dir / f"metrics_{timestamp}.json"
            
            # Convert metrics to serializable format
            serializable_metrics = {}
            for name, metric in metrics.items():
                serializable_metrics[name] = {
                    'value': metric.value,
                    'timestamp': metric.timestamp.isoformat(),
                    'unit': metric.unit,
                    'tags': metric.tags or {}
                }
            
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_metrics, f, indent=2)
        
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def _start_dashboard_server(self):
        """Start the dashboard web server."""
        try:
            port = self.config['monitoring'].get('dashboard', {}).get('port', 8081)
            
            class DashboardHandler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)
                
                def do_GET(self):
                    if self.path == '/api/metrics':
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        
                        # Return current metrics as JSON
                        metrics_json = {}
                        for name, metric in self.server.monitoring_service.metrics_data.items():
                            metrics_json[name] = {
                                'value': metric.value,
                                'timestamp': metric.timestamp.isoformat(),
                                'unit': metric.unit
                            }
                        
                        self.wfile.write(json.dumps(metrics_json).encode())
                    else:
                        super().do_GET()
            
            with socketserver.TCPServer(("", port), DashboardHandler) as httpd:
                httpd.monitoring_service = self
                logger.info(f"Dashboard server started on port {port}")
                httpd.serve_forever()
        
        except Exception as e:
            logger.error(f"Failed to start dashboard server: {e}")

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='RooCode Monitoring Service')
    parser.add_argument('--config', default='core/config/monitoring.yaml',
                       help='Path to monitoring configuration file')
    parser.add_argument('--daemon', action='store_true',
                       help='Run as daemon')
    
    args = parser.parse_args()
    
    # Initialize monitoring service
    service = MonitoringService(args.config)
    
    try:
        service.start()
        
        if args.daemon:
            # Run as daemon
            while True:
                time.sleep(60)
        else:
            # Interactive mode
            print("Monitoring service running. Press Ctrl+C to stop.")
            while True:
                time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        service.stop()

if __name__ == '__main__':
    main()
