import asyncio
import logging
from datetime import datetime
from pathlib import Path
from agents.state_manager import state_manager
from agents.agent_deployment import AgentController
from agents.crypto_agent import CryptoAgent
from agents.mega_controller import MegaController

class StartupManager:
    def __init__(self):
        self.setup_logging()
        self.state = state_manager
        self.agent_controller = AgentController()
        self.crypto_agent = CryptoAgent()
        self.mega_controller = MegaController()
        
    def setup_logging(self):
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            filename=f"logs/system_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
    async def startup_sequence(self):
        try:
            logging.info("Starting system initialization...")
            
            # Load previous state
            current_state = self.state.load_state()
            logging.info(f"Loaded previous state from {current_state['last_updated']}")
            
            # Start state auto-save
            asyncio.create_task(self.state.auto_save())
            
            # Initialize all subsystems
            tasks = [
                self.agent_controller.run(),
                self.crypto_agent.run(),
                self.mega_controller.run()
            ]
            
            # Run all systems concurrently
            await asyncio.gather(*tasks)
            
        except Exception as e:
            logging.error(f"Startup sequence failed: {str(e)}")
            self.state.log_error(f"Startup failure: {str(e)}")
            raise

if __name__ == "__main__":
    startup = StartupManager()
    asyncio.run(startup.startup_sequence())
