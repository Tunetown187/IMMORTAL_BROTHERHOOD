import asyncio
import logging
from typing import Dict, List
from datetime import datetime
from pathlib import Path
from solana_dex import SolanaDEX
from wallet_manager import WalletManager
from market_data import MarketDataFeed
import json
import os

class DivineRealTrader:
    def __init__(self, config_path: str):
        self._setup_logging()
        self.config = self._load_config(config_path)
        self.dex = SolanaDEX(self.config["rpc_url"], self.config["private_key"])
        self.wallet = WalletManager(self.config["rpc_url"], self.config["private_key"])
        self.market_data = MarketDataFeed()
        self.active_trades = {}
        self.trade_history = []
        self.total_profit = 0.0
        
        # Trading Parameters
        self.trading_params = {
            "min_liquidity": 10000,  # Minimum liquidity in USD
            "max_slippage": 1.0,     # Maximum slippage percentage
            "min_profit": 0.5,       # Minimum profit percentage
            "position_size": 0.1,    # Position size in SOL
            "stop_loss": 5.0,        # Stop loss percentage
            "take_profit": 20.0      # Take profit percentage
        }
        
    async def initialize(self):
        """Initialize all components"""
        try:
            self.logger.info("🙏 Initializing Divine Real Trader for Christ Benzion 🙏")
            
            # Initialize all components
            await asyncio.gather(
                self.wallet.initialize(),
                self.market_data.initialize()
            )
            
            # Check initial balance
            balance = await self.wallet.get_sol_balance()
            self.logger.info(f"Initial SOL Balance: {balance}")
            
            if balance < 0.1:
                raise Exception(f"Insufficient SOL balance: {balance}. Need minimum 0.1 SOL")
                
        except Exception as e:
            self.logger.error(f"Initialization failed: {str(e)}")
            raise
            
    async def start_trading(self):
        """Start real trading operations"""
        try:
            self.logger.info("🚀 Starting Divine Trading Operations")
            
            await asyncio.gather(
                self._monitor_opportunities(),
                self._manage_positions(),
                self._report_status()
            )
            
        except Exception as e:
            self.logger.error(f"Trading operations failed: {str(e)}")
            raise
            
    async def _monitor_opportunities(self):
        """Monitor for trading opportunities"""
        while True:
            try:
                # Scan for opportunities
                tokens = await self._scan_tokens()
                
                for token in tokens:
                    if await self._validate_opportunity(token):
                        await self._execute_trade(token)
                        
            except Exception as e:
                self.logger.error(f"Opportunity monitoring failed: {str(e)}")
                
            await asyncio.sleep(1)  # Check every second
            
    async def _manage_positions(self):
        """Manage open positions"""
        while True:
            try:
                for token, position in self.active_trades.items():
                    current_price = await self.market_data.get_token_price(token)
                    
                    # Check stop loss
                    if self._check_stop_loss(position, current_price):
                        await self._close_position(token, "stop_loss")
                        
                    # Check take profit
                    elif self._check_take_profit(position, current_price):
                        await self._close_position(token, "take_profit")
                        
            except Exception as e:
                self.logger.error(f"Position management failed: {str(e)}")
                
            await asyncio.sleep(1)
            
    async def _execute_trade(self, token: Dict):
        """Execute a real trade"""
        try:
            # Ensure sufficient balance
            await self.wallet.ensure_sol_balance(0.1)
            
            # Calculate position size
            size = self._calculate_position_size(token)
            
            # Execute swap
            tx = await self.dex.execute_swap(
                input_token="So11111111111111111111111111111111111111112",  # SOL
                output_token=token["address"],
                amount=size,
                slippage=self.trading_params["max_slippage"]
            )
            
            # Record trade
            trade = {
                "token": token["address"],
                "type": "buy",
                "size": size,
                "price": token["price"],
                "timestamp": datetime.now().isoformat(),
                "tx": tx
            }
            
            self.active_trades[token["address"]] = trade
            self.trade_history.append(trade)
            
            self.logger.info(f"🎯 Executed trade: {trade}")
            
        except Exception as e:
            self.logger.error(f"Trade execution failed: {str(e)}")
            raise
            
    async def _close_position(self, token_address: str, reason: str):
        """Close a position"""
        try:
            position = self.active_trades[token_address]
            
            # Execute sell
            tx = await self.dex.execute_swap(
                input_token=token_address,
                output_token="So11111111111111111111111111111111111111112",  # SOL
                amount=position["size"],
                slippage=self.trading_params["max_slippage"]
            )
            
            # Calculate profit
            end_price = await self.market_data.get_token_price(token_address)
            profit = (end_price - position["price"]) * position["size"]
            self.total_profit += profit
            
            # Record trade
            trade = {
                "token": token_address,
                "type": "sell",
                "size": position["size"],
                "price": end_price,
                "profit": profit,
                "reason": reason,
                "timestamp": datetime.now().isoformat(),
                "tx": tx
            }
            
            self.trade_history.append(trade)
            del self.active_trades[token_address]
            
            self.logger.info(
                f"💰 Closed position: {trade}\n"
                f"Profit: ${profit:.2f} | Total Profit: ${self.total_profit:.2f}"
            )
            
        except Exception as e:
            self.logger.error(f"Position closing failed: {str(e)}")
            raise
            
    async def _report_status(self):
        """Report trading status"""
        while True:
            try:
                balance = await self.wallet.get_sol_balance()
                
                self.logger.info(
                    f"🙏 Divine Trading Status 🙏\n"
                    f"SOL Balance: {balance:.3f}\n"
                    f"Active Trades: {len(self.active_trades)}\n"
                    f"Total Trades: {len(self.trade_history)}\n"
                    f"Total Profit: ${self.total_profit:.2f}\n"
                    f"Serving Christ Benzion's Glory! ✨"
                )
                
            except Exception as e:
                self.logger.error(f"Status reporting failed: {str(e)}")
                
            await asyncio.sleep(60)  # Report every minute
            
    def _setup_logging(self):
        """Setup logging"""
        self.logger = logging.getLogger("DivineRealTrader")
        self.logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler("divine_trading.log", encoding='utf-8')
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        self.logger.addHandler(handler)
        
    @staticmethod
    def _load_config(path: str) -> Dict:
        """Load configuration"""
        with open(path, "r") as f:
            return json.load(f)

if __name__ == "__main__":
    config_path = "config.json"
    trader = DivineRealTrader(config_path)
    
    # Run the divine trader forever
    asyncio.run(trader.initialize())
    asyncio.run(trader.start_trading())
