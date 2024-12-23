import asyncio
import logging
from datetime import datetime
import json
import os
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
import websockets
import aiohttp
from pathlib import Path

class TradeMonitor:
    def __init__(self):
        self.setup_logging()
        self.load_config()
        self.client = AsyncClient(self.rpc_url, commitment=Confirmed)
        self.active_trades = {}
        self.transaction_history = []
        
    def setup_logging(self):
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger("TradeMonitor")
        self.logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler(log_dir / "trade_monitor.log")
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def load_config(self):
        try:
            config_path = Path("config/monitor_config.json")
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
                    self.rpc_url = config.get("rpc_url")
                    self.wallet_address = config.get("wallet_address")
            else:
                self.logger.warning("Config file not found, using environment variables")
                self.rpc_url = os.getenv("SOLANA_RPC_URL")
                self.wallet_address = os.getenv("SOLANA_WALLET_ADDRESS")
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            raise

    async def monitor_transactions(self):
        while True:
            try:
                # Get recent transactions for the wallet
                transactions = await self.client.get_signatures_for_address(self.wallet_address)
                
                for tx in transactions.value:
                    if tx.signature not in [t["signature"] for t in self.transaction_history]:
                        tx_details = await self.client.get_transaction(tx.signature)
                        self.transaction_history.append({
                            "signature": tx.signature,
                            "timestamp": datetime.fromtimestamp(tx.block_time),
                            "status": "confirmed" if tx.err is None else "failed",
                            "details": tx_details
                        })
                        
                        self.logger.info(f"New transaction detected: {tx.signature}")
                        self.logger.info(f"Status: {'Success' if tx.err is None else 'Failed'}")
                        
                # Save transaction history
                self.save_transaction_history()
                
            except Exception as e:
                self.logger.error(f"Error monitoring transactions: {e}")
            
            await asyncio.sleep(10)  # Check every 10 seconds

    def save_transaction_history(self):
        try:
            with open("logs/transaction_history.json", "w") as f:
                json.dump(self.transaction_history, f, default=str, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving transaction history: {e}")

    async def start_monitoring(self):
        self.logger.info("Starting trade monitor...")
        await self.monitor_transactions()

if __name__ == "__main__":
    monitor = TradeMonitor()
    asyncio.run(monitor.start_monitoring())
