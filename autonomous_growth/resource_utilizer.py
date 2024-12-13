import asyncio
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List
import aiohttp
import os

class ResourceUtilizer:
    def __init__(self):
        self.base_dir = Path("c:/Users/p8tty/Downloads/agency-swarm-0.2.0")
        self.downloads_dir = Path("c:/Users/p8tty/Downloads")
        self.setup_logging()
        
        self.resource_types = {
            "landing_pages": [
                "landing-page-generator-main",
                "CPA Landing Page Collection",
                "MEGA Pack, 250 clean and ready pre-landers"
            ],
            "saas_templates": [
                "best-saas-kit-master",
                "bolt.diy-main",
                "bolt.new-any-llm-main"
            ],
            "crypto_resources": [
                "1000 crypto info",
                "Crypto Generator",
                "flashloans",
                "arbitrage-bot-main"
            ],
            "ai_tools": [
                "AI-Article-Creator",
                "AI-Web-Scraper-main",
                "CreativeWritingCoach-main",
                "MoneyPrinter-Enhanced-main"
            ],
            "marketing_tools": [
                "Email-Finder-Scraper",
                "GMB tools",
                "Instagram-Tagger",
                "SEO tools"
            ]
        }

    async def organize_all_resources(self):
        """Organize and utilize all available resources"""
        try:
            # Create resource directories
            await self.create_resource_structure()
            
            # Organize resources by type
            await self.organize_resources()
            
            # Setup resource databases
            await self.setup_resource_databases()
            
            # Initialize resource managers
            await self.initialize_resource_managers()
            
        except Exception as e:
            logging.error(f"Resource organization error: {str(e)}")
            raise

    async def create_resource_structure(self):
        """Create organized resource structure"""
        resource_dirs = {
            "landing_pages": {
                "templates": True,
                "assets": True,
                "scripts": True
            },
            "saas_templates": {
                "bolt_diy": True,
                "best_saas": True,
                "components": True
            },
            "crypto_tools": {
                "trading_bots": True,
                "flash_loans": True,
                "arbitrage": True
            },
            "ai_systems": {
                "content_creation": True,
                "automation": True,
                "analysis": True
            },
            "marketing": {
                "email": True,
                "social": True,
                "seo": True
            }
        }
        
        for category, subdirs in resource_dirs.items():
            category_dir = self.base_dir / "resources" / category
            category_dir.mkdir(parents=True, exist_ok=True)
            
            for subdir, enabled in subdirs.items():
                if enabled:
                    (category_dir / subdir).mkdir(exist_ok=True)

    async def organize_resources(self):
        """Organize resources into appropriate directories"""
        for resource_type, patterns in self.resource_types.items():
            target_dir = self.base_dir / "resources" / resource_type
            target_dir.mkdir(parents=True, exist_ok=True)
            
            for pattern in patterns:
                for source in self.downloads_dir.glob(f"*{pattern}*"):
                    if source.is_file():
                        shutil.copy2(source, target_dir / source.name)
                    elif source.is_dir():
                        shutil.copytree(source, target_dir / source.name, dirs_exist_ok=True)

    async def setup_resource_databases(self):
        """Setup databases to track resources"""
        databases = {
            "landing_pages": {
                "templates": [],
                "components": [],
                "assets": []
            },
            "saas_templates": {
                "bolt_components": [],
                "api_integrations": [],
                "ui_templates": []
            },
            "crypto_tools": {
                "trading_strategies": [],
                "smart_contracts": [],
                "arbitrage_opportunities": []
            },
            "ai_systems": {
                "models": [],
                "prompts": [],
                "datasets": []
            },
            "marketing": {
                "email_templates": [],
                "social_campaigns": [],
                "seo_strategies": []
            }
        }
        
        db_dir = self.base_dir / "resources" / "databases"
        db_dir.mkdir(parents=True, exist_ok=True)
        
        for db_name, structure in databases.items():
            with open(db_dir / f"{db_name}.json", "w") as f:
                json.dump(structure, f, indent=4)

    async def initialize_resource_managers(self):
        """Initialize resource management systems"""
        managers = {
            "landing_pages": self.manage_landing_pages,
            "saas_templates": self.manage_saas_templates,
            "crypto_tools": self.manage_crypto_tools,
            "ai_systems": self.manage_ai_systems,
            "marketing": self.manage_marketing_tools
        }
        
        for manager_name, manager_func in managers.items():
            await manager_func()

    async def manage_landing_pages(self):
        """Manage landing page resources"""
        landing_pages_dir = self.base_dir / "resources" / "landing_pages"
        
        # Process landing page templates
        templates = list(landing_pages_dir.glob("**/*.html"))
        for template in templates:
            await self.process_landing_page(template)

    async def manage_saas_templates(self):
        """Manage SaaS template resources"""
        saas_dir = self.base_dir / "resources" / "saas_templates"
        
        # Process Bolt.DIY templates
        bolt_templates = saas_dir / "bolt_diy"
        if bolt_templates.exists():
            await self.process_bolt_templates(bolt_templates)
        
        # Process Best-SaaS-Kit templates
        saas_kit = saas_dir / "best_saas"
        if saas_kit.exists():
            await self.process_saas_kit(saas_kit)

    async def manage_crypto_tools(self):
        """Manage crypto tool resources"""
        crypto_dir = self.base_dir / "resources" / "crypto_tools"
        
        # Process trading bots
        trading_bots = list(crypto_dir.glob("**/trading*.py"))
        for bot in trading_bots:
            await self.process_trading_bot(bot)
        
        # Process flash loan contracts
        flash_loans = list(crypto_dir.glob("**/flash*.sol"))
        for contract in flash_loans:
            await self.process_flash_loan(contract)

    async def manage_ai_systems(self):
        """Manage AI system resources"""
        ai_dir = self.base_dir / "resources" / "ai_systems"
        
        # Process AI models
        models = list(ai_dir.glob("**/*.onnx"))
        for model in models:
            await self.process_ai_model(model)
        
        # Process prompts
        prompts = list(ai_dir.glob("**/*.json"))
        for prompt_file in prompts:
            await self.process_prompts(prompt_file)

    async def manage_marketing_tools(self):
        """Manage marketing tool resources"""
        marketing_dir = self.base_dir / "resources" / "marketing"
        
        # Process email tools
        email_tools = list(marketing_dir.glob("**/email*.py"))
        for tool in email_tools:
            await self.process_email_tool(tool)
        
        # Process SEO tools
        seo_tools = list(marketing_dir.glob("**/seo*.py"))
        for tool in seo_tools:
            await self.process_seo_tool(tool)

    async def process_landing_page(self, template_path: Path):
        """Process a landing page template"""
        try:
            # Create output directory
            output_dir = self.base_dir / "resources" / "landing_pages" / "processed"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy template to output directory
            shutil.copy2(template_path, output_dir / template_path.name)
            
            logging.info(f"Processed landing page template: {template_path.name}")
            
        except Exception as e:
            logging.error(f"Error processing landing page {template_path}: {str(e)}")

    async def process_bolt_templates(self, templates_dir: Path):
        """Process Bolt.DIY templates"""
        try:
            # Create output directory
            output_dir = self.base_dir / "resources" / "saas_templates" / "processed_bolt"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy templates
            if templates_dir.is_dir():
                shutil.copytree(templates_dir, output_dir / templates_dir.name, dirs_exist_ok=True)
            
            logging.info(f"Processed Bolt templates from: {templates_dir}")
            
        except Exception as e:
            logging.error(f"Error processing Bolt templates: {str(e)}")

    async def process_saas_kit(self, kit_dir: Path):
        """Process Best-SaaS-Kit templates"""
        try:
            # Create output directory
            output_dir = self.base_dir / "resources" / "saas_templates" / "processed_saas_kit"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy templates
            if kit_dir.is_dir():
                shutil.copytree(kit_dir, output_dir / kit_dir.name, dirs_exist_ok=True)
            
            logging.info(f"Processed SaaS Kit from: {kit_dir}")
            
        except Exception as e:
            logging.error(f"Error processing SaaS Kit: {str(e)}")

    async def process_trading_bot(self, bot_path: Path):
        """Process trading bot script"""
        try:
            # Create output directory
            output_dir = self.base_dir / "resources" / "crypto_tools" / "processed_bots"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy bot script
            shutil.copy2(bot_path, output_dir / bot_path.name)
            
            logging.info(f"Processed trading bot: {bot_path.name}")
            
        except Exception as e:
            logging.error(f"Error processing trading bot {bot_path}: {str(e)}")

    async def process_flash_loan(self, contract_path: Path):
        """Process flash loan contract"""
        try:
            # Create output directory
            output_dir = self.base_dir / "resources" / "crypto_tools" / "processed_contracts"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy contract
            shutil.copy2(contract_path, output_dir / contract_path.name)
            
            logging.info(f"Processed flash loan contract: {contract_path.name}")
            
        except Exception as e:
            logging.error(f"Error processing flash loan contract {contract_path}: {str(e)}")

    async def process_ai_model(self, model_path: Path):
        """Process AI model"""
        try:
            # Create output directory
            output_dir = self.base_dir / "resources" / "ai_systems" / "processed_models"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy model
            shutil.copy2(model_path, output_dir / model_path.name)
            
            logging.info(f"Processed AI model: {model_path.name}")
            
        except Exception as e:
            logging.error(f"Error processing AI model {model_path}: {str(e)}")

    async def process_prompts(self, prompt_path: Path):
        """Process AI prompts"""
        try:
            # Create output directory
            output_dir = self.base_dir / "resources" / "ai_systems" / "processed_prompts"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy prompts
            shutil.copy2(prompt_path, output_dir / prompt_path.name)
            
            logging.info(f"Processed prompts: {prompt_path.name}")
            
        except Exception as e:
            logging.error(f"Error processing prompts {prompt_path}: {str(e)}")

    async def process_email_tool(self, tool_path: Path):
        """Process email marketing tool"""
        try:
            # Create output directory
            output_dir = self.base_dir / "resources" / "marketing" / "processed_email_tools"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy tool
            shutil.copy2(tool_path, output_dir / tool_path.name)
            
            logging.info(f"Processed email tool: {tool_path.name}")
            
        except Exception as e:
            logging.error(f"Error processing email tool {tool_path}: {str(e)}")

    async def process_seo_tool(self, tool_path: Path):
        """Process SEO tool"""
        try:
            # Create output directory
            output_dir = self.base_dir / "resources" / "marketing" / "processed_seo_tools"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy tool
            shutil.copy2(tool_path, output_dir / tool_path.name)
            
            logging.info(f"Processed SEO tool: {tool_path.name}")
            
        except Exception as e:
            logging.error(f"Error processing SEO tool {tool_path}: {str(e)}")

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            filename='resource_utilizer.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

if __name__ == "__main__":
    utilizer = ResourceUtilizer()
    asyncio.run(utilizer.organize_all_resources())
