from web3 import Web3
import json
import os
from eth_account import Account
import secrets

class BlockchainManager:
    def __init__(self):
        # Initialize connections to different chains
        self.connections = {
            'ethereum': Web3(Web3.HTTPProvider('https://ethereum.publicnode.com')),
            'bsc': Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org')),
            'polygon': Web3(Web3.HTTPProvider('https://polygon-rpc.com')),
            'arbitrum': Web3(Web3.HTTPProvider('https://arb1.arbitrum.io/rpc')),
        }
        
        # Test connections
        self.test_connections()
        
    def test_connections(self):
        """Test connections to all chains"""
        print("=== Testing Blockchain Connections ===")
        for chain, w3 in self.connections.items():
            connected = w3.is_connected()
            print(f"{chain.capitalize()}: {'Connected' if connected else 'Not Connected'}")
            if connected:
                print(f"- Current Block: {w3.eth.block_number}")
                print(f"- Gas Price: {w3.eth.gas_price / 1e9:.2f} Gwei")
                print()

    def create_wallet(self):
        """Create a new wallet"""
        # Generate a random private key
        private_key = "0x" + secrets.token_hex(32)
        account = Account.from_key(private_key)
        return {
            'address': account.address,
            'private_key': private_key
        }

    def get_balance(self, chain, address):
        """Get balance for an address on specified chain"""
        if chain in self.connections:
            w3 = self.connections[chain]
            balance_wei = w3.eth.get_balance(address)
            balance_eth = w3.from_wei(balance_wei, 'ether')
            return balance_eth
        return None

def main():
    manager = BlockchainManager()
    
    # Create a new wallet
    wallet = manager.create_wallet()
    print("\n=== New Wallet Created ===")
    print(f"Address: {wallet['address']}")
    print(f"Private Key: {wallet['private_key']}")
    
    # Check balance across chains
    print("\n=== Checking Balances ===")
    for chain in manager.connections.keys():
        balance = manager.get_balance(chain, wallet['address'])
        print(f"{chain.capitalize()}: {balance if balance is not None else 'Error'} ETH")

if __name__ == "__main__":
    main()
