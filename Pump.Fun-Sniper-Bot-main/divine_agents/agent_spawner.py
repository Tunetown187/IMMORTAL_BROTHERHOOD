import asyncio
from typing import Dict, List
import uuid
from optimized_agent import SuperAgent, AgentConfig
from shared_resources import SHARED_RESOURCES
import logging
import psutil
import numpy as np

class AgentSpawner:
    """Efficient agent spawning and management"""
    
    def __init__(self):
        self.agents: Dict[str, SuperAgent] = {}
        self.configs: Dict[str, AgentConfig] = {}
        self._setup_logging()
        self._spawn_lock = asyncio.Lock()
        
    async def spawn_agents(self, count: int, agent_type: str):
        """Spawn multiple agents efficiently"""
        async with self._spawn_lock:
            # Calculate available resources
            available_memory = psutil.virtual_memory().available
            memory_per_agent = 1024 * 1024  # 1MB per agent
            max_agents = min(
                count,
                int(available_memory * 0.8 / memory_per_agent)
            )
            
            # Spawn agents in batches
            batch_size = 100
            for i in range(0, max_agents, batch_size):
                batch_count = min(batch_size, max_agents - i)
                await self._spawn_batch(batch_count, agent_type)
                
            self.logger.info(f"Spawned {max_agents} agents of type {agent_type}")
            
    async def _spawn_batch(self, count: int, agent_type: str):
        """Spawn a batch of agents efficiently"""
        spawn_tasks = []
        for _ in range(count):
            agent_id = str(uuid.uuid4())
            config = AgentConfig()  # Full capabilities enabled
            agent = SuperAgent(agent_id, agent_type, config)
            
            self.agents[agent_id] = agent
            self.configs[agent_id] = config
            
            spawn_tasks.append(agent.initialize())
            
        # Initialize all agents in parallel
        await asyncio.gather(*spawn_tasks)
        
        # Start agent operations
        for agent in self.agents.values():
            asyncio.create_task(agent.run())
            
    async def monitor_agents(self):
        """Monitor and manage agents efficiently"""
        while True:
            try:
                # Check agent health
                for agent_id, agent in list(self.agents.items()):
                    if not await self._check_agent_health(agent):
                        await self._restart_agent(agent_id)
                        
                # Monitor system resources
                mem = psutil.virtual_memory()
                if mem.percent > 90:
                    await self._reduce_agents()
                elif mem.percent < 50:
                    await self._increase_agents()
                    
            except Exception as e:
                self.logger.error(f"Agent monitoring error: {str(e)}")
                
            await asyncio.sleep(1)
            
    async def _check_agent_health(self, agent: SuperAgent) -> bool:
        """Check if agent is healthy"""
        try:
            # Verify agent is responsive
            async with asyncio.timeout(1):
                return agent.state is not None
        except asyncio.TimeoutError:
            return False
            
    async def _restart_agent(self, agent_id: str):
        """Restart failed agent"""
        try:
            old_agent = self.agents[agent_id]
            config = self.configs[agent_id]
            
            # Create new agent with same config
            new_agent = SuperAgent(agent_id, old_agent.agent_type, config)
            await new_agent.initialize()
            
            # Replace old agent
            self.agents[agent_id] = new_agent
            asyncio.create_task(new_agent.run())
            
            self.logger.info(f"Restarted agent {agent_id}")
            
        except Exception as e:
            self.logger.error(f"Agent restart failed: {str(e)}")
            
    async def _reduce_agents(self):
        """Reduce agent count when resources are low"""
        if len(self.agents) > 100:
            agents_to_remove = sorted(
                self.agents.keys(),
                key=lambda x: self.agents[x].state.memory_view.nbytes,
                reverse=True
            )[:100]
            
            for agent_id in agents_to_remove:
                await SHARED_RESOURCES.unregister_agent(agent_id)
                del self.agents[agent_id]
                del self.configs[agent_id]
                
    async def _increase_agents(self):
        """Increase agents when resources are available"""
        current_count = len(self.agents)
        available_memory = psutil.virtual_memory().available
        memory_per_agent = 1024 * 1024  # 1MB per agent
        
        can_add = int(available_memory * 0.5 / memory_per_agent)
        if can_add > 100:
            await self.spawn_agents(100, "standard")
            
    def _setup_logging(self):
        """Setup spawner logging"""
        self.logger = logging.getLogger("AgentSpawner")
        self.logger.setLevel(logging.INFO)
        
# Global spawner instance
AGENT_SPAWNER = AgentSpawner()
