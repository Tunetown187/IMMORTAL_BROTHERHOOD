import asyncio
import logging
from typing import Dict, List
from agent_config_manager import AgentConfigManager
from datetime import datetime
import uuid
import random

class AgentOrchestrator:
    def __init__(self):
        self.config_manager = AgentConfigManager()
        self.active_agents = {}
        self.setup_logging()

        self.business_ideas = {
            "saas": [
                {
                    "name": "AI Content Generator",
                    "description": "Generate blog posts, social media content, and marketing copy",
                    "price": 49.99
                },
                {
                    "name": "AutoGPT Business Assistant",
                    "description": "AI-powered business automation and management",
                    "price": 99.99
                },
                {
                    "name": "Smart Email Marketing",
                    "description": "AI-driven email campaign optimization",
                    "price": 79.99
                }
            ],
            "digital_product": [
                {
                    "name": "AI Business Playbook",
                    "description": "Guide to building AI-powered businesses",
                    "price": 199.99
                },
                {
                    "name": "Automation Scripts Bundle",
                    "description": "Collection of business automation scripts",
                    "price": 299.99
                }
            ],
            "service": [
                {
                    "name": "AI Implementation Service",
                    "description": "Custom AI solution implementation",
                    "price": 999.99
                },
                {
                    "name": "Business Automation Setup",
                    "description": "Setup and configure business automation",
                    "price": 799.99
                }
            ],
            "ai_agency": [
                {
                    "name": "AI Marketing Agency",
                    "description": "Full-service AI marketing automation",
                    "price": 1499.99
                },
                {
                    "name": "AI Development Studio",
                    "description": "Custom AI solution development",
                    "price": 2499.99
                }
            ],
            "automation_service": [
                {
                    "name": "Business Process Automation",
                    "description": "End-to-end business automation solutions",
                    "price": 999.99
                },
                {
                    "name": "Marketing Automation Suite",
                    "description": "Automated marketing campaigns and analytics",
                    "price": 799.99
                }
            ],
            "ai_product": [
                {
                    "name": "AI Content Wizard",
                    "description": "Advanced AI content generation platform",
                    "price": 149.99
                },
                {
                    "name": "AI Sales Assistant",
                    "description": "Automated sales outreach and follow-up",
                    "price": 199.99
                }
            ],
            "digital_agency": [
                {
                    "name": "Full-Stack Agency",
                    "description": "Complete digital transformation service",
                    "price": 2999.99
                },
                {
                    "name": "Growth Hacking Agency",
                    "description": "Data-driven growth strategies",
                    "price": 1999.99
                }
            ],
            "ecommerce": [
                {
                    "name": "AI Shopping Assistant",
                    "description": "Personalized shopping recommendations",
                    "price": 29.99
                },
                {
                    "name": "Dropshipping Automation",
                    "description": "Automated dropshipping business",
                    "price": 499.99
                }
            ],
            "education": [
                {
                    "name": "AI Learning Platform",
                    "description": "Personalized AI education system",
                    "price": 199.99
                },
                {
                    "name": "Business Skills Academy",
                    "description": "Online business training platform",
                    "price": 299.99
                }
            ]
        }

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    async def spawn_agent(self, agent_type: str) -> str:
        """Spawn a new autonomous agent"""
        try:
            # Generate unique agent ID
            agent_id = f"{agent_type}_{str(uuid.uuid4())[:8]}"
            
            # Create agent profile with unique browser fingerprint
            profile = await self.config_manager.create_agent_profile(agent_id)
            
            # Setup browser for the agent
            browser = await self.config_manager.setup_browser(agent_id)
            
            # Initialize agent's resources
            await self._initialize_agent_resources(agent_id, browser)
            
            # Start business operations
            await self._start_business_operations(agent_id)
            
            self.active_agents[agent_id] = {
                "type": agent_type,
                "status": "active",
                "created_at": datetime.now(),
                "browser": browser,
                "profile": profile
            }
            
            self.logger.info(f"Successfully spawned agent {agent_id}")
            return agent_id
            
        except Exception as e:
            self.logger.error(f"Error spawning agent: {str(e)}")
            raise

    async def _start_business_operations(self, agent_id: str):
        """Start agent's business operations"""
        try:
            # Choose a business type
            business_type = random.choice(["saas", "digital_product", "service", "ai_agency", "automation_service", "ai_product", "digital_agency", "ecommerce", "education"])
            
            # Create the business
            business = await self.config_manager.create_business(agent_id, business_type)
            
            # Launch products
            product_ideas = self.business_ideas[business_type]
            for product in random.sample(product_ideas, min(2, len(product_ideas))):
                await self.config_manager.create_and_launch_product(agent_id, {
                    "name": product["name"],
                    "type": business_type,
                    "price": product["price"],
                    "description": product["description"]
                })
                
            self.logger.info(f"Started business operations for agent {agent_id}")
            
        except Exception as e:
            self.logger.error(f"Error starting business operations: {str(e)}")
            raise

    async def _initialize_agent_resources(self, agent_id: str, browser):
        """Initialize necessary resources for an agent"""
        try:
            # Create accounts on necessary services
            services = [
                # AI Services
                "gemini", "mistral", "together_ai", "perplexity",
                # Business Tools
                "ottomator", "boltstarter", "e2b", "superagent",
                # Marketing
                "systeme", "lemlist", "phantombuster",
                # Development
                "railway", "replit", "vercel",
                # Business Services
                "stripe", "gumroad"
            ]
            
            for service in services:
                try:
                    await self.config_manager.create_service_account(agent_id, service, browser)
                    self.logger.info(f"Created {service} account for agent {agent_id}")
                except Exception as e:
                    self.logger.error(f"Error creating {service} account: {str(e)}")
                    continue
                
                await asyncio.sleep(2)  # Prevent rate limiting
                
        except Exception as e:
            self.logger.error(f"Error initializing agent resources: {str(e)}")
            raise

    async def get_agent_status(self, agent_id: str) -> Dict:
        """Get current status of an agent"""
        if agent_id in self.active_agents:
            agent_info = self.active_agents[agent_id]
            profile = await self.config_manager.load_agent_profile(agent_id)
            
            return {
                "agent_id": agent_id,
                "status": agent_info["status"],
                "type": agent_info["type"],
                "created_at": agent_info["created_at"],
                "businesses": profile.get("businesses", {}),
                "products": profile.get("products", []),
                "total_revenue": sum(p.get("revenue", 0) for p in profile.get("products", []))
            }
        else:
            raise ValueError(f"No agent found with ID {agent_id}")

    async def get_business_metrics(self, agent_id: str) -> Dict:
        """Get business metrics for an agent"""
        profile = await self.config_manager.load_agent_profile(agent_id)
        
        metrics = {
            "total_revenue": 0.0,
            "active_products": 0,
            "total_sales": 0,
            "businesses": {}
        }
        
        for business_type, business in profile.get("businesses", {}).items():
            metrics["businesses"][business_type] = {
                "revenue": business.get("revenue", 0.0),
                "products": len(business.get("products", [])),
                "status": business.get("status", "unknown")
            }
            metrics["total_revenue"] += business.get("revenue", 0.0)
            metrics["active_products"] += len(business.get("products", []))
            
        return metrics

# Example usage:
async def main():
    orchestrator = AgentOrchestrator()
    
    # Spawn a new business agent
    agent_id = await orchestrator.spawn_agent("business_builder")
    
    # Get agent status and metrics
    status = await orchestrator.get_agent_status(agent_id)
    metrics = await orchestrator.get_business_metrics(agent_id)
    
    print(f"Agent status: {status}")
    print(f"Business metrics: {metrics}")

if __name__ == "__main__":
    asyncio.run(main())
