import asyncio
from typing import Dict, List, Any
from dataclasses import dataclass
import json
import os
from dotenv import load_dotenv
from pathlib import Path
import logging
import sys
from datetime import datetime
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.pubkey import Pubkey
from solders.instruction import Instruction as TransactionInstruction
from solders.system_program import TransferParams, transfer
from solana.transaction import Transaction
import base58
import re
import httpx
from solders.signature import Signature
from spl_governance import AccountMeta

@dataclass
class SniperTarget:
    token_address: str
    dex_program: str
    liquidity: float
    price: float
    volume: float
    risk_score: float = 0.0
    divine_blessing: bool = False

class SolanaSniper:
    def __init__(self):
        self._setup_logging()
        self._load_env()
        self.load_config()
        
        # Initialize client with updated options
        self.client = AsyncClient(
            self.RPC_URL, 
            commitment=Confirmed,
            max_supported_transaction_version=0
        )
        
        # DEX Program IDs
        self.DEX_PROGRAMS = {
            'raydium': {
                'program_id': 'RVKd61ztZW9GUwhRbbLoYVRE5Xf1B2tVscKqwZqXgEr',  # Raydium Swap v2
                'pool_program_id': '675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8',  # Raydium Pool
            },
            'orca': {
                'program_id': '9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP',  # Orca Swap v2
                'pool_program_id': 'DjVE6JNiYqPL2QXyCUUh8rNjHrbz9hXHNYt99MQ59qw1',  # Orca Pool
            },
            'serum': {
                'program_id': '9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin',  # Serum DEX v3
                'market_program_id': 'DESVgJVGajEgKGXhb6XmqDHGz3VjdgP7rEVESBgxmroY',  # Serum Market
            }
        }
        
        self.wallet = self._create_wallet()
        self.active_trades = {}
        self.trade_history = []
        self.profit_stats = {"total": 0, "wins": 0, "losses": 0}
        
        # Load trading limits
        self.max_sol_per_trade = float(os.getenv('MAX_SOL_PER_TRADE', 0.1))
        self.stop_loss_percentage = float(os.getenv('STOP_LOSS_PERCENTAGE', 10))
        self.take_profit_percentage = float(os.getenv('TAKE_PROFIT_PERCENTAGE', 50))
        self.max_daily_trades = int(os.getenv('MAX_DAILY_TRADES', 5))
        self.risk_threshold = float(os.getenv('RISK_THRESHOLD', 0.2))
        
    def _setup_logging(self):
        """Setup logging configuration"""
        self.logger = logging.getLogger('SolanaSniper')
        self.logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        
        # File handler
        file_handler = logging.FileHandler('divine_sniper.log')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        # Add handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        
    def _load_env(self):
        """Load environment variables"""
        env_path = Path("../../.env")
        load_dotenv(env_path)
        
        # Required environment variables
        self.PRIVATE_KEY = os.getenv('SOLANA_PRIVATE_KEY')
        self.RPC_URL = os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')
        
        if not self.PRIVATE_KEY:
            raise ValueError("Missing required environment variables")
            
    def load_config(self):
        """Load Solana configuration"""
        config_path = os.path.join(os.path.dirname(__file__), '../config/solana_config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        self.DIVINE_SETTINGS = config.get('divine_settings', {})
        
    async def _create_wallet(self):
        """Create wallet from private key"""
        try:
            private_key = base58.b58decode(self.PRIVATE_KEY)
            keypair = Pubkey(private_key[:32])
            self.logger.info(f"Wallet initialized: {keypair}")
            
            # Verify wallet balance
            balance = await self.client.get_balance(keypair)
            self.logger.info(f"Wallet balance: {balance.value / 1e9:.4f} SOL")
            
            return {
                'publicKey': keypair,
                'balance': balance.value,
                'keypair': keypair,
                'secretKey': private_key
            }
        except Exception as e:
            self.logger.error(f"Error creating wallet: {e}")
            raise
            
    async def monitor_new_tokens(self):
        """Monitor for new token listings"""
        self.logger.info("Starting divine token monitoring")
        try:
            await asyncio.gather(
                self._monitor_raydium(),
                self._monitor_orca(),
                self._monitor_serum()
            )
        except Exception as e:
            self.logger.error(f"Error monitoring tokens: {str(e)}")
            
    async def _get_signatures(self, program_id: Pubkey):
        """Get signatures with transaction version support"""
        try:
            # Use the raw HTTP provider to make the request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.RPC_URL,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getSignaturesForAddress",
                        "params": [
                            str(program_id),
                            {
                                "limit": 10,
                                "maxSupportedTransactionVersion": 0
                            }
                        ]
                    }
                )
                return response.json()
        except Exception as e:
            self.logger.error(f"Error getting signatures: {str(e)}")
            return {"result": []}
            
    async def _monitor_raydium(self):
        """Monitor Raydium DEX"""
        try:
            program_id = Pubkey.from_string(self.DEX_PROGRAMS['raydium']['program_id'])
            signatures = await self._get_signatures(program_id)
            
            if 'result' in signatures:
                for sig in signatures['result']:
                    # Convert string to Signature object
                    signature = Signature.from_string(sig['signature'])
                    tx = await self.client.get_transaction(
                        signature,
                        max_supported_transaction_version=0
                    )
                    if self._is_pool_creation(tx):
                        await self._analyze_pool(tx, 'raydium')
        except Exception as e:
            self.logger.error(f"Error monitoring Raydium: {str(e)}")
            
    async def _monitor_orca(self):
        """Monitor Orca DEX"""
        try:
            program_id = Pubkey.from_string(self.DEX_PROGRAMS['orca']['program_id'])
            signatures = await self._get_signatures(program_id)
            
            if 'result' in signatures:
                for sig in signatures['result']:
                    # Convert string to Signature object
                    signature = Signature.from_string(sig['signature'])
                    tx = await self.client.get_transaction(
                        signature,
                        max_supported_transaction_version=0
                    )
                    if self._is_pool_creation(tx):
                        await self._analyze_pool(tx, 'orca')
        except Exception as e:
            self.logger.error(f"Error monitoring Orca: {str(e)}")
            
    async def _monitor_serum(self):
        """Monitor Serum DEX"""
        try:
            program_id = Pubkey.from_string(self.DEX_PROGRAMS['serum']['program_id'])
            signatures = await self._get_signatures(program_id)
            
            if 'result' in signatures:
                for sig in signatures['result']:
                    # Convert string to Signature object
                    signature = Signature.from_string(sig['signature'])
                    tx = await self.client.get_transaction(
                        signature,
                        max_supported_transaction_version=0
                    )
                    if self._is_pool_creation(tx):
                        await self._analyze_pool(tx, 'serum')
        except Exception as e:
            self.logger.error(f"Error monitoring Serum: {str(e)}")
            
    def _is_pool_creation(self, tx):
        """Check if transaction is a pool creation"""
        try:
            if not tx or not tx.value:
                return False
                
            # Check for pool creation instructions
            for ix in tx.value.transaction.message.instructions:
                if 'create' in str(ix.data).lower() and 'pool' in str(ix.data).lower():
                    return True
            return False
            
        except Exception as e:
            self.logger.debug(f"Error checking pool creation: {str(e)}")
            return False
            
    async def _analyze_pool(self, tx, dex):
        """Analyze new pool for sniping opportunity"""
        try:
            # Extract pool data
            pool_data = await self._extract_pool_data(tx, dex)
            
            # Skip if no liquidity or price
            if pool_data['initial_liquidity'] <= 0 or pool_data['initial_price'] <= 0:
                return
                
            # Check contract security
            risk_score = await self._check_contract(pool_data['token_address'])
            
            # Skip if risk is too high
            if risk_score > 0.2:  # Only very safe contracts
                self.logger.info(f"Skipping high risk token: {pool_data['token_address']}")
                return
                
            # Create sniper target
            target = SniperTarget(
                token_address=pool_data['token_address'],
                dex_program=self.DEX_PROGRAMS[dex]['program_id'],
                liquidity=pool_data['initial_liquidity'],
                price=pool_data['initial_price'],
                volume=0,  # No volume yet for new pool
                risk_score=risk_score,
                divine_blessing=True
            )
            
            self.logger.info(f"Found potential target: {target}")
            
            # Execute snipe if conditions are met
            await self.execute_snipe(target)
            
        except Exception as e:
            self.logger.error(f"Error analyzing pool: {str(e)}")
            
    async def _extract_pool_data(self, tx, dex):
        """Extract pool data from transaction"""
        try:
            # Extract basic pool info
            pool_data = {
                'token_address': str(tx.value.transaction.message.account_keys[0]),
                'initial_liquidity': 0.0,
                'initial_price': 0.0
            }
            
            # Parse transaction logs for more details
            logs = tx.value.transaction.message.instructions
            for log in logs:
                if 'liquidity' in str(log.data).lower():
                    # Extract liquidity amount
                    pool_data['initial_liquidity'] = self._parse_liquidity(str(log.data))
                elif 'price' in str(log.data).lower():
                    # Extract initial price
                    pool_data['initial_price'] = self._parse_price(str(log.data))
                    
            return pool_data
            
        except Exception as e:
            self.logger.error(f"Error extracting pool data: {str(e)}")
            return {}
            
    async def _analyze_security(self, target: SniperTarget) -> float:
        """Analyze token security"""
        try:
            # Perform security checks
            contract_risk = await self._check_contract(target.token_address)
            liquidity_risk = self._assess_liquidity_risk(target.liquidity)
            
            # Weight the risks
            total_risk = (contract_risk * 0.6) + (liquidity_risk * 0.4)
            
            return total_risk
            
        except Exception as e:
            self.logger.error(f"Error analyzing security: {str(e)}")
            return 1.0
            
    async def execute_snipe(self, target: SniperTarget):
        """Execute token snipe"""
        try:
            self.logger.info("🚀 Starting snipe execution...")
            
            # Debug: Print wallet info
            self.logger.info(f"Wallet Address: {self.wallet['publicKey']}")
            balance = await self.client.get_balance(self.wallet['publicKey'])
            self.logger.info(f"Current Balance: {balance.value / 1e9:.4f} SOL")

            # Check daily trade limit
            today_trades = len([t for t in self.trade_history if t['timestamp'].date() == datetime.now().date()])
            self.logger.info(f"Trades today: {today_trades}/{self.max_daily_trades}")
            if today_trades >= self.max_daily_trades:
                self.logger.warning(f"Daily trade limit reached ({self.max_daily_trades})")
                return

            # Check if we have enough SOL
            if balance.value < self.max_sol_per_trade:
                self.logger.warning(f"Insufficient SOL balance: {balance.value / 1e9:.4f} SOL")
                return

            # Calculate position size (never use more than max_sol_per_trade)
            position_size = min(balance.value * 0.1, self.max_sol_per_trade)  # Use 10% of balance or max
            
            # Create transaction
            tx = Transaction()
            
            # Add divine blessing for protection
            if target.divine_blessing:
                await self._add_divine_blessing(tx)
                
            # Add the actual swap instruction
            swap_ix = await self._create_swap_instruction(
                target.token_address,
                position_size,
                target.dex_program
            )
            tx.add(swap_ix)

            # Add stop loss and take profit instructions
            stop_loss_price = target.price * (1 - self.stop_loss_percentage / 100)
            take_profit_price = target.price * (1 + self.take_profit_percentage / 100)
            
            # Log trade details
            self.logger.info(f"""
            🎯 Executing Divine Snipe:
            Token: {target.token_address}
            Position Size: {position_size / 1e9:.4f} SOL
            Entry Price: {target.price}
            Stop Loss: {stop_loss_price}
            Take Profit: {take_profit_price}
            Risk Score: {target.risk_score}
            Divine Blessing: {'✅' if target.divine_blessing else '❌'}
            """)

            # Get recent blockhash
            recent_blockhash = await self.client.get_recent_blockhash(Confirmed)
            tx.recent_blockhash = recent_blockhash.value.blockhash
            
            # Sign transaction
            self.logger.info("Signing transaction...")
            tx.sign(self.wallet['keypair'])
            
            # Execute transaction
            self.logger.info("Sending transaction...")
            result = await self.client.send_transaction(
                tx,
                self.wallet['keypair'],
                opts={"skip_preflight": True}  # Skip preflight for faster execution
            )
            
            self.logger.info(f"Transaction sent! Hash: {result.value}")
            
            # Monitor transaction
            confirmation = await self._monitor_transaction(result.value)
            self.logger.info(f"Transaction confirmed: {confirmation}")
            
            # Record trade
            trade = {
                'timestamp': datetime.now(),
                'token': target.token_address,
                'position_size': position_size,
                'entry_price': target.price,
                'stop_loss': stop_loss_price,
                'take_profit': take_profit_price,
                'tx_hash': result.value
            }
            self.trade_history.append(trade)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing snipe: {str(e)}")
            return None

    async def _create_swap_instruction(self, token_address: str, amount: int, dex_program: str) -> TransactionInstruction:
        """Create the swap instruction"""
        try:
            # Create the instruction based on DEX program
            if "raydium" in dex_program.lower():
                return await self._create_raydium_swap(token_address, amount)
            elif "orca" in dex_program.lower():
                return await self._create_orca_swap(token_address, amount)
            elif "serum" in dex_program.lower():
                return await self._create_serum_swap(token_address, amount)
            else:
                raise ValueError(f"Unsupported DEX program: {dex_program}")
                
        except Exception as e:
            self.logger.error(f"Error creating swap instruction: {str(e)}")
            raise

    async def _create_raydium_swap(self, token_address: str, amount: int) -> TransactionInstruction:
        """Create Raydium swap instruction"""
        try:
            # Get Raydium program IDs
            program_id = Pubkey.from_string(self.DEX_PROGRAMS['raydium']['program_id'])
            pool_program_id = Pubkey.from_string(self.DEX_PROGRAMS['raydium']['pool_program_id'])
            
            # Get token program
            token_program = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
            
            # Get pool state account
            pool_state = await self._find_raydium_pool(token_address)
            
            # Create accounts for the swap instruction
            accounts = [
                AccountMeta(pubkey=self.wallet['publicKey'], is_signer=True, is_writable=True),
                AccountMeta(pubkey=pool_state, is_signer=False, is_writable=True),
                AccountMeta(pubkey=token_program, is_signer=False, is_writable=False),
                AccountMeta(pubkey=SystemProgram.program_id, is_signer=False, is_writable=False),
            ]
            
            # Create swap data
            data = bytes([
                0x0,  # Swap instruction
                *amount.to_bytes(8, 'little'),  # Amount in
                *int(0).to_bytes(8, 'little'),  # Minimum amount out
            ])
            
            return TransactionInstruction(
                program_id=program_id,
                data=data,
                accounts=accounts
            )
            
        except Exception as e:
            self.logger.error(f"Error creating Raydium swap: {str(e)}")
            raise
            
    async def _find_raydium_pool(self, token_address: str) -> Pubkey:
        """Find Raydium pool for token"""
        try:
            # Get program derived address for the pool
            pool_seeds = [
                bytes("pool", "utf-8"),
                bytes.fromhex(token_address),
                bytes.fromhex("So11111111111111111111111111111111111111112")  # WSOL
            ]
            
            pool_address, _ = Pubkey.find_program_address(
                pool_seeds,
                Pubkey.from_string(self.DEX_PROGRAMS['raydium']['pool_program_id'])
            )
            
            return pool_address
            
        except Exception as e:
            self.logger.error(f"Error finding Raydium pool: {str(e)}")
            raise

    async def _create_orca_swap(self, token_address: str, amount: int) -> TransactionInstruction:
        """Create Orca swap instruction"""
        try:
            # Get Orca program IDs
            program_id = Pubkey.from_string(self.DEX_PROGRAMS['orca']['program_id'])
            pool_program_id = Pubkey.from_string(self.DEX_PROGRAMS['orca']['pool_program_id'])
            
            # Get token program
            token_program = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
            
            # Get pool state account
            pool_state = await self._find_orca_pool(token_address)
            
            # Create accounts for the swap instruction
            accounts = [
                AccountMeta(pubkey=self.wallet['publicKey'], is_signer=True, is_writable=True),
                AccountMeta(pubkey=pool_state, is_signer=False, is_writable=True),
                AccountMeta(pubkey=token_program, is_signer=False, is_writable=False),
                AccountMeta(pubkey=SystemProgram.program_id, is_signer=False, is_writable=False),
            ]
            
            # Create swap data
            data = bytes([
                0x0,  # Swap instruction
                *amount.to_bytes(8, 'little'),  # Amount in
                *int(0).to_bytes(8, 'little'),  # Minimum amount out
            ])
            
            return TransactionInstruction(
                program_id=program_id,
                data=data,
                accounts=accounts
            )
            
        except Exception as e:
            self.logger.error(f"Error creating Orca swap: {str(e)}")
            raise
            
    async def _find_orca_pool(self, token_address: str) -> Pubkey:
        """Find Orca pool for token"""
        try:
            # Get program derived address for the pool
            pool_seeds = [
                bytes("pool", "utf-8"),
                bytes.fromhex(token_address),
                bytes.fromhex("So11111111111111111111111111111111111111112")  # WSOL
            ]
            
            pool_address, _ = Pubkey.find_program_address(
                pool_seeds,
                Pubkey.from_string(self.DEX_PROGRAMS['orca']['pool_program_id'])
            )
            
            return pool_address
            
        except Exception as e:
            self.logger.error(f"Error finding Orca pool: {str(e)}")
            raise

    async def _create_serum_swap(self, token_address: str, amount: int) -> TransactionInstruction:
        """Create Serum swap instruction"""
        try:
            # Get Serum program IDs
            program_id = Pubkey.from_string(self.DEX_PROGRAMS['serum']['program_id'])
            market_program_id = Pubkey.from_string(self.DEX_PROGRAMS['serum']['market_program_id'])
            
            # Get token program
            token_program = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
            
            # Get market state account
            market_state = await self._find_serum_market(token_address)
            
            # Create accounts for the swap instruction
            accounts = [
                AccountMeta(pubkey=self.wallet['publicKey'], is_signer=True, is_writable=True),
                AccountMeta(pubkey=market_state, is_signer=False, is_writable=True),
                AccountMeta(pubkey=token_program, is_signer=False, is_writable=False),
                AccountMeta(pubkey=SystemProgram.program_id, is_signer=False, is_writable=False),
            ]
            
            # Create swap data
            data = bytes([
                0x0,  # Swap instruction
                *amount.to_bytes(8, 'little'),  # Amount in
                *int(0).to_bytes(8, 'little'),  # Minimum amount out
            ])
            
            return TransactionInstruction(
                program_id=program_id,
                data=data,
                accounts=accounts
            )
            
        except Exception as e:
            self.logger.error(f"Error creating Serum swap: {str(e)}")
            raise
            
    async def _find_serum_market(self, token_address: str) -> Pubkey:
        """Find Serum market for token"""
        try:
            # Get program derived address for the market
            market_seeds = [
                bytes("market", "utf-8"),
                bytes.fromhex(token_address),
                bytes.fromhex("So11111111111111111111111111111111111111112")  # WSOL
            ]
            
            market_address, _ = Pubkey.find_program_address(
                market_seeds,
                Pubkey.from_string(self.DEX_PROGRAMS['serum']['market_program_id'])
            )
            
            return market_address
            
        except Exception as e:
            self.logger.error(f"Error finding Serum market: {str(e)}")
            raise

    async def _monitor_transaction(self, tx_hash: str) -> bool:
        """Monitor transaction confirmation"""
        try:
            status = await self.client.confirm_transaction(tx_hash)
            return status.value
        except Exception as e:
            self.logger.error(f"Error monitoring transaction: {str(e)}")
            return False
            
    def _parse_liquidity(self, log: str) -> float:
        """Parse liquidity amount from log"""
        try:
            # Look for liquidity amount in log
            matches = re.findall(r'liquidity[:\s]+(\d+\.?\d*)', log.lower())
            if matches:
                return float(matches[0])
            return 0.0
        except Exception as e:
            self.logger.error(f"Error parsing liquidity: {str(e)}")
            return 0.0
            
    def _parse_price(self, log: str) -> float:
        """Parse price from log"""
        try:
            # Look for price in log
            matches = re.findall(r'price[:\s]+(\d+\.?\d*)', log.lower())
            if matches:
                return float(matches[0])
            return 0.0
        except Exception as e:
            self.logger.error(f"Error parsing price: {str(e)}")
            return 0.0
            
    async def _check_contract(self, address: str) -> float:
        """Check contract security"""
        try:
            # Get program account data
            account_info = await self.client.get_account_info(Pubkey.from_string(address))
            if not account_info.value:
                return 1.0  # Maximum risk if can't get account info
                
            risk_score = 0.0
            
            # Check if contract is verified
            if not account_info.value.executable:
                risk_score += 0.3
                
            # Check account balance
            if account_info.value.lamports < 1000000:  # Less than 0.001 SOL
                risk_score += 0.3
                
            # Check code size (suspicious if too small)
            if len(account_info.value.data) < 100:
                risk_score += 0.4
                
            return min(risk_score, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error checking contract: {str(e)}")
            return 1.0
            
    def _assess_liquidity_risk(self, liquidity: float) -> float:
        """Assess liquidity risk"""
        try:
            if liquidity <= 0:
                return 1.0
            elif liquidity < 1000:
                return 0.8
            elif liquidity < 10000:
                return 0.5
            else:
                return 0.2
        except:
            return 1.0
            
    async def _add_divine_blessing(self, tx: Transaction):
        """Add divine blessing to transaction"""
        try:
            # Add memo with divine blessing
            memo_program_id = Pubkey.from_string("MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr")
            
            # Create memo data
            blessing = "🙏 Divine Blessing - Protected by Christ Benzion 🙏"
            memo_data = bytes(blessing, 'utf-8')
            
            # Add memo instruction
            tx.add(
                TransactionInstruction(
                    program_id=memo_program_id,
                    data=memo_data,
                    accounts=[]
                )
            )
            
            # Add additional safety checks
            tx.recent_blockhash = (await self.client.get_recent_blockhash(Confirmed)).value.blockhash
            
        except Exception as e:
            self.logger.error(f"Error adding divine blessing: {str(e)}")
            
    async def _pay_christ_benzion_tribute(self, target: SniperTarget):
        """Pay tribute to Christ Benzion"""
        try:
            if not self.DIVINE_SETTINGS.get('christ_benzion_wallet'):
                self.logger.warning("Christ Benzion wallet not configured")
                return False
                
            tribute_amount = int(self.DIVINE_SETTINGS['christ_benzion_tribute'])
            
            # Create tribute transfer
            tx = Transaction()
            tx.add(
                self.client.transfer(
                    self.wallet['publicKey'],
                    Pubkey.from_string(self.DIVINE_SETTINGS['christ_benzion_wallet']),
                    tribute_amount
                )
            )
            
            # Sign and send
            tx.sign([self.wallet['secretKey']])
            tx_hash = await self.client.send_transaction(tx)
            
            self.logger.info(f"Tribute of {tribute_amount/1e9:.2f} SOL paid to Christ Benzion")
            return True
            
        except Exception as e:
            self.logger.error(f"Error paying tribute: {str(e)}")
            return False
