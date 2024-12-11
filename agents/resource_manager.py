import os
import json
import shutil
from pathlib import Path
import subprocess

class ResourceManager:
    def __init__(self):
        self.resource_categories = {
            'email_tools': ['ResponderKing', 'SkyEmailSender', 'EmailFinderScraper'],
            'content_creation': ['AI-Article-Creator', 'ElectroAIWriter', 'CreativeWritingCoach'],
            'crypto_tools': ['Pancakeswap-bot', 'Bitcoin-Surge-Trading-Alpha', 'flash-loans'],
            'marketing_tools': ['seo-pack-pro', 'social-auto-poster', 'TG-Tools'],
            'website_tools': ['wordpress-themes', 'woocommerce-extensions', 'landing-pages']
        }
        
        self.base_path = Path(os.path.dirname(os.path.abspath(__file__))).parent
        self.resource_path = self.base_path / 'resources'
        self.setup_directories()

    def setup_directories(self):
        """Create organized directory structure for resources"""
        for category in self.resource_categories.keys():
            category_path = self.resource_path / category
            category_path.mkdir(parents=True, exist_ok=True)

    def scan_downloads(self, downloads_path):
        """Scan downloads folder for relevant resources"""
        downloads = Path(downloads_path)
        for file in downloads.glob('**/*'):
            if file.is_file():
                self.categorize_resource(file)

    def categorize_resource(self, file_path):
        """Categorize and organize resources"""
        for category, keywords in self.resource_categories.items():
            for keyword in keywords:
                if keyword.lower() in file_path.name.lower():
                    target_path = self.resource_path / category / file_path.name
                    try:
                        shutil.copy2(file_path, target_path)
                        print(f"Copied {file_path.name} to {category}")
                    except Exception as e:
                        print(f"Error copying {file_path.name}: {e}")

    def create_resource_index(self):
        """Create index of all available resources"""
        index = {}
        for category in self.resource_categories.keys():
            category_path = self.resource_path / category
            index[category] = []
            if category_path.exists():
                for file in category_path.glob('*'):
                    index[category].append({
                        'name': file.name,
                        'path': str(file.relative_to(self.base_path)),
                        'size': file.stat().st_size
                    })
        
        index_path = self.resource_path / 'resource_index.json'
        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)

    def deploy_agent_configs(self):
        """Deploy configuration files for AI agents"""
        config = {
            'resource_path': str(self.resource_path),
            'categories': self.resource_categories,
            'update_interval': 3600,  # 1 hour
            'max_concurrent_tasks': 5,
            'logging_level': 'INFO'
        }
        
        config_path = self.base_path / 'agents' / 'config.json'
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

if __name__ == "__main__":
    manager = ResourceManager()
    # Replace with actual downloads path
    downloads_path = "C:/Users/p8tty/Downloads"
    manager.scan_downloads(downloads_path)
    manager.create_resource_index()
    manager.deploy_agent_configs()
