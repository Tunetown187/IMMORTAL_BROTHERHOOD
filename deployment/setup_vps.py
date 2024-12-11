import subprocess
import sys
import os
from pathlib import Path

class VPSDeployment:
    def __init__(self):
        self.base_dir = Path("/root/agency-swarm")
        self.log_dir = self.base_dir / "logs"
        self.data_dir = self.base_dir / "data"
        
    def setup_directories(self):
        """Create necessary directories"""
        dirs = [self.base_dir, self.log_dir, self.data_dir]
        for dir in dirs:
            dir.mkdir(parents=True, exist_ok=True)
            
    def install_system_dependencies(self):
        """Install required system packages"""
        packages = [
            "python3-pip",
            "python3-dev",
            "git",
            "nginx",
            "supervisor",
            "build-essential",
            "ntp",
            "htop",
            "screen"
        ]
        subprocess.run(["apt-get", "update"])
        subprocess.run(["apt-get", "install", "-y"] + packages)
        
    def setup_python_environment(self):
        """Set up Python virtual environment and install requirements"""
        subprocess.run(["python3", "-m", "venv", str(self.base_dir / "venv")])
        subprocess.run([
            str(self.base_dir / "venv/bin/pip"),
            "install",
            "-r",
            "requirements.txt"
        ])
        subprocess.run([
            str(self.base_dir / "venv/bin/pip"),
            "install",
            "-r",
            "requirements_crypto.txt"
        ])
        
    def setup_supervisor(self):
        """Configure supervisor for 24/7 operation"""
        config = f"""[program:agency-swarm]
command={self.base_dir}/venv/bin/python startup.py
directory={self.base_dir}
autostart=true
autorestart=true
stderr_logfile={self.log_dir}/supervisor.err.log
stdout_logfile={self.log_dir}/supervisor.out.log
environment=PYTHONUNBUFFERED=1
startsecs=10
stopwaitsecs=600
killasgroup=true
"""
        with open("/etc/supervisor/conf.d/agency-swarm.conf", "w") as f:
            f.write(config)
            
    def setup_monitoring(self):
        """Set up system monitoring"""
        subprocess.run([
            str(self.base_dir / "venv/bin/pip"),
            "install",
            "prometheus_client",
            "grafana-client"
        ])
        
    def deploy(self):
        """Run full deployment sequence"""
        try:
            print("Starting VPS deployment...")
            self.setup_directories()
            print("Installing system dependencies...")
            self.install_system_dependencies()
            print("Setting up Python environment...")
            self.setup_python_environment()
            print("Configuring supervisor...")
            self.setup_supervisor()
            print("Setting up monitoring...")
            self.setup_monitoring()
            
            # Start services
            subprocess.run(["supervisorctl", "reread"])
            subprocess.run(["supervisorctl", "update"])
            subprocess.run(["supervisorctl", "start", "agency-swarm"])
            
            print("Deployment complete! System is running 24/7")
            
        except Exception as e:
            print(f"Deployment failed: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    deployment = VPSDeployment()
    deployment.deploy()
