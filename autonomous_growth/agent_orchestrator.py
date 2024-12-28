import logging
import asyncio
from typing import Dict, List
from agent_config_manager import AgentConfigManager
import streamlit as st

class AgentOrchestrator:
    def __init__(self):
        self.setup_logging()
        self.config_manager = AgentConfigManager()
        self.active_agents = {}
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    async def deploy_agent(self, agent_type: str, config: Dict = None) -> str:
        """Deploy a new agent instance"""
        try:
            if not config:
                config = self.config_manager.get_agent_config(agent_type)
                
            if not config:
                raise ValueError(f"No configuration found for agent type: {agent_type}")
                
            agent_id = f"{agent_type}_{len(self.active_agents) + 1}"
            self.active_agents[agent_id] = {
                "type": agent_type,
                "config": config,
                "status": "active",
                "tasks": []
            }
            
            self.logger.info(f"Deployed agent: {agent_id}")
            return agent_id
            
        except Exception as e:
            self.logger.error(f"Error deploying agent: {str(e)}")
            raise
            
    async def terminate_agent(self, agent_id: str) -> bool:
        """Terminate an active agent"""
        try:
            if agent_id in self.active_agents:
                self.active_agents[agent_id]["status"] = "terminated"
                self.logger.info(f"Terminated agent: {agent_id}")
                return True
            else:
                self.logger.warning(f"Agent not found: {agent_id}")
                return False
        except Exception as e:
            self.logger.error(f"Error terminating agent: {str(e)}")
            return False
            
    def get_active_agents(self) -> List[Dict]:
        """Get list of active agents and their status"""
        return [
            {
                "id": agent_id,
                "type": info["type"],
                "status": info["status"]
            }
            for agent_id, info in self.active_agents.items()
            if info["status"] == "active"
        ]
        
    async def assign_task(self, agent_id: str, task: Dict) -> bool:
        """Assign a task to an agent"""
        try:
            if agent_id in self.active_agents:
                if self.active_agents[agent_id]["status"] == "active":
                    self.active_agents[agent_id]["tasks"].append(task)
                    self.logger.info(f"Assigned task to agent {agent_id}")
                    return True
                else:
                    self.logger.warning(f"Agent {agent_id} is not active")
                    return False
            else:
                self.logger.warning(f"Agent not found: {agent_id}")
                return False
        except Exception as e:
            self.logger.error(f"Error assigning task: {str(e)}")
            return False
            
    def get_agent_status(self, agent_id: str) -> Dict:
        """Get current status of an agent"""
        if agent_id in self.active_agents:
            agent = self.active_agents[agent_id]
            return {
                "id": agent_id,
                "type": agent["type"],
                "status": agent["status"],
                "task_count": len(agent["tasks"])
            }
        else:
            return {"error": "Agent not found"}
