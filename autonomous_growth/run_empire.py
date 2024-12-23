import asyncio
import signal
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Import all empire components
from empire_builder import EmpireBuilder
from ai_researcher import AIResearcher
from divine_empire.solana_sniper_strategy import SolanaSniper
from cost_optimizer import CostOptimizer
from empire_expander import EmpireExpander
from resource_utilizer import ResourceUtilizer
from smart_scaling_system import SmartScalingSystem

class EmpireController:
    def __init__(self):
        self.base_dir = Path("c:/Users/p8tty/Downloads/agency-swarm-0.2.0")
        self.setup_logging()
        self.load_config()
        self.shutdown = False
        
        # Initialize all components
        self.components = {
            "builder": EmpireBuilder(),
            "researcher": AIResearcher(),
            "sniper": SolanaSniper(),
            "optimizer": CostOptimizer(),
            "expander": EmpireExpander(),
            "utilizer": ResourceUtilizer(),
            "scaler": SmartScalingSystem()
        }
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('empire_controller.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('EmpireController')
        
    def load_config(self):
        """Load empire configuration"""
        config_path = self.base_dir / 'autonomous_growth/config/empire_config.json'
        with open(config_path) as f:
            self.config = json.load(f)
            
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info("🛑 Received shutdown signal. Gracefully stopping all components...")
        self.shutdown = True
        
    async def monitor_performance(self):
        """Monitor overall empire performance"""
        while not self.shutdown:
            try:
                # Collect metrics from all components
                metrics = {}
                for name, component in self.components.items():
                    if hasattr(component, 'get_metrics'):
                        metrics[name] = await component.get_metrics()
                
                # Log performance
                self.logger.info(f"Empire Performance Metrics: {metrics}")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error monitoring performance: {str(e)}")
                
    async def run(self):
        """Run all empire components"""
        try:
            # Setup signal handlers
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            
            self.logger.info("""
            🏰 Divine Empire Control Center 🏰
            ================================
            🚀 Starting all empire components...
            """)
            
            # Start all components
            tasks = []
            
            # Empire Builder
            if self.config['empire_settings']['auto_expansion']:
                tasks.append(self.components['builder'].build_empire())
            
            # AI Researcher
            if self.config['ai_empire']['research']['enabled']:
                tasks.append(self.components['researcher'].start_research())
            
            # Solana Sniper
            if self.config['crypto_empire']['trading']['enabled']:
                tasks.append(self.components['sniper'].monitor_tokens())
            
            # Cost Optimizer
            tasks.append(self.components['optimizer'].optimize_costs())
            
            # Empire Expander
            tasks.append(self.components['expander'].expand_empire())
            
            # Resource Utilizer
            tasks.append(self.components['utilizer'].optimize_resources())
            
            # Smart Scaling
            tasks.append(self.components['scaler'].scale_systems())
            
            # Performance Monitoring
            tasks.append(self.monitor_performance())
            
            # Run everything
            await asyncio.gather(*tasks)
            
        except Exception as e:
            self.logger.error(f"Fatal error in Empire Controller: {str(e)}")
            raise

if __name__ == "__main__":
    controller = EmpireController()
    try:
        asyncio.run(controller.run())
    except KeyboardInterrupt:
        print("\n👋 Divine Empire shutdown complete")
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)
