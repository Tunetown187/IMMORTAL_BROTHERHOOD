from ledgerblue.comm import getDongle
from ledgerblue.commException import CommException
from eth_account.messages import encode_defunct
from web3 import Web3
import struct
import time
import asyncio
from typing import Optional

class LedgerWallet:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(os.getenv('ETH_RPC_URL')))
        self.dongle = None
        self.connected = False
        self.path = "44'/60'/0'/0/0"  # Standard Ethereum path
        
    async def connect(self) -> bool:
        """Connect to Ledger device"""
        try:
            self.dongle = getDongle(True)
            self.connected = True
            print("Successfully connected to Ledger device")
            return True
        except CommException as e:
            print(f"Failed to connect to Ledger: {e}")
            return False

    async def get_address(self) -> Optional[str]:
        """Get Ethereum address from Ledger"""
        if not self.connected:
            await self.connect()

        try:
            # Convert path to bytes
            path_bytes = bytes.fromhex("058000002C8000003C800000000000000000000000")
            
            # Send get address command
            result = self.dongle.exchange(
                bytes.fromhex("e002000015") + path_bytes
            )
            
            # Extract address from response
            offset = 1 + result[0]
            address = result[offset + 1: offset + 1 + 40]
            return "0x" + address.decode()
            
        except CommException as e:
            print(f"Error getting address: {e}")
            return None

    async def sign_transaction(self, transaction_dict: dict) -> Optional[str]:
        """Sign Ethereum transaction using Ledger"""
        if not self.connected:
            await self.connect()

        try:
            # Prepare transaction
            raw_tx = self.w3.eth.account.sign_transaction(transaction_dict).rawTransaction
            
            # Convert path to bytes
            path_bytes = bytes.fromhex("058000002C8000003C800000000000000000000000")
            
            # Send transaction to Ledger
            result = self.dongle.exchange(
                bytes.fromhex("e004000000") + path_bytes + raw_tx
            )
            
            # Extract signature
            v = result[0]
            r = int.from_bytes(result[1:33], 'big')
            s = int.from_bytes(result[33:65], 'big')
            
            # Create signed transaction
            signed_tx = self.w3.eth.account.sign_transaction(
                transaction_dict,
                signature=self.w3.toHex(result)
            ).rawTransaction
            
            return signed_tx
            
        except CommException as e:
            print(f"Error signing transaction: {e}")
            return None

    async def check_balance(self) -> float:
        """Check ETH balance"""
        address = await self.get_address()
        if address:
            balance = self.w3.eth.get_balance(address)
            return self.w3.from_wei(balance, 'ether')
        return 0.0

    async def verify_ledger_presence(self) -> bool:
        """Verify Ledger is connected and unlocked"""
        try:
            if not self.connected:
                await self.connect()
            
            # Try to get address as verification
            address = await self.get_address()
            return address is not None
            
        except Exception:
            return False

    async def monitor_connection(self):
        """Continuously monitor Ledger connection"""
        while True:
            if not await self.verify_ledger_presence():
                print("Ledger disconnected! Waiting for reconnection...")
                self.connected = False
                while not await self.connect():
                    await asyncio.sleep(5)
                print("Ledger reconnected!")
            await asyncio.sleep(30)

    def format_transaction(self, to_address: str, value: int, data: bytes = b'') -> dict:
        """Format transaction for Ledger signing"""
        address = await self.get_address()
        return {
            'nonce': self.w3.eth.get_transaction_count(address),
            'gasPrice': self.w3.eth.gas_price,
            'gas': 21000,  # Basic ETH transfer
            'to': to_address,
            'value': value,
            'data': data,
            'chainId': 1  # Mainnet
        }

    async def execute_trade(self, contract_address: str, amount: int, is_buy: bool = True):
        """Execute a trade through DEX"""
        try:
            # Get router contract
            router_address = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"  # Uniswap V2
            router_contract = self.w3.eth.contract(
                address=router_address,
                abi=self.get_router_abi()
            )
            
            # Prepare transaction
            deadline = int(time.time()) + 300  # 5 minutes
            path = [
                "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
                contract_address
            ]
            if not is_buy:
                path.reverse()
            
            # Get method and parameters
            if is_buy:
                method = router_contract.functions.swapExactETHForTokens
                value = amount
            else:
                method = router_contract.functions.swapExactTokensForETH
                value = 0
            
            # Build transaction
            tx = method(
                0,  # amountOutMin (no slippage protection for example)
                path,
                await self.get_address(),
                deadline
            ).build_transaction({
                'value': value,
                'gas': 250000,
                'gasPrice': self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(await self.get_address())
            })
            
            # Sign and send transaction
            signed_tx = await self.sign_transaction(tx)
            if signed_tx:
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx)
                return tx_hash
            
            return None
            
        except Exception as e:
            print(f"Error executing trade: {e}")
            return None

    def get_router_abi(self):
        """Get Uniswap Router ABI"""
        return [
            # Simplified ABI for example
            {
                "inputs": [
                    {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                    {"internalType": "address[]", "name": "path", "type": "address[]"},
                    {"internalType": "address", "name": "to", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"}
                ],
                "name": "swapExactETHForTokens",
                "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
                "stateMutability": "payable",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                    {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
                    {"internalType": "address[]", "name": "path", "type": "address[]"},
                    {"internalType": "address", "name": "to", "type": "address"},
                    {"internalType": "uint256", "name": "deadline", "type": "uint256"}
                ],
                "name": "swapExactTokensForETH",
                "outputs": [{"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
