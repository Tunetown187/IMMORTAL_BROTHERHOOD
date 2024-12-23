from eth_account import Account
import json
import os
from web3 import Web3

def create_initial_wallet():
    # Create new account
    account = Account.create()
    
    # Save wallet info
    wallet_data = {
        'address': account.address,
        'private_key': account.key.hex()
    }
    
    # Save to file
    with open('data/initial_wallet.json', 'w') as f:
        json.dump(wallet_data, f)
        
    print(f"\nInitial Funding Wallet Created:")
    print(f"Address: {account.address}")
    print("\nIMPORTANT: Send initial funds to this address to start trading!")
    print("Required funds:")
    print("- ETH: 0.5 ETH")
    print("- BNB: 2 BNB")
    
if __name__ == "__main__":
    if not os.path.exists('data'):
        os.makedirs('data')
    create_initial_wallet()
