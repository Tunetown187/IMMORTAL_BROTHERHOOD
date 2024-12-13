import os
import shutil
from pathlib import Path
import subprocess
import logging

class AWSDeployment:
    def __init__(self):
        self.base_dir = Path("c:/Users/p8tty/Downloads/agency-swarm-0.2.0")
        self.setup_logging()

    def organize_project(self):
        """Organize all project files into correct directories"""
        # Core directories
        directories = {
            'agents': ['base_agent.py', 'crypto_agent.py', 'state_manager.py', 'supreme_identity.py'],
            'crypto': ['quantum_crypto_domination.py', 'blockchain_manager.py', 'master_controller.py'],
            'autonomous_growth': ['smart_scaling_system.py', 'budget_optimizer.py'],
            'deployment': ['aws_deployment.py', 'setup_vps.py', 'ENTERPRISE_VPS_SPECS.md', 'CRYPTO_AGENTS_VPS_SPECS.md'],
            'config': ['settings.json', '.env', 'config.json'],
            'scripts': ['optimize_system.ps1', 'gpu_optimizer.ps1', 'system_cleanup.ps1'],
            'contracts': ['token_contract.sol'],
            'tests': ['test_gpu.py', 'test_gpu_agency.py', 'run_tests.py']
        }

        for dir_name, files in directories.items():
            dir_path = self.base_dir / dir_name
            dir_path.mkdir(exist_ok=True)
            for file in files:
                source = self.base_dir / file
                if source.exists():
                    shutil.move(str(source), str(dir_path / file))

    def setup_aws_structure(self):
        """Setup structure for AWS deployment"""
        aws_dirs = [
            'logs',
            'data',
            'state',
            'backups',
            'monitoring',
            'agents/configs',
            'crypto/strategies',
            'autonomous_growth/data'
        ]

        for dir_path in aws_dirs:
            (self.base_dir / dir_path).mkdir(parents=True, exist_ok=True)

    def create_aws_configs(self):
        """Create AWS-specific configuration files"""
        configs = {
            'aws_config.json': {
                'region': 'us-east-1',
                'instance_type': 't3.xlarge',
                'volume_size': 100,
                'security_groups': ['agency-swarm-sg'],
                'key_name': 'agency-swarm-key'
            },
            'supervisor_config.conf': '''
[program:agency-swarm]
command=/root/venv/bin/python /root/agency-swarm/startup.py
directory=/root/agency-swarm
user=root
autostart=true
autorestart=true
stderr_logfile=/var/log/agency-swarm.err.log
stdout_logfile=/var/log/agency-swarm.out.log
            ''',
            'nginx_config.conf': '''
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
            '''
        }

        config_dir = self.base_dir / 'deployment' / 'aws_configs'
        config_dir.mkdir(exist_ok=True)

        for filename, content in configs.items():
            with open(config_dir / filename, 'w') as f:
                if isinstance(content, dict):
                    json.dump(content, f, indent=4)
                else:
                    f.write(content)

    def create_deployment_script(self):
        """Create AWS deployment script"""
        deploy_script = '''#!/bin/bash
# AWS Deployment Script

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-dev git nginx supervisor build-essential ntp htop screen

# Setup Python virtual environment
python3 -m venv /root/venv
source /root/venv/bin/activate

# Clone repository
git clone https://github.com/Tunetown187/IMMORTAL_BROTHERHOOD.git /root/agency-swarm

# Install requirements
pip install -r /root/agency-swarm/requirements.txt
pip install -r /root/agency-swarm/requirements_crypto.txt

# Setup supervisor
cp /root/agency-swarm/deployment/aws_configs/supervisor_config.conf /etc/supervisor/conf.d/agency-swarm.conf
supervisorctl reread
supervisorctl update

# Setup nginx
cp /root/agency-swarm/deployment/aws_configs/nginx_config.conf /etc/nginx/sites-available/agency-swarm
ln -s /etc/nginx/sites-available/agency-swarm /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx

# Start the system
supervisorctl start agency-swarm
'''
        
        deploy_path = self.base_dir / 'deployment' / 'aws_deploy.sh'
        with open(deploy_path, 'w') as f:
            f.write(deploy_script)
        
        # Make script executable
        os.chmod(deploy_path, 0o755)

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            filename=str(self.base_dir / 'deployment' / 'aws_setup.log'),
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def prepare_for_aws(self):
        """Prepare entire project for AWS deployment"""
        try:
            self.organize_project()
            self.setup_aws_structure()
            self.create_aws_configs()
            self.create_deployment_script()
            logging.info("Successfully prepared project for AWS deployment")
        except Exception as e:
            logging.error(f"Error preparing for AWS: {str(e)}")
            raise

if __name__ == "__main__":
    deployment = AWSDeployment()
    deployment.prepare_for_aws()
