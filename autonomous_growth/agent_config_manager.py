import logging
import json
from typing import Dict, List
import streamlit as st
from datetime import datetime
import random

class AgentConfigManager:
    def __init__(self):
        self.setup_logging()
        self.load_default_configs()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def load_default_configs(self):
        """Load default configurations for different agent types"""
        self.agent_configs = {
            "marketing": {
                "name": "Marketing Agent",
                "description": "Handles marketing campaigns and content creation",
                "capabilities": ["content_creation", "campaign_management", "analytics"],
                "settings": {
                    "content_types": ["blog", "social", "email"],
                    "platforms": ["twitter", "linkedin", "medium"],
                    "posting_frequency": "daily"
                }
            },
            "sales": {
                "name": "Sales Agent",
                "description": "Manages sales processes and customer relationships",
                "capabilities": ["lead_generation", "deal_management", "reporting"],
                "settings": {
                    "lead_sources": ["website", "referral", "social"],
                    "follow_up_interval": 3,
                    "deal_stages": ["prospect", "qualified", "proposal", "closed"]
                }
            },
            "support": {
                "name": "Support Agent",
                "description": "Provides customer support and issue resolution",
                "capabilities": ["ticket_management", "knowledge_base", "customer_communication"],
                "settings": {
                    "response_time": "4h",
                    "priority_levels": ["low", "medium", "high", "urgent"],
                    "channels": ["email", "chat", "phone"]
                }
            }
        }
        
    def get_agent_config(self, agent_type: str) -> Dict:
        """Get configuration for a specific agent type"""
        if agent_type in self.agent_configs:
            return self.agent_configs[agent_type]
        else:
            self.logger.error(f"Unknown agent type: {agent_type}")
            return {}
            
    def update_agent_config(self, agent_type: str, new_config: Dict) -> bool:
        """Update configuration for a specific agent type"""
        try:
            if agent_type in self.agent_configs:
                self.agent_configs[agent_type].update(new_config)
                self.logger.info(f"Updated config for {agent_type}")
                return True
            else:
                self.logger.error(f"Unknown agent type: {agent_type}")
                return False
        except Exception as e:
            self.logger.error(f"Error updating config: {str(e)}")
            return False
            
    def list_agent_types(self) -> List[str]:
        """Get list of available agent types"""
        return list(self.agent_configs.keys())
        
    def validate_config(self, config: Dict) -> bool:
        """Validate agent configuration"""
        required_fields = ["name", "description", "capabilities", "settings"]
        return all(field in config for field in required_fields)
        
    async def create_agent_profile(self, agent_id: str) -> Dict:
        """Create a new agent profile"""
        profile = {
            "id": agent_id,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "metrics": {
                "tasks_completed": 0,
                "success_rate": 0.0,
                "uptime": 0
            }
        }
        return profile
