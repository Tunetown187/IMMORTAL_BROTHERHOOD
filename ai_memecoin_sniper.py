from web3 import Web3
import json
import asyncio
from eth_account import Account
import os
from dotenv import load_dotenv
import tweepy
import requests
from transformers import pipeline
import pandas as pd
from wallet_manager import WalletManager

class AIMemeSniper:
    def __init__(self):
        load_dotenv()
        self.w3 = Web3(Web3.HTTPProvider(os.getenv('ETH_RPC_URL')))
        self.wallet_manager = WalletManager()
        self.private_key = os.getenv('PRIVATE_KEY')
        self.account = Account.from_key(self.private_key)
        self.twitter_client = self.setup_twitter()
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        
        # Router and factory addresses
        self.uniswap_factory = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
        self.uniswap_router = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
        
        # Load ABIs
        with open('abis/factory.json', 'r') as f:
            self.factory_abi = json.load(f)
        with open('abis/router.json', 'r') as f:
            self.router_abi = json.load(f)
        with open('abis/token.json', 'r') as f:
            self.token_abi = json.load(f)

    def setup_twitter(self):
        auth = tweepy.OAuthHandler(
            os.getenv('TWITTER_API_KEY'),
            os.getenv('TWITTER_API_SECRET')
        )
        auth.set_access_token(
            os.getenv('TWITTER_ACCESS_TOKEN'),
            os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        )
        return tweepy.API(auth)

    async def monitor_memecoin_launches(self):
        """Monitor new token launches and AI-related social media activity"""
        factory_contract = self.w3.eth.contract(
            address=self.uniswap_factory,
            abi=self.factory_abi
        )
        
        # Subscribe to PairCreated events
        event_filter = factory_contract.events.PairCreated.create_filter(fromBlock='latest')
        
        while True:
            try:
                events = event_filter.get_new_entries()
                for event in events:
                    token_address = event['args']['token1']
                    if await self.analyze_token(token_address):
                        await self.snipe_token(token_address)
            except Exception as e:
                print(f"Error monitoring launches: {e}")
            await asyncio.sleep(1)

    async def analyze_token(self, token_address):
        """Analyze if token is AI-related and has potential"""
        try:
            # Get token info
            token_contract = self.w3.eth.contract(
                address=token_address,
                abi=self.token_abi
            )
            name = token_contract.functions.name().call()
            symbol = token_contract.functions.symbol().call()
            
            # Check if AI-related
            ai_keywords = ['AI', 'GPT', 'AGI', 'Intelligence', 'Neural', 'Brain']
            if not any(keyword.lower() in name.lower() or keyword.lower() in symbol.lower() 
                      for keyword in ai_keywords):
                return False

            # Analyze social sentiment
            tweets = self.twitter_client.search_tweets(
                q=f"#{symbol} OR {name} crypto",
                lang="en",
                count=100
            )
            
            sentiments = []
            for tweet in tweets:
                result = self.sentiment_analyzer(tweet.text)[0]
                sentiments.append(1 if result['label'] == 'POSITIVE' else -1)
            
            sentiment_score = sum(sentiments) / len(sentiments) if sentiments else 0
            
            # Check liquidity and holder metrics
            liquidity = await self.check_liquidity(token_address)
            holders = await self.get_holder_count(token_address)
            
            # Score the token
            score = self.calculate_token_score(
                sentiment_score,
                liquidity,
                holders,
                name,
                symbol
            )
            
            return score > 0.7  # Threshold for sniping
            
        except Exception as e:
            print(f"Error analyzing token: {e}")
            return False

    async def check_liquidity(self, token_address):
        """Check token liquidity"""
        router_contract = self.w3.eth.contract(
            address=self.uniswap_router,
            abi=self.router_abi
        )
        
        try:
            # Get WETH pair liquidity
            weth = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
            reserves = router_contract.functions.getReserves(
                weth,
                token_address
            ).call()
            
            return float(reserves[1]) / 10**18
        except:
            return 0

    async def get_holder_count(self, token_address):
        """Get number of token holders"""
        try:
            # Use Etherscan API
            response = requests.get(
                f"https://api.etherscan.io/api",
                params={
                    "module": "token",
                    "action": "tokenholderlist",
                    "contractaddress": token_address,
                    "apikey": os.getenv('ETHERSCAN_API_KEY')
                }
            )
            data = response.json()
            return len(data['result'])
        except:
            return 0

    def calculate_token_score(self, sentiment, liquidity, holders, name, symbol):
        """Calculate overall token score"""
        # Weights for different metrics
        SENTIMENT_WEIGHT = 0.3
        LIQUIDITY_WEIGHT = 0.3
        HOLDERS_WEIGHT = 0.2
        AI_RELEVANCE_WEIGHT = 0.2
        
        # Calculate AI relevance score
        ai_terms = ['ai', 'gpt', 'intelligence', 'neural', 'brain', 'agent']
        ai_score = sum(term in name.lower() or term in symbol.lower() 
                      for term in ai_terms) / len(ai_terms)
        
        # Normalize liquidity (0-1 scale)
        liquidity_score = min(liquidity / 100, 1)  # Cap at 100 ETH
        
        # Normalize holders (0-1 scale)
        holders_score = min(holders / 1000, 1)  # Cap at 1000 holders
        
        # Calculate final score
        final_score = (
            sentiment * SENTIMENT_WEIGHT +
            liquidity_score * LIQUIDITY_WEIGHT +
            holders_score * HOLDERS_WEIGHT +
            ai_score * AI_RELEVANCE_WEIGHT
        )
        
        return final_score

    async def snipe_token(self, token_address):
        """Execute token purchase"""
        try:
            router_contract = self.w3.eth.contract(
                address=self.uniswap_router,
                abi=self.router_abi
            )
            
            # Amount of ETH to spend
            amount_in = self.w3.to_wei(0.1, 'ether')  # 0.1 ETH
            
            # Get token output amount
            weth = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
            amounts_out = router_contract.functions.getAmountsOut(
                amount_in,
                [weth, token_address]
            ).call()
            
            # Set minimum amount out (5% slippage)
            min_amount_out = int(amounts_out[1] * 0.95)
            
            # Prepare transaction
            deadline = int(time.time()) + 300  # 5 minutes
            
            # Build transaction
            tx = router_contract.functions.swapExactETHForTokens(
                min_amount_out,
                [weth, token_address],
                self.account.address,
                deadline
            ).build_transaction({
                'from': self.account.address,
                'value': amount_in,
                'gas': 250000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            print(f"Successfully sniped token: {token_address}")
            print(f"Transaction hash: {receipt['transactionHash'].hex()}")
            
            # Monitor price for take-profit/stop-loss
            asyncio.create_task(self.monitor_position(token_address))
            
        except Exception as e:
            print(f"Error sniping token: {e}")

    async def monitor_position(self, token_address):
        """Monitor token position for take-profit/stop-loss"""
        entry_price = await self.get_token_price(token_address)
        
        while True:
            try:
                current_price = await self.get_token_price(token_address)
                price_change = (current_price - entry_price) / entry_price
                
                # Take profit at 100% gain
                if price_change >= 1.0:
                    await self.sell_token(token_address, 1.0)  # Sell 100%
                    break
                    
                # Stop loss at 20% loss
                elif price_change <= -0.2:
                    await self.sell_token(token_address, 1.0)  # Sell 100%
                    break
                    
            except Exception as e:
                print(f"Error monitoring position: {e}")
                
            await asyncio.sleep(10)  # Check every 10 seconds

    async def get_token_price(self, token_address):
        """Get current token price in ETH"""
        router_contract = self.w3.eth.contract(
            address=self.uniswap_router,
            abi=self.router_abi
        )
        
        try:
            # Get price for 1 token
            weth = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
            amount_in = 10**18  # 1 token
            amounts = router_contract.functions.getAmountsOut(
                amount_in,
                [token_address, weth]
            ).call()
            
            return amounts[1] / 10**18
        except:
            return 0

    async def sell_token(self, token_address, percentage):
        """Sell token position"""
        try:
            token_contract = self.w3.eth.contract(
                address=token_address,
                abi=self.token_abi
            )
            
            # Get token balance
            balance = token_contract.functions.balanceOf(self.account.address).call()
            amount_to_sell = int(balance * percentage)
            
            router_contract = self.w3.eth.contract(
                address=self.uniswap_router,
                abi=self.router_abi
            )
            
            # Get minimum ETH out
            weth = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
            amounts_out = router_contract.functions.getAmountsOut(
                amount_to_sell,
                [token_address, weth]
            ).call()
            
            min_eth_out = int(amounts_out[1] * 0.95)  # 5% slippage
            
            # Approve router
            approve_tx = token_contract.functions.approve(
                self.uniswap_router,
                amount_to_sell
            ).build_transaction({
                'from': self.account.address,
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            signed_approve = self.w3.eth.account.sign_transaction(
                approve_tx,
                self.private_key
            )
            self.w3.eth.send_raw_transaction(signed_approve.rawTransaction)
            
            # Sell tokens
            deadline = int(time.time()) + 300
            
            sell_tx = router_contract.functions.swapExactTokensForETH(
                amount_to_sell,
                min_eth_out,
                [token_address, weth],
                self.account.address,
                deadline
            ).build_transaction({
                'from': self.account.address,
                'gas': 250000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address)
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(sell_tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"Successfully sold token: {token_address}")
            print(f"Transaction hash: {receipt['transactionHash'].hex()}")
            
        except Exception as e:
            print(f"Error selling token: {e}")

async def main():
    sniper = AIMemeSniper()
    await sniper.monitor_memecoin_launches()

if __name__ == "__main__":
    asyncio.run(main())
