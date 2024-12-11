import os
import requests
from dotenv import load_dotenv
from web3 import Web3

load_dotenv('../config/.env')

def test_metamask_connection():
    api_key = os.getenv('METAMASK_API_KEY')
    
    # Test basic ETH mainnet connection
    w3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{api_key}'))
    
    print("=== MetaMask API Connection Test ===")
    print(f"Connected to Ethereum: {w3.is_connected()}")
    if w3.is_connected():
        print(f"Current ETH Block: {w3.eth.block_number}")
        print(f"Gas Price: {w3.eth.gas_price / 1e9} Gwei")
        
        # Get ETH price
        try:
            eth_price_url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
            eth_price = requests.get(eth_price_url).json()['ethereum']['usd']
            print(f"Current ETH Price: ${eth_price:,.2f}")
        except Exception as e:
            print(f"Could not fetch ETH price: {e}")

if __name__ == "__main__":
    test_metamask_connection()
