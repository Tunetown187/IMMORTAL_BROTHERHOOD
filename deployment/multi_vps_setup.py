import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List

class MultiVPSSetup:
    def __init__(self):
        self.base_dir = Path("c:/Users/p8tty/Downloads/agency-swarm-0.2.0")
        self.providers = {
            "contabo": {
                "cost": 60,
                "specs": {
                    "cpu": 16,
                    "ram": 64,
                    "storage": 400
                }
            },
            "hetzner": {
                "cost": 70,
                "specs": {
                    "cpu": 16,
                    "ram": 64,
                    "storage": 240
                }
            },
            "time4vps": {
                "cost": 80,
                "specs": {
                    "cpu": 16,
                    "ram": 64,
                    "storage": 256
                }
            }
        }

    async def setup_infrastructure(self):
        """Setup multi-VPS infrastructure"""
        try:
            # Create deployment scripts for each provider
            await self.create_provider_scripts()
            
            # Setup monitoring
            await self.setup_monitoring()
            
            # Setup load balancing
            await self.setup_load_balancing()
            
            # Setup backup system
            await self.setup_backup_system()
            
        except Exception as e:
            logging.error(f"Multi-VPS setup error: {str(e)}")
            raise

    async def create_provider_scripts(self):
        """Create deployment scripts for each provider"""
        scripts_dir = self.base_dir / "deployment" / "providers"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        
        for provider in self.providers:
            script_file = scripts_dir / f"{provider}_setup.sh"
            with open(script_file, "w") as f:
                f.write(self.generate_provider_script(provider))
            script_file.chmod(0o755)

    def generate_provider_script(self, provider: str) -> str:
        """Generate provider-specific setup script"""
        return f'''#!/bin/bash
# {provider.upper()} Setup Script

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3-pip python3-venv git nginx supervisor redis-server

# Setup Python environment
python3 -m venv /root/venv
source /root/venv/bin/activate

# Clone repository
git clone https://github.com/yourusername/agency-swarm.git /root/agency-swarm

# Install requirements
pip install -r /root/agency-swarm/requirements.txt
pip install -r /root/agency-swarm/requirements_crypto.txt

# Setup Redis
systemctl enable redis-server
systemctl start redis-server

# Setup monitoring
apt install -y prometheus node-exporter grafana

# Setup firewall
ufw allow 22
ufw allow 80
ufw allow 443
ufw enable

# Start services
systemctl start prometheus
systemctl start node-exporter
systemctl start grafana-server

# Setup SSL
apt install -y certbot python3-certbot-nginx
'''

    async def setup_monitoring(self):
        """Setup monitoring configuration"""
        monitoring_dir = self.base_dir / "deployment" / "monitoring"
        monitoring_dir.mkdir(parents=True, exist_ok=True)
        
        configs = {
            "prometheus.yml": '''
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
''',
            "grafana.ini": '''
[server]
protocol = http
http_port = 3000
domain = localhost
''',
            "alertmanager.yml": '''
global:
  resolve_timeout: 5m
route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'email-notifications'
receivers:
- name: 'email-notifications'
  email_configs:
  - to: 'your-email@example.com'
'''
        }
        
        for filename, content in configs.items():
            with open(monitoring_dir / filename, "w") as f:
                f.write(content)

    async def setup_load_balancing(self):
        """Setup load balancing configuration"""
        lb_dir = self.base_dir / "deployment" / "load_balancing"
        lb_dir.mkdir(parents=True, exist_ok=True)
        
        nginx_config = '''
upstream backend {
    least_conn;
    server backend1.example.com:8000;
    server backend2.example.com:8000;
    server backend3.example.com:8000;
}

server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
'''
        
        with open(lb_dir / "nginx.conf", "w") as f:
            f.write(nginx_config)

    async def setup_backup_system(self):
        """Setup backup system configuration"""
        backup_dir = self.base_dir / "deployment" / "backup"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        backup_script = '''#!/bin/bash
# Backup script for agency-swarm

# Backup directories
BACKUP_DIR="/var/backups/agency-swarm"
DATA_DIR="/root/agency-swarm"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz $DATA_DIR

# Rotate old backups (keep last 7 days)
find $BACKUP_DIR -type f -mtime +7 -delete
'''
        
        with open(backup_dir / "backup.sh", "w") as f:
            f.write(backup_script)
        (backup_dir / "backup.sh").chmod(0o755)

if __name__ == "__main__":
    setup = MultiVPSSetup()
    asyncio.run(setup.setup_infrastructure())
