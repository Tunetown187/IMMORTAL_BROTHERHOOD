from typing import Dict, List
import asyncio
from datetime import datetime
from agency_swarm.agents import BaseAgent
from ..core.divine_master_bot import DivineMasterBot

class SolanaSniperAgent(BaseAgent):
    """Agent responsible for executing Solana sniper trades"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.divine_bot = DivineMasterBot()
        self.active = False
        self.last_scan = None
        self.scan_interval = 30  # seconds
        
    async def start(self):
        """Start the sniper agent"""
        self.active = True
        await self._run_scan_loop()
        
    async def stop(self):
        """Stop the sniper agent"""
        self.active = False
        
    async def _run_scan_loop(self):
        """Main scanning loop"""
        while self.active:
            try:
                # Scan market signals
                market_signals = await self.divine_bot._scan_market_signals()
                
                # Scan social signals
                social_signals = await self.divine_bot._gather_social_signals()
                
                # Scan arbitrage opportunities
                arb_routes = await self.divine_bot._scan_arbitrage_routes()
                
                # Process all signals
                await self._process_signals(market_signals, social_signals, arb_routes)
                
                # Calculate stats
                stats = self.divine_bot._calculate_divine_stats()
                self.logger.info(f"Divine Stats: {stats}")
                
                # Update last scan time
                self.last_scan = datetime.now()
                
            except Exception as e:
                self.logger.error(f"Error in scan loop: {str(e)}")
                
            # Wait for next scan
            await asyncio.sleep(self.scan_interval)
            
    async def _process_signals(self, market_signals: Dict, social_signals: Dict, arb_routes: List):
        """Process all gathered signals and execute trades"""
        try:
            # Combine signals
            combined_signals = self._combine_signals(market_signals, social_signals)
            
            # Filter high confidence signals
            actionable_signals = self._filter_signals(combined_signals)
            
            # Execute trades based on signals
            for signal in actionable_signals:
                await self._execute_trade(signal)
                
            # Process arbitrage opportunities
            for route in arb_routes:
                if route["profit"] > self.divine_bot.config["min_profit"]:
                    await self._execute_arbitrage(route)
                    
        except Exception as e:
            self.logger.error(f"Error processing signals: {str(e)}")
            
    def _combine_signals(self, market_signals: Dict, social_signals: Dict) -> List:
        """Combine market and social signals"""
        combined = []
        
        # Process market signals
        for token, data in market_signals.items():
            signal_strength = self._calculate_signal_strength(data)
            if signal_strength > 0:
                combined.append({
                    "token": token,
                    "type": "market",
                    "strength": signal_strength,
                    "data": data
                })
                
        # Process social signals
        for platform, signals in social_signals.items():
            for signal in signals:
                if signal["confidence"] > 0.5:  # Minimum confidence threshold
                    combined.append({
                        "type": "social",
                        "platform": platform,
                        "strength": signal["confidence"],
                        "data": signal
                    })
                    
        return combined
        
    def _calculate_signal_strength(self, data: Dict) -> float:
        """Calculate overall signal strength"""
        strength = 0.0
        
        # Price change weight
        if abs(data["price_change"]) > 5:  # 5% threshold
            strength += 0.3 * (data["price_change"] / 100)
            
        # Volume change weight
        if data["volume_change"] > 50:  # 50% volume increase threshold
            strength += 0.7 * (data["volume_change"] / 100)
            
        return min(1.0, max(0.0, strength))
        
    def _filter_signals(self, signals: List) -> List:
        """Filter signals based on confidence and strength"""
        return [
            signal for signal in signals
            if signal["strength"] > 0.7  # High confidence threshold
        ]
        
    async def _execute_trade(self, signal: Dict):
        """Execute a trade based on signal"""
        try:
            if signal["type"] == "market":
                # Execute market-based trade
                await self.divine_bot._execute_market_trade(signal["token"], signal["data"])
            elif signal["type"] == "social":
                # Execute social signal-based trade
                await self.divine_bot._execute_social_trade(signal["data"])
                
        except Exception as e:
            self.logger.error(f"Error executing trade: {str(e)}")
            
    async def _execute_arbitrage(self, route: Dict):
        """Execute arbitrage trade"""
        try:
            await self.divine_bot._execute_arbitrage_trade(
                route["pair"],
                route["dex1"],
                route["dex2"],
                route["profit"]
            )
        except Exception as e:
            self.logger.error(f"Error executing arbitrage: {str(e)}")
