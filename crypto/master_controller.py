import asyncio
from web3 import Web3
import logging
from pathlib import Path
import json
from typing import Dict, List
from strategies.mev_hunter import MEVHunter
from strategies.flash_loan_master import FlashLoanMaster
from strategies.arbitrage_master import ArbitrageMaster

class MasterController:
    def __init__(self):
        self.setup_logging()
        self.web3_connections = self.initialize_connections()
        self.strategies = self.initialize_strategies()
        self.profit_tracker = {
            'mev': 0.0,
            'flash_loans': 0.0,
            'arbitrage': 0.0,
            'total': 0.0
        }
        
    def setup_logging(self):
        logging.basicConfig(
            filename='master_controller.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def initialize_connections(self) -> Dict[str, Web3]:
        """Initialize connections to all supported blockchains"""
        connections = {
            'ethereum': Web3(Web3.HTTPProvider('https://ethereum.publicnode.com')),
            'bsc': Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org')),
            'polygon': Web3(Web3.HTTPProvider('https://polygon-rpc.com')),
            'arbitrum': Web3(Web3.HTTPProvider('https://arb1.arbitrum.io/rpc')),
            'optimism': Web3(Web3.HTTPProvider('https://mainnet.optimism.io')),
            'avalanche': Web3(Web3.HTTPProvider('https://api.avax.network/ext/bc/C/rpc'))
        }
        
        # Test connections
        for chain, w3 in connections.items():
            if w3.is_connected():
                logging.info(f"Connected to {chain}")
            else:
                logging.error(f"Failed to connect to {chain}")
                
        return connections
        
    def initialize_strategies(self) -> Dict:
        """Initialize all trading strategies"""
        return {
            'mev': MEVHunter(self.web3_connections),
            'flash_loans': FlashLoanMaster(self.web3_connections),
            'arbitrage': ArbitrageMaster(self.web3_connections)
        }
        
    async def monitor_profits(self):
        """Monitor and log profits from all strategies"""
        while True:
            try:
                # Update profit tracking
                self.profit_tracker['total'] = sum(
                    value for key, value in self.profit_tracker.items()
                    if key != 'total'
                )
                
                # Log current profits
                logging.info("=== Profit Report ===")
                for strategy, profit in self.profit_tracker.items():
                    logging.info(f"{strategy.capitalize()}: ${profit:,.2f}")
                    
                # Save profit data
                await self.save_profit_data()
                
            except Exception as e:
                logging.error(f"Error monitoring profits: {e}")
                
            await asyncio.sleep(300)  # Update every 5 minutes
            
    async def save_profit_data(self):
        """Save profit data to file"""
        try:
            data_path = Path("data/profits.json")
            data_path.parent.mkdir(exist_ok=True)
            
            with open(data_path, 'w') as f:
                json.dump(self.profit_tracker, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving profit data: {e}")
            
    async def run(self):
        """Run all strategies concurrently"""
        try:
            # Start profit monitoring
            profit_monitor = asyncio.create_task(self.monitor_profits())
            
            # Start all strategies
            strategy_tasks = []
            for strategy_name, strategy in self.strategies.items():
                strategy_tasks.append(asyncio.create_task(strategy.run()))
                logging.info(f"Started {strategy_name} strategy")
                
            # Wait for all tasks
            await asyncio.gather(profit_monitor, *strategy_tasks)
            
        except Exception as e:
            logging.error(f"Error in master controller: {e}")
            
    def update_profit(self, strategy: str, amount: float):
        """Update profit for a specific strategy"""
        if strategy in self.profit_tracker:
            self.profit_tracker[strategy] += amount
            logging.info(f"Updated {strategy} profit: +${amount:,.2f}")
            
async def main():
    controller = MasterController()
    await controller.run()

if __name__ == "__main__":
    asyncio.run(main())
