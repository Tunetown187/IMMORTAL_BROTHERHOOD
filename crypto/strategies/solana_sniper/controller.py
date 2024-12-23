import asyncio
from typing import List, Dict
from datetime import datetime
from agents.sniper_agent import SolanaSniperAgent
from core.divine_master_bot import DivineMasterBot

class SniperController:
    """Controller for managing Solana Sniper Bot agents"""
    
    def __init__(self):
        self.agents: List[SolanaSniperAgent] = []
        self.divine_bot = DivineMasterBot()
        self.active = False
        self.start_time = None
        
    async def initialize(self):
        """Initialize the controller and its agents"""
        try:
            # Load configuration
            await self.divine_bot._load_config()
            
            # Create agents
            await self._create_agents()
            
            # Initialize logging
            self._setup_logging()
            
            self.logger.info("Sniper Controller initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing controller: {str(e)}")
            raise
            
    async def _create_agents(self):
        """Create and configure sniper agents"""
        try:
            # Create main sniper agent
            main_agent = SolanaSniperAgent(name="MainSniper")
            self.agents.append(main_agent)
            
            # Create specialized agents if needed
            if self.divine_bot.config.get("use_arbitrage", False):
                arb_agent = SolanaSniperAgent(name="ArbitrageSniper")
                self.agents.append(arb_agent)
                
            if self.divine_bot.config.get("use_social_signals", False):
                social_agent = SolanaSniperAgent(name="SocialSniper")
                self.agents.append(social_agent)
                
        except Exception as e:
            self.logger.error(f"Error creating agents: {str(e)}")
            raise
            
    def _setup_logging(self):
        """Setup logging for the controller"""
        import logging
        
        # Create logger
        self.logger = logging.getLogger("SniperController")
        self.logger.setLevel(logging.INFO)
        
        # Create handlers
        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler("logs/sniper_controller.log")
        
        # Create formatters
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        
    async def start(self):
        """Start all agents"""
        try:
            self.active = True
            self.start_time = datetime.now()
            
            # Start all agents
            start_tasks = [agent.start() for agent in self.agents]
            await asyncio.gather(*start_tasks)
            
            self.logger.info("All agents started successfully")
            
            # Start monitoring
            await self._monitor_agents()
            
        except Exception as e:
            self.logger.error(f"Error starting agents: {str(e)}")
            await self.stop()
            
    async def stop(self):
        """Stop all agents"""
        self.active = False
        try:
            # Stop all agents
            stop_tasks = [agent.stop() for agent in self.agents]
            await asyncio.gather(*stop_tasks)
            
            self.logger.info("All agents stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping agents: {str(e)}")
            
    async def _monitor_agents(self):
        """Monitor agent performance and health"""
        while self.active:
            try:
                for agent in self.agents:
                    # Check agent health
                    if agent.last_scan:
                        time_since_scan = (datetime.now() - agent.last_scan).seconds
                        if time_since_scan > agent.scan_interval * 2:
                            self.logger.warning(f"Agent {agent.name} may be stuck. Last scan: {time_since_scan}s ago")
                            
                    # Get agent stats
                    stats = agent.divine_bot._calculate_divine_stats()
                    self.logger.info(f"Agent {agent.name} stats: {stats}")
                    
            except Exception as e:
                self.logger.error(f"Error monitoring agents: {str(e)}")
                
            await asyncio.sleep(60)  # Check every minute
            
    def get_performance_stats(self) -> Dict:
        """Get overall performance statistics"""
        try:
            stats = {
                "uptime": (datetime.now() - self.start_time).seconds if self.start_time else 0,
                "active_agents": len([a for a in self.agents if a.active]),
                "total_agents": len(self.agents),
                "total_profit": sum(a.divine_bot.profit_stats["total"] for a in self.agents),
                "total_trades": sum(
                    a.divine_bot.profit_stats["wins"] + a.divine_bot.profit_stats["losses"] 
                    for a in self.agents
                )
            }
            return stats
        except Exception as e:
            self.logger.error(f"Error getting performance stats: {str(e)}")
            return {}
