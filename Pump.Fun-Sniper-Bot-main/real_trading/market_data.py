import aiohttp
import asyncio
from typing import Dict, List, Optional
import json
import websockets
import logging

class MarketDataFeed:
    def __init__(self):
        self.logger = logging.getLogger("MarketData")
        self.price_feeds = {
            "birdeye": "https://public-api.birdeye.so",
            "coingecko": "https://api.coingecko.com/api/v3",
            "dexscreener": "https://api.dexscreener.com/latest"
        }
        self.websocket_feeds = {
            "raydium": "wss://api.raydium.io/v2/ws",
            "orca": "wss://api.orca.so/v1/ws",
            "jupiter": "wss://price.jup.ag/v4/ws"
        }
        
    async def initialize(self):
        """Initialize all market data connections"""
        try:
            self.logger.info("Initializing market data feeds...")
            # Initialize price feeds
            async with aiohttp.ClientSession() as session:
                for name, url in self.price_feeds.items():
                    try:
                        async with session.get(url) as response:
                            if response.status == 200:
                                self.logger.info(f"{name} price feed connected")
                            else:
                                self.logger.warning(f"{name} price feed connection failed")
                    except Exception as e:
                        self.logger.error(f"{name} price feed error: {str(e)}")
                        
        except Exception as e:
            raise Exception(f"Market data initialization failed: {str(e)}")
            
    async def get_token_price(self, token_address: str) -> Dict:
        """Get real-time token price from multiple sources"""
        try:
            prices = await asyncio.gather(
                self._get_birdeye_price(token_address),
                self._get_dexscreener_price(token_address)
            )
            return self._aggregate_prices(prices)
        except Exception as e:
            raise Exception(f"Failed to get token price: {str(e)}")
            
    async def get_market_data(self, token_address: str) -> Dict:
        """Get comprehensive market data"""
        try:
            data = await asyncio.gather(
                self.get_token_price(token_address),
                self._get_volume_data(token_address),
                self._get_liquidity_data(token_address)
            )
            return self._combine_market_data(data)
        except Exception as e:
            raise Exception(f"Failed to get market data: {str(e)}")
            
    async def monitor_price_changes(self, token_address: str, callback):
        """Monitor real-time price changes"""
        try:
            async with websockets.connect(self.websocket_feeds["jupiter"]) as ws:
                subscribe_msg = {
                    "type": "subscribe",
                    "tokens": [token_address]
                }
                await ws.send(json.dumps(subscribe_msg))
                
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    await callback(data)
                    
        except Exception as e:
            raise Exception(f"Price monitoring failed: {str(e)}")
            
    async def _get_birdeye_price(self, token_address: str) -> float:
        """Get price from Birdeye"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.price_feeds['birdeye']}/public/price?address={token_address}"
                async with session.get(url) as response:
                    data = await response.json()
                    return float(data["data"]["value"])
        except Exception as e:
            self.logger.error(f"Birdeye price fetch failed: {str(e)}")
            return None
            
    async def _get_dexscreener_price(self, token_address: str) -> float:
        """Get price from DexScreener"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.price_feeds['dexscreener']}/dex/tokens/{token_address}"
                async with session.get(url) as response:
                    data = await response.json()
                    return float(data["pairs"][0]["priceUsd"])
        except Exception as e:
            self.logger.error(f"DexScreener price fetch failed: {str(e)}")
            return None
            
    def _aggregate_prices(self, prices: List[Optional[float]]) -> float:
        """Aggregate prices from multiple sources"""
        valid_prices = [p for p in prices if p is not None]
        if not valid_prices:
            raise Exception("No valid prices available")
        return sum(valid_prices) / len(valid_prices)
            
    async def _get_volume_data(self, token_address: str) -> Dict:
        """Get trading volume data"""
        try:
            # Implement volume data fetching
            pass
        except Exception as e:
            raise Exception(f"Volume data fetch failed: {str(e)}")
            
    async def _get_liquidity_data(self, token_address: str) -> Dict:
        """Get liquidity data"""
        try:
            # Implement liquidity data fetching
            pass
        except Exception as e:
            raise Exception(f"Liquidity data fetch failed: {str(e)}")
            
    def _combine_market_data(self, data: List[Dict]) -> Dict:
        """Combine all market data into one structure"""
        try:
            return {
                "price": data[0],
                "volume": data[1],
                "liquidity": data[2]
            }
        except Exception as e:
            raise Exception(f"Data combination failed: {str(e)}")
