import requests
import time
import argparse
import sys
import threading
import json
import base58
from datetime import datetime
from solders.transaction import VersionedTransaction
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.commitment_config import CommitmentLevel
from solders.message import MessageV0
from solders.hash import Hash
from solders.system_program import transfer, TransferParams
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from solders.instruction import Instruction
from solders.rpc.config import RpcSendTransactionConfig
from solders.rpc.requests import SendVersionedTransaction
import logging
import concurrent.futures
from typing import Dict, List, Optional
import websockets
import asyncio
import aiohttp

# Enhanced configuration
class Config:
    DOMAIN = "frontend-api.pump.fun"
    RPC_ENDPOINT = "https://api.mainnet-beta.solana.com"
    WEBSOCKET_ENDPOINT = "wss://api.mainnet-beta.solana.com"
    LIST_URL = f"https://{DOMAIN}/coins/for-you?offset=0&limit=50&includeNsfw=false"
    MONITOR_URL = f"https://{DOMAIN}/coins/"
    TRADE_URL = "https://pumpportal.fun/api/trade-local"
    
    # Trading parameters
    MIN_MARKET_CAP = 20000
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    WEBSOCKET_TIMEOUT = 60
    MAX_CONCURRENT_TRADES = 5

    # Color codes for terminal output
    COLORS = {
        'RESET': "\033[0m",
        'GREEN': "\033[92m",
        'RED': "\033[91m",
        'YELLOW': "\033[93m",
        'BLUE': "\033[94m",
        'PURPLE': "\033[95m"
    }

class EnhancedPumpBot:
    def __init__(self, private_key: str, config: dict):
        self.config = config
        self.keypair = Keypair.from_base58_string(private_key)
        self.public_key = str(self.keypair.pubkey())
        self.client = Client(Config.RPC_ENDPOINT)
        self.purchased_coins = {}
        self.stop_event = threading.Event()
        self.setup_logging()
        self.trade_lock = threading.Lock()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=Config.MAX_CONCURRENT_TRADES)
        self.websocket = None
        self.market_data = {}
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('pump_bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    async def setup_websocket(self):
        try:
            self.websocket = await websockets.connect(Config.WEBSOCKET_ENDPOINT)
            subscription = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "programSubscribe",
                "params": [
                    "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
                    {"encoding": "jsonParsed", "commitment": "confirmed"}
                ]
            }
            await self.websocket.send(json.dumps(subscription))
            self.logger.info("WebSocket connection established")
            return True
        except Exception as e:
            self.logger.error(f"WebSocket connection failed: {e}")
            return False

    async def monitor_market_events(self):
        while not self.stop_event.is_set():
            try:
                msg = await asyncio.wait_for(self.websocket.recv(), timeout=Config.WEBSOCKET_TIMEOUT)
                data = json.loads(msg)
                await self.process_market_event(data)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error in market monitoring: {e}")
                await asyncio.sleep(1)

    async def process_market_event(self, event_data):
        try:
            # Process different types of market events
            if 'method' in event_data and event_data['method'] == 'programNotification':
                await self.handle_token_event(event_data['params']['result'])
        except Exception as e:
            self.logger.error(f"Error processing market event: {e}")

    async def handle_token_event(self, event):
        # Implement token event handling logic
        pass

    def analyze_token(self, token_data: dict) -> float:
        """Advanced token analysis using multiple metrics"""
        score = 0.0
        
        # Market cap analysis
        market_cap = token_data.get('usd_market_cap', 0)
        if market_cap > self.config['min_market_cap']:
            score += 1.0

        # Social metrics
        if token_data.get('telegram'):
            score += 0.5
        if token_data.get('twitter'):
            score += 0.5
        if token_data.get('website'):
            score += 0.5

        # Trading volume analysis
        volume = token_data.get('volume_24h', 0)
        if volume > 0:
            score += 1.0

        # Holder analysis
        holders = token_data.get('holders', 0)
        if holders > 100:
            score += 1.0

        return score

    async def execute_trade_strategy(self, token_data: dict):
        """Execute advanced trading strategy"""
        try:
            score = self.analyze_token(token_data)
            if score >= self.config['min_score']:
                await self.execute_buy_order(token_data)
                self.monitor_position(token_data['mint'])
        except Exception as e:
            self.logger.error(f"Trade strategy error: {e}")

    async def execute_buy_order(self, token_data: dict):
        """Execute buy order with advanced error handling and retries"""
        for attempt in range(Config.MAX_RETRIES):
            try:
                success = await self.place_buy_order(token_data)
                if success:
                    self.logger.info(f"Successfully bought {token_data['name']}")
                    return True
            except Exception as e:
                self.logger.error(f"Buy attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(Config.RETRY_DELAY)
        return False

    def monitor_position(self, token_mint: str):
        """Monitor and manage open positions"""
        def _monitor():
            while not self.stop_event.is_set():
                try:
                    current_price = self.get_token_price(token_mint)
                    if self.should_take_profit(token_mint, current_price):
                        self.execute_sell_order(token_mint)
                        break
                    elif self.should_stop_loss(token_mint, current_price):
                        self.execute_sell_order(token_mint)
                        break
                except Exception as e:
                    self.logger.error(f"Position monitoring error: {e}")
                time.sleep(1)

        threading.Thread(target=_monitor, daemon=True).start()

    def should_take_profit(self, token_mint: str, current_price: float) -> bool:
        """Implement take profit logic"""
        if token_mint in self.purchased_coins:
            entry_price = self.purchased_coins[token_mint]['entry_price']
            profit_percentage = ((current_price - entry_price) / entry_price) * 100
            return profit_percentage >= self.config['take_profit_percentage']
        return False

    def should_stop_loss(self, token_mint: str, current_price: float) -> bool:
        """Implement stop loss logic"""
        if token_mint in self.purchased_coins:
            entry_price = self.purchased_coins[token_mint]['entry_price']
            loss_percentage = ((entry_price - current_price) / entry_price) * 100
            return loss_percentage >= self.config['stop_loss_percentage']
        return False

    async def fetch_token_list(self) -> List[dict]:
        """Fetch and filter token list from the API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(Config.LIST_URL) as response:
                    if response.status == 200:
                        data = await response.json()
                        if isinstance(data, list):
                            return [token for token in data if self.is_valid_token(token)]
                    self.logger.error(f"API request failed: {response.status}")
                    return []
        except Exception as e:
            self.logger.error(f"Error fetching token list: {e}")
            return []

    def is_valid_token(self, token: dict) -> bool:
        """Validate token data"""
        required_fields = ['mint', 'name', 'usd_market_cap']
        return all(field in token for field in required_fields) and \
               token['usd_market_cap'] > self.config['min_market_cap']

    async def run(self):
        """Main bot execution loop"""
        try:
            if not await self.setup_websocket():
                return

            monitor_task = asyncio.create_task(self.monitor_market_events())
            
            while not self.stop_event.is_set():
                tokens = await self.fetch_token_list()
                for token in tokens:
                    if self.stop_event.is_set():
                        break
                    await self.execute_trade_strategy(token)
                await asyncio.sleep(self.config['scan_interval'])

        except Exception as e:
            self.logger.error(f"Bot execution error: {e}")
        finally:
            self.stop_event.set()
            if self.websocket:
                await self.websocket.close()
            self.executor.shutdown(wait=True)

def main():
    parser = argparse.ArgumentParser(description="Enhanced Pump.Fun Trading Bot")
    parser.add_argument("--private-key", type=str, required=True, help="Private key for transactions")
    parser.add_argument("--min-market-cap", type=float, default=20000, help="Minimum market cap for tokens")
    parser.add_argument("--take-profit", type=float, default=50, help="Take profit percentage")
    parser.add_argument("--stop-loss", type=float, default=10, help="Stop loss percentage")
    parser.add_argument("--scan-interval", type=int, default=5, help="Interval between market scans")
    parser.add_argument("--min-score", type=float, default=3.0, help="Minimum score for token analysis")
    args = parser.parse_args()

    config = {
        'min_market_cap': args.min_market_cap,
        'take_profit_percentage': args.take_profit,
        'stop_loss_percentage': args.stop_loss,
        'scan_interval': args.scan_interval,
        'min_score': args.min_score
    }

    bot = EnhancedPumpBot(args.private_key, config)
    
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\nShutting down bot...")
        bot.stop_event.set()

if __name__ == "__main__":
    main()
