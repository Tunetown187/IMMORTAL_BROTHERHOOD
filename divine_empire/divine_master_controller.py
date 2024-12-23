import os
import warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Hide console window if running on Windows
try:
    import win32gui
    import win32con
    hwnd = win32gui.GetForegroundWindow()
    win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
except ImportError:
    pass

import asyncio
import logging
from pathlib import Path
from datetime import datetime
import json
import os
from typing import Dict, Any

# Import all divine components
from divine_agents import DivineAgents
from divine_angel_system import DivineAngelSystem
from divine_archangel_system import DivineArchangelSystem
from divine_blockchain_mastery import DivineBlockchainMastery
from divine_crypto_system import DivineCryptoSystem
from divine_expansion_master import DivineExpansionMaster
from divine_knowledge_integration import DivineKnowledgeSystem
from divine_orchestration_system import DivineOrchestrationSystem
from divine_super_intelligence import DivineSuperIntelligence
from divine_swarm import DivineSwarm
from solana_sniper_strategy import SolanaSniper
from trade_monitor import TradeMonitor

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Create handlers with UTF-8 encoding
file_handler = logging.FileHandler(log_dir / "divine_master.log", encoding='utf-8')
error_handler = logging.FileHandler(log_dir / "divine_master_errors.log", encoding='utf-8')
error_handler.setLevel(logging.ERROR)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)

# Setup root logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, error_handler],
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class DivineMasterController:
    def __init__(self):
        self.setup_silent_mode()
        self.load_config()
        self.initialize_components()
        
    def setup_silent_mode(self):
        # Check if running in silent mode
        if os.environ.get('SILENT_MODE', 'False').lower() == 'true':
            # Disable console logging
            logging.getLogger().handlers = [file_handler, error_handler]
        else:
            # Enable console logging
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logging.getLogger().handlers = [file_handler, error_handler, console_handler]
        
    def load_config(self):
        try:
            config_path = Path("config/divine_master_config.json")
            if config_path.exists():
                with open(config_path) as f:
                    self.config = json.load(f)
            else:
                logging.warning("Config not found, using defaults")
                self.config = self.get_default_config()
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            self.config = self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        return {
            "divine_expansion": {
                "auto_scale": True,
                "max_concurrent_missions": 10,
                "resource_allocation": {
                    "ai_research": 0.3,
                    "trading": 0.3,
                    "expansion": 0.2,
                    "knowledge": 0.2
                }
            },
            "trading": {
                "max_concurrent_trades": 5,
                "risk_management": {
                    "max_position_size": 0.1,
                    "stop_loss": 0.1,
                    "take_profit": 0.5
                }
            },
            "ai_enhancement": {
                "auto_learn": True,
                "knowledge_sharing": True,
                "swarm_intelligence": True
            }
        }
    
    def initialize_components(self):
        self.components = {
            "agents": DivineAgents(),
            "angel_system": DivineAngelSystem(),
            "archangel_system": DivineArchangelSystem(),
            "blockchain_mastery": DivineBlockchainMastery(),
            "crypto_system": DivineCryptoSystem(),
            "expansion_master": DivineExpansionMaster(),
            "knowledge_integration": DivineKnowledgeSystem(),
            "orchestration": DivineOrchestrationSystem(),
            "super_intelligence": DivineSuperIntelligence(),
            "swarm": DivineSwarm(),
            "solana_sniper": SolanaSniper(),
            "trade_monitor": TradeMonitor()
        }
        
    async def start_divine_mission(self):
        """Start the divine mission with all components"""
        logging.info("Initiating Divine Master Mission")
        
        try:
            # Start all components
            tasks = []
            for name, component in self.components.items():
                if hasattr(component, 'start') and callable(getattr(component, 'start')):
                    logging.info(f"Starting {name}")
                    tasks.append(asyncio.create_task(component.start()))
            
            # Monitor and coordinate components
            await self.monitor_divine_mission(tasks)
            
        except Exception as e:
            logging.error(f"Error in divine mission: {e}")
            raise
    
    async def monitor_divine_mission(self, tasks):
        """Monitor and coordinate all divine components"""
        while True:
            try:
                # Check component health
                for name, component in self.components.items():
                    if hasattr(component, 'health_check'):
                        status = await component.health_check()
                        if not status['healthy']:
                            logging.warning(f"{name} needs attention: {status['message']}")
                
                # Coordinate resource allocation
                await self.optimize_resources()
                
                # Update mission progress
                self.save_mission_state()
                
            except Exception as e:
                logging.error(f"Error monitoring divine mission: {e}")
            
            await asyncio.sleep(60)  # Check every minute
    
    async def optimize_resources(self):
        """Optimize resource allocation across components"""
        try:
            # Get current resource allocation
            resource_config = self.config["divine_expansion"]["resource_allocation"]
            
            # Get component performance metrics
            performance_metrics = {}
            for name, component in self.components.items():
                if hasattr(component, 'get_state'):
                    state = component.get_state()
                    if isinstance(state, dict):
                        # Extract relevant metrics (profits, success rate, etc.)
                        metrics = {
                            "profits": state.get("total_profits", 0),
                            "success_rate": state.get("success_rate", 0),
                            "divine_power": state.get("total_divine_power", 0)
                        }
                        performance_metrics[name] = metrics
            
            # Adjust resource allocation based on performance
            if performance_metrics:
                total_profits = sum(m["profits"] for m in performance_metrics.values())
                total_success = sum(m["success_rate"] for m in performance_metrics.values())
                total_power = sum(m["divine_power"] for m in performance_metrics.values())
                
                # Calculate new allocation weights
                new_allocation = {}
                for category, current_weight in resource_config.items():
                    components_in_category = [
                        name for name in self.components.keys()
                        if category.lower() in name.lower()
                    ]
                    
                    if components_in_category:
                        # Calculate category performance
                        category_profits = sum(
                            performance_metrics[name]["profits"]
                            for name in components_in_category
                            if name in performance_metrics
                        )
                        category_success = sum(
                            performance_metrics[name]["success_rate"]
                            for name in components_in_category
                            if name in performance_metrics
                        )
                        category_power = sum(
                            performance_metrics[name]["divine_power"]
                            for name in components_in_category
                            if name in performance_metrics
                        )
                        
                        # Calculate new weight based on performance
                        if total_profits > 0:
                            profit_factor = category_profits / total_profits
                        else:
                            profit_factor = 0.25  # Default even distribution
                            
                        if total_success > 0:
                            success_factor = category_success / total_success
                        else:
                            success_factor = 0.25
                            
                        if total_power > 0:
                            power_factor = category_power / total_power
                        else:
                            power_factor = 0.25
                        
                        # Combine factors with weights
                        new_weight = (
                            0.4 * profit_factor +  # Prioritize profit
                            0.3 * success_factor +  # Consider success rate
                            0.3 * power_factor      # Consider divine power
                        )
                        
                        new_allocation[category] = new_weight
                
                # Normalize weights to sum to 1
                total_weight = sum(new_allocation.values())
                if total_weight > 0:
                    for category in new_allocation:
                        new_allocation[category] /= total_weight
                    
                    # Update config with new allocation
                    self.config["divine_expansion"]["resource_allocation"] = new_allocation
                    
                    # Log the optimization
                    logging.info("Resource allocation optimized:")
                    for category, weight in new_allocation.items():
                        logging.info(f"  {category}: {weight:.2%}")
                    
                    # Save updated config
                    config_path = Path("config/divine_master_config.json")
                    with open(config_path, "w") as f:
                        json.dump(self.config, f, indent=2)
        
        except Exception as e:
            logging.error(f"Error optimizing resources: {e}")

    def save_mission_state(self):
        """Save current mission state for crash recovery"""
        try:
            state = {
                "timestamp": datetime.now().isoformat(),
                "components": {},
                "mission_progress": {}
            }
            
            # Collect state from each component
            for name, component in self.components.items():
                if hasattr(component, 'get_state'):
                    state['components'][name] = component.get_state()
            
            # Save state to file
            with open("logs/mission_state.json", "w") as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            logging.error(f"Error saving mission state: {e}")

async def main():
    controller = DivineMasterController()
    await controller.start_divine_mission()

if __name__ == "__main__":
    asyncio.run(main())
