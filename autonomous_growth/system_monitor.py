import asyncio
import aiohttp
import json
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, List
import schedule
import github
from datetime import datetime

class SystemMonitor:
    def __init__(self):
        self.base_dir = Path("c:/Users/p8tty/Downloads/agency-swarm-0.2.0")
        self.setup_logging()
        
        # GitHub configuration
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_repo = "your-repo-name"
        
        # Netlify configuration
        self.netlify_token = os.getenv("NETLIFY_TOKEN")
        self.netlify_site_id = "your-site-id"
        
        # StackBlitz configuration
        self.stackblitz_token = os.getenv("STACKBLITZ_TOKEN")
        
        # VPS monitoring configuration
        self.vps_endpoints = {
            "main": "https://your-vps-endpoint/health",
            "backup": "https://your-backup-vps/health"
        }
        
        # Initialize monitoring state
        self.monitoring_state = {
            "last_github_check": None,
            "last_netlify_check": None,
            "last_stackblitz_check": None,
            "last_vps_check": None,
            "errors": []
        }

    async def start_monitoring(self):
        """Start the monitoring system"""
        try:
            # Schedule regular checks
            schedule.every(5).minutes.do(self.check_github_status)
            schedule.every(3).minutes.do(self.check_netlify_status)
            schedule.every(3).minutes.do(self.check_stackblitz_status)
            schedule.every(1).minutes.do(self.check_vps_status)
            schedule.every(1).hours.do(self.perform_system_maintenance)
            
            while True:
                schedule.run_pending()
                await asyncio.sleep(60)
                
        except Exception as e:
            logging.error(f"Monitoring system error: {str(e)}")
            await self.handle_error(e)

    async def check_github_status(self):
        """Check GitHub repository status"""
        try:
            g = github.Github(self.github_token)
            repo = g.get_repo(self.github_repo)
            
            # Check for failed workflows
            workflows = repo.get_workflows()
            for workflow in workflows:
                runs = workflow.get_runs()
                for run in runs:
                    if run.conclusion == "failure":
                        await self.fix_github_workflow(workflow, run)
            
            self.monitoring_state["last_github_check"] = datetime.now()
            logging.info("GitHub status check completed successfully")
            
        except Exception as e:
            logging.error(f"GitHub status check error: {str(e)}")
            await self.handle_error(e)

    async def check_netlify_status(self):
        """Check Netlify deployment status"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.netlify_token}"}
                async with session.get(f"https://api.netlify.com/api/v1/sites/{self.netlify_site_id}", headers=headers) as response:
                    if response.status == 200:
                        site_data = await response.json()
                        if site_data["state"] != "ready":
                            await self.fix_netlify_deployment()
            
            self.monitoring_state["last_netlify_check"] = datetime.now()
            logging.info("Netlify status check completed successfully")
            
        except Exception as e:
            logging.error(f"Netlify status check error: {str(e)}")
            await self.handle_error(e)

    async def check_stackblitz_status(self):
        """Check StackBlitz project status"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.stackblitz_token}"}
                async with session.get("https://api.stackblitz.com/v1/projects", headers=headers) as response:
                    if response.status == 200:
                        projects = await response.json()
                        for project in projects:
                            if project["status"] != "active":
                                await self.fix_stackblitz_project(project["id"])
            
            self.monitoring_state["last_stackblitz_check"] = datetime.now()
            logging.info("StackBlitz status check completed successfully")
            
        except Exception as e:
            logging.error(f"StackBlitz status check error: {str(e)}")
            await self.handle_error(e)

    async def check_vps_status(self):
        """Check VPS health status"""
        try:
            async with aiohttp.ClientSession() as session:
                for endpoint_name, url in self.vps_endpoints.items():
                    async with session.get(url) as response:
                        if response.status != 200:
                            await self.fix_vps_issues(endpoint_name)
            
            self.monitoring_state["last_vps_check"] = datetime.now()
            logging.info("VPS status check completed successfully")
            
        except Exception as e:
            logging.error(f"VPS status check error: {str(e)}")
            await self.handle_error(e)

    async def perform_system_maintenance(self):
        """Perform regular system maintenance"""
        try:
            # Update dependencies
            await self.update_dependencies()
            
            # Clean up temporary files
            await self.cleanup_temp_files()
            
            # Optimize database
            await self.optimize_database()
            
            # Backup important data
            await self.backup_data()
            
            logging.info("System maintenance completed successfully")
            
        except Exception as e:
            logging.error(f"System maintenance error: {str(e)}")
            await self.handle_error(e)

    async def fix_github_workflow(self, workflow, failed_run):
        """Fix failed GitHub workflow"""
        try:
            # Analyze workflow logs
            logs = failed_run.get_logs()
            
            # Common fixes based on error patterns
            if "npm ERR!" in logs:
                await self.fix_npm_issues()
            elif "Python exception" in logs:
                await self.fix_python_issues()
            
            # Retrigger workflow
            workflow.create_dispatch()
            
            logging.info(f"Fixed GitHub workflow: {workflow.name}")
            
        except Exception as e:
            logging.error(f"Error fixing GitHub workflow: {str(e)}")
            await self.handle_error(e)

    async def fix_netlify_deployment(self):
        """Fix Netlify deployment issues"""
        try:
            # Trigger new deployment
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.netlify_token}"}
                async with session.post(f"https://api.netlify.com/api/v1/sites/{self.netlify_site_id}/deploys", headers=headers) as response:
                    if response.status == 200:
                        logging.info("Successfully triggered new Netlify deployment")
                    
        except Exception as e:
            logging.error(f"Error fixing Netlify deployment: {str(e)}")
            await self.handle_error(e)

    async def fix_stackblitz_project(self, project_id):
        """Fix StackBlitz project issues"""
        try:
            # Restart project
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.stackblitz_token}"}
                async with session.post(f"https://api.stackblitz.com/v1/projects/{project_id}/restart", headers=headers) as response:
                    if response.status == 200:
                        logging.info(f"Successfully restarted StackBlitz project: {project_id}")
                    
        except Exception as e:
            logging.error(f"Error fixing StackBlitz project: {str(e)}")
            await self.handle_error(e)

    async def fix_vps_issues(self, endpoint_name):
        """Fix VPS issues"""
        try:
            # Restart services
            if endpoint_name == "main":
                await self.restart_main_services()
            else:
                await self.restart_backup_services()
            
            logging.info(f"Fixed VPS issues for endpoint: {endpoint_name}")
            
        except Exception as e:
            logging.error(f"Error fixing VPS issues: {str(e)}")
            await self.handle_error(e)

    async def update_dependencies(self):
        """Update system dependencies"""
        try:
            # Update pip packages
            subprocess.run(["pip", "install", "--upgrade", "-r", "requirements.txt"])
            
            # Update npm packages
            subprocess.run(["npm", "update"])
            
            logging.info("Successfully updated dependencies")
            
        except Exception as e:
            logging.error(f"Error updating dependencies: {str(e)}")
            await self.handle_error(e)

    async def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            # Clean temp directories
            temp_dirs = ["./tmp", "./cache", "./logs"]
            for dir_path in temp_dirs:
                if os.path.exists(dir_path):
                    for file in os.listdir(dir_path):
                        file_path = os.path.join(dir_path, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
            
            logging.info("Successfully cleaned up temporary files")
            
        except Exception as e:
            logging.error(f"Error cleaning up temp files: {str(e)}")
            await self.handle_error(e)

    async def optimize_database(self):
        """Optimize database performance"""
        try:
            # Add database optimization logic here
            pass
            
        except Exception as e:
            logging.error(f"Error optimizing database: {str(e)}")
            await self.handle_error(e)

    async def backup_data(self):
        """Backup important data"""
        try:
            # Add backup logic here
            pass
            
        except Exception as e:
            logging.error(f"Error backing up data: {str(e)}")
            await self.handle_error(e)

    async def handle_error(self, error):
        """Handle and log errors"""
        try:
            self.monitoring_state["errors"].append({
                "timestamp": datetime.now(),
                "error": str(error),
                "handled": False
            })
            
            # Implement error handling logic
            if "npm" in str(error):
                await self.fix_npm_issues()
            elif "python" in str(error):
                await self.fix_python_issues()
            elif "network" in str(error):
                await self.fix_network_issues()
            
        except Exception as e:
            logging.error(f"Error in error handler: {str(e)}")

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            filename='system_monitor.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

if __name__ == "__main__":
    monitor = SystemMonitor()
    asyncio.run(monitor.start_monitoring())
