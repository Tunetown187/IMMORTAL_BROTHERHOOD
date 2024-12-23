import json
import logging
from pathlib import Path
import asyncio
import time
import os

class BaseAgent:
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.base_path = Path(os.path.dirname(os.path.abspath(__file__))).parent
        self.config = self.load_config()
        self.setup_logging()
        self.resources = self.load_resources()
        self.active = True

    def load_config(self):
        """Load agent configuration"""
        config_path = self.base_path / 'agents' / 'config.json'
        with open(config_path, 'r') as f:
            return json.load(f)

    def setup_logging(self):
        """Setup logging for the agent"""
        log_path = self.base_path / 'logs' / f'{self.agent_name}.log'
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            filename=str(log_path),
            level=self.config.get('logging_level', 'INFO'),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.agent_name)

    def load_resources(self):
        """Load available resources"""
        resource_index = self.base_path / 'resources' / 'resource_index.json'
        if resource_index.exists():
            with open(resource_index, 'r') as f:
                return json.load(f)
        return {}

    async def run(self):
        """Main agent loop"""
        self.logger.info(f"Agent {self.agent_name} starting...")
        while self.active:
            try:
                await self.execute_tasks()
                await asyncio.sleep(self.config.get('update_interval', 3600))
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying

    async def execute_tasks(self):
        """Execute agent-specific tasks"""
        raise NotImplementedError("Subclasses must implement execute_tasks")

    def get_resource_path(self, category, resource_name):
        """Get path to a specific resource"""
        if category in self.resources:
            for resource in self.resources[category]:
                if resource['name'] == resource_name:
                    return self.base_path / resource['path']
        return None

    async def report_status(self):
        """Report agent status"""
        status = {
            'agent_name': self.agent_name,
            'timestamp': time.time(),
            'status': 'active',
            'last_task': None,
            'errors': []
        }
        status_path = self.base_path / 'status' / f'{self.agent_name}_status.json'
        status_path.parent.mkdir(parents=True, exist_ok=True)
        with open(status_path, 'w') as f:
            json.dump(status, f, indent=2)

    def stop(self):
        """Stop the agent"""
        self.active = False
        self.logger.info(f"Agent {self.agent_name} stopping...")
