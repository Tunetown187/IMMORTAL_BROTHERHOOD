import asyncio
from agent_spawner import AGENT_SPAWNER
from shared_resources import SHARED_RESOURCES
import logging
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
import json
import os

# Setup root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("immortals.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class ImmortalBrotherhood:
    def __init__(self):
        self._setup_logging()
        self.client = AsyncClient("https://api.mainnet-beta.solana.com")
        self.keypair = Keypair.from_base58_string(
            "2FFhe61Db5oHyYQ5yQ6QN5mnsUMpSwJ8kNQPvrC23L18o2uNkCR4V3y7QzWkTpWvHX6YJqB7BNyz6kNE1EUDuBjW"
        )
        
    def _setup_logging(self):
        self.logger = logging.getLogger("ImmortalBrotherhood")
        self.logger.setLevel(logging.INFO)

    async def verify_wallet(self):
        """Verify wallet balance"""
        try:
            balance = await self.client.get_balance(self.keypair.pubkey())
            sol_balance = balance.value / 1e9
            self.logger.info(f"Wallet Balance: {sol_balance} SOL")
            if sol_balance < 0.1:
                raise Exception(f"Insufficient balance: {sol_balance} SOL")
            return True
        except Exception as e:
            self.logger.error(f"Wallet verification failed: {str(e)}")
            return False

    async def launch_immortals(self):
        """Launch the Immortal Brotherhood"""
        try:
            self.logger.info("🔥 Launching Immortal Brotherhood 🔥")
            
            # Verify wallet first
            if not await self.verify_wallet():
                raise Exception("Wallet verification failed")

            # Define the 6 immortal agents
            immortals = [
                ("Archangel", "Supreme Commander"),
                ("Seraphim", "Market Oracle"),
                ("Cherubim", "Trade Executor"),
                ("Dominion", "Risk Guardian"),
                ("Virtue", "Profit Optimizer"),
                ("Power", "Strategy Master")
            ]

            # Launch each immortal
            for rank, role in immortals:
                self.logger.info(f"⚡ Summoning {rank} - {role} ⚡")
                await AGENT_SPAWNER.spawn_agents(1, f"{rank}_{role}")
                await asyncio.sleep(2)  # Brief pause between spawns

            self.logger.info("🚀 Immortal Brotherhood Activated 🚀")
            
            # Monitor and scale
            while True:
                await self._monitor_immortals()
                await asyncio.sleep(10)

        except Exception as e:
            self.logger.error(f"Launch failed: {str(e)}")
            raise

    async def _monitor_immortals(self):
        """Monitor immortal agents"""
        try:
            # Get wallet balance
            balance = await self.client.get_balance(self.keypair.pubkey())
            sol_balance = balance.value / 1e9
            
            # Get agent stats
            agent_count = len(AGENT_SPAWNER.agents)
            active_trades = sum(
                len(agent.state.active_trades) 
                for agent in AGENT_SPAWNER.agents.values()
            )
            
            self.logger.info(
                f"💫 Immortal Brotherhood Status 💫\n"
                f"Active Immortals: {agent_count}\n"
                f"Active Trades: {active_trades}\n"
                f"SOL Balance: {sol_balance}\n"
                f"Glory to Christ Benzion! ✨"
            )

        except Exception as e:
            self.logger.error(f"Monitoring error: {str(e)}")

async def main():
    brotherhood = ImmortalBrotherhood()
    await brotherhood.launch_immortals()

if __name__ == "__main__":
    asyncio.run(main())
