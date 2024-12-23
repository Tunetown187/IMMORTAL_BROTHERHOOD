from eth_account import Account
from web3 import Web3
import os
import json
from cryptography.fernet import Fernet
import asyncio
from typing import List, Dict
import time

class WalletManager:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(os.getenv('ETH_RPC_URL')))
        self.ledger_address = "0xA9500Cf2854Ae4A9eaC54d533426C935A534fB8c"  # Final profit destination
        self.hot_wallets: Dict[str, Account] = {}
        self.profit_threshold = self.w3.to_wei(5, 'ether')  # Transfer to Ledger at 5 ETH
        self.setup_encryption()
        
    def setup_encryption(self):
        """Setup encryption for hot wallet keys"""
        if not os.path.exists('data/key.key'):
            self.key = Fernet.generate_key()
            with open('data/key.key', 'wb') as key_file:
                key_file.write(self.key)
        else:
            with open('data/key.key', 'rb') as key_file:
                self.key = key_file.read()
        self.cipher = Fernet(self.key)

    def create_hot_wallet(self) -> Account:
        """Create new hot wallet for trading"""
        acct = Account.create()
        encrypted_key = self.cipher.encrypt(acct.key.hex().encode())
        
        wallet_data = {
            'address': acct.address,
            'encrypted_key': encrypted_key.decode()
        }
        
        # Store encrypted wallet data
        with open(f'data/wallet_{acct.address}.json', 'w') as f:
            json.dump(wallet_data, f)
            
        self.hot_wallets[acct.address] = acct
        return acct

    def get_hot_wallets(self, num_wallets: int = 5) -> List[Account]:
        """Get or create hot wallets"""
        while len(self.hot_wallets) < num_wallets:
            self.create_hot_wallet()
        return list(self.hot_wallets.values())

    async def check_and_transfer_profits(self):
        """Check balances and transfer profits to Ledger"""
        while True:
            try:
                for wallet in self.hot_wallets.values():
                    balance = self.w3.eth.get_balance(wallet.address)
                    
                    if balance > self.profit_threshold:
                        # Calculate gas cost
                        gas_price = self.w3.eth.gas_price
                        gas_limit = 21000  # Standard ETH transfer
                        gas_cost = gas_price * gas_limit
                        
                        # Calculate amount to transfer (balance - gas cost)
                        transfer_amount = balance - gas_cost
                        
                        if transfer_amount > 0:
                            # Create transaction
                            transaction = {
                                'nonce': self.w3.eth.get_transaction_count(wallet.address),
                                'gasPrice': gas_price,
                                'gas': gas_limit,
                                'to': self.ledger_address,
                                'value': transfer_amount,
                                'data': b'',
                                'chainId': 1  # Mainnet
                            }
                            
                            # Sign and send transaction
                            signed_txn = self.w3.eth.account.sign_transaction(
                                transaction, 
                                self.cipher.decrypt(
                                    self.hot_wallets[wallet.address].encrypted_key.encode()
                                ).decode()
                            )
                            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                            
                            print(f"Transferred {self.w3.from_wei(transfer_amount, 'ether')} ETH to Ledger")
                            print(f"Transaction hash: {tx_hash.hex()}")
                            
            except Exception as e:
                print(f"Error in profit transfer: {e}")
                
            await asyncio.sleep(300)  # Check every 5 minutes

    async def monitor_wallet_health(self):
        """Monitor wallet health and create new ones if needed"""
        while True:
            try:
                wallets = self.get_hot_wallets()
                
                for wallet in wallets:
                    # Check if wallet has enough ETH for gas
                    balance = self.w3.eth.get_balance(wallet.address)
                    min_balance = self.w3.to_wei(0.1, 'ether')  # Minimum 0.1 ETH for gas
                    
                    if balance < min_balance:
                        # Create new wallet if this one is low on funds
                        new_wallet = self.create_hot_wallet()
                        print(f"Created new hot wallet: {new_wallet.address}")
                        
            except Exception as e:
                print(f"Error monitoring wallets: {e}")
                
            await asyncio.sleep(3600)  # Check every hour

    def get_best_wallet(self) -> Account:
        """Get the best wallet for trading"""
        best_wallet = None
        highest_balance = 0
        
        for wallet in self.hot_wallets.values():
            balance = self.w3.eth.get_balance(wallet.address)
            if balance > highest_balance:
                highest_balance = balance
                best_wallet = wallet
                
        return best_wallet or self.create_hot_wallet()

    async def distribute_funds(self):
        """Distribute funds among hot wallets"""
        while True:
            try:
                wallets = self.get_hot_wallets()
                balances = [self.w3.eth.get_balance(w.address) for w in wallets]
                total_balance = sum(balances)
                
                if total_balance > 0:
                    # Find wallets that need funds
                    avg_balance = total_balance / len(wallets)
                    for i, wallet in enumerate(wallets):
                        if balances[i] < avg_balance * 0.5:  # If wallet has less than 50% of average
                            # Find wallet with excess funds
                            for j, other_wallet in enumerate(wallets):
                                if balances[j] > avg_balance * 1.5:  # If wallet has more than 150% of average
                                    # Transfer funds to balance
                                    transfer_amount = int((balances[j] - avg_balance) * 0.5)
                                    if transfer_amount > 0:
                                        await self.transfer_between_hot_wallets(
                                            other_wallet,
                                            wallet.address,
                                            transfer_amount
                                        )
                                    break
                                    
            except Exception as e:
                print(f"Error distributing funds: {e}")
                
            await asyncio.sleep(3600)  # Redistribute every hour

    async def transfer_between_hot_wallets(self, from_wallet: Account, to_address: str, amount: int):
        """Transfer funds between hot wallets"""
        try:
            gas_price = self.w3.eth.gas_price
            gas_limit = 21000
            
            transaction = {
                'nonce': self.w3.eth.get_transaction_count(from_wallet.address),
                'gasPrice': gas_price,
                'gas': gas_limit,
                'to': to_address,
                'value': amount,
                'data': b'',
                'chainId': 1
            }
            
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction,
                self.cipher.decrypt(
                    self.hot_wallets[from_wallet.address].encrypted_key.encode()
                ).decode()
            )
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            print(f"Transferred {self.w3.from_wei(amount, 'ether')} ETH between hot wallets")
            print(f"Transaction hash: {tx_hash.hex()}")
            
        except Exception as e:
            print(f"Error transferring between wallets: {e}")

async def main():
    wallet_manager = WalletManager()
    
    # Start all monitoring tasks
    await asyncio.gather(
        wallet_manager.check_and_transfer_profits(),
        wallet_manager.monitor_wallet_health(),
        wallet_manager.distribute_funds()
    )

if __name__ == "__main__":
    asyncio.run(main())
