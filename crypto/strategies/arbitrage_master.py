import asyncio
from web3 import Web3
from typing import List, Dict
import logging
import json
from decimal import Decimal

class ArbitrageMaster:
    def __init__(self, web3_connections: Dict[str, Web3]):
        self.connections = web3_connections
        self.dex_registry = {
            'ethereum': {
                'uniswap_v2': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
                'sushiswap': '0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F',
                'curve': '0x7D86446dDb609eD0F5f8684AcF30380a356b2B4c'
            },
            'bsc': {
                'pancakeswap': '0x10ED43C718714eb63d5aA57B78B54704E256024E',
                'apeswap': '0xcF0feBd3f17CEf5b47b0cD257aCf6025c5BFf3b7'
            },
            'polygon': {
                'quickswap': '0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff',
                'sushiswap': '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506'
            }
        }
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            filename='arbitrage.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    async def scan_opportunities(self):
        """Scan for arbitrage opportunities across DEXes and chains"""
        opportunities = []
        
        # Intra-chain opportunities
        for chain in self.connections:
            dexes = self.dex_registry.get(chain, {})
            if len(dexes) >= 2:
                chain_opportunities = await self.scan_intra_chain(chain, dexes)
                opportunities.extend(chain_opportunities)
                
        # Cross-chain opportunities
        cross_chain_opportunities = await self.scan_cross_chain()
        opportunities.extend(cross_chain_opportunities)
        
        return opportunities
        
    async def scan_intra_chain(self, chain: str, dexes: Dict[str, str]) -> List[Dict]:
        """Scan for arbitrage opportunities within the same chain"""
        opportunities = []
        w3 = self.connections[chain]
        
        # Get common token pairs across DEXes
        token_pairs = await self.get_common_pairs(chain, dexes)
        
        for pair in token_pairs:
            prices = {}
            for dex_name, dex_address in dexes.items():
                try:
                    price = await self.get_token_price(chain, dex_name, dex_address, pair)
                    prices[dex_name] = price
                except Exception as e:
                    logging.error(f"Error getting price from {dex_name} on {chain}: {e}")
                    
            # Find arbitrage opportunities
            for buy_dex, buy_price in prices.items():
                for sell_dex, sell_price in prices.items():
                    if buy_dex != sell_dex:
                        profit = (sell_price - buy_price) / buy_price
                        if profit > 0.01:  # 1% minimum profit threshold
                            opportunities.append({
                                'type': 'intra_chain',
                                'chain': chain,
                                'buy_dex': buy_dex,
                                'sell_dex': sell_dex,
                                'token_pair': pair,
                                'profit_percentage': profit * 100,
                                'buy_price': buy_price,
                                'sell_price': sell_price
                            })
                            
        return opportunities
        
    async def scan_cross_chain(self) -> List[Dict]:
        """Scan for arbitrage opportunities across different chains"""
        opportunities = []
        
        # Get prices for major tokens across chains
        prices = {}
        for chain in self.connections:
            try:
                chain_prices = await self.get_chain_prices(chain)
                prices[chain] = chain_prices
            except Exception as e:
                logging.error(f"Error getting prices for {chain}: {e}")
                
        # Find cross-chain opportunities
        for token in ['USDT', 'USDC', 'ETH', 'BTC']:
            for chain1, prices1 in prices.items():
                for chain2, prices2 in prices.items():
                    if chain1 != chain2 and token in prices1 and token in prices2:
                        profit = (prices2[token] - prices1[token]) / prices1[token]
                        if profit > 0.02:  # 2% minimum profit threshold for cross-chain
                            opportunities.append({
                                'type': 'cross_chain',
                                'token': token,
                                'buy_chain': chain1,
                                'sell_chain': chain2,
                                'profit_percentage': profit * 100,
                                'buy_price': prices1[token],
                                'sell_price': prices2[token]
                            })
                            
        return opportunities
        
    async def execute_arbitrage(self, opportunity: Dict):
        """Execute arbitrage opportunity"""
        try:
            if opportunity['type'] == 'intra_chain':
                await self.execute_intra_chain_arbitrage(opportunity)
            else:
                await self.execute_cross_chain_arbitrage(opportunity)
        except Exception as e:
            logging.error(f"Error executing arbitrage: {e}")
            
    async def execute_intra_chain_arbitrage(self, opportunity: Dict):
        """Execute intra-chain arbitrage"""
        chain = opportunity['chain']
        w3 = self.connections[chain]
        
        try:
            # 1. Buy tokens on cheaper DEX
            buy_tx = await self.execute_swap(
                chain,
                opportunity['buy_dex'],
                opportunity['token_pair'][0],
                opportunity['token_pair'][1],
                opportunity['buy_price']
            )
            
            # 2. Sell tokens on more expensive DEX
            sell_tx = await self.execute_swap(
                chain,
                opportunity['sell_dex'],
                opportunity['token_pair'][1],
                opportunity['token_pair'][0],
                opportunity['sell_price']
            )
            
            logging.info(f"Successfully executed intra-chain arbitrage on {chain}")
            return True
            
        except Exception as e:
            logging.error(f"Intra-chain arbitrage failed: {e}")
            return False
            
    async def execute_cross_chain_arbitrage(self, opportunity: Dict):
        """Execute cross-chain arbitrage"""
        try:
            # 1. Buy tokens on source chain
            buy_tx = await self.execute_cross_chain_swap(
                opportunity['buy_chain'],
                opportunity['token'],
                'buy',
                opportunity['buy_price']
            )
            
            # 2. Bridge tokens to destination chain
            bridge_tx = await self.bridge_tokens(
                opportunity['buy_chain'],
                opportunity['sell_chain'],
                opportunity['token']
            )
            
            # 3. Sell tokens on destination chain
            sell_tx = await self.execute_cross_chain_swap(
                opportunity['sell_chain'],
                opportunity['token'],
                'sell',
                opportunity['sell_price']
            )
            
            logging.info(f"Successfully executed cross-chain arbitrage")
            return True
            
        except Exception as e:
            logging.error(f"Cross-chain arbitrage failed: {e}")
            return False
            
    async def run(self):
        """Main loop for arbitrage operations"""
        while True:
            try:
                opportunities = await self.scan_opportunities()
                for opportunity in opportunities:
                    if await self.validate_opportunity(opportunity):
                        await self.execute_arbitrage(opportunity)
            except Exception as e:
                logging.error(f"Error in main loop: {e}")
            await asyncio.sleep(1)  # Prevent CPU overload
