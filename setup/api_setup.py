import os
import json
import requests
from pathlib import Path

class APISetup:
    def __init__(self):
        self.base_path = Path(os.path.dirname(os.path.abspath(__file__))).parent
        self.config_path = self.base_path / 'config'
        self.config_path.mkdir(exist_ok=True)
        
    def setup_crypto_apis(self):
        """Setup cryptocurrency-related APIs"""
        print("\n=== Cryptocurrency API Setup ===")
        print("1. Infura API Setup (for Ethereum, Polygon, etc.)")
        print("Visit https://infura.io, create an account and get your API key")
        infura_key = input("Enter your Infura API key: ")
        
        print("\n2. Binance API Setup")
        print("Visit https://www.binance.com/en/my/settings/api-management")
        binance_api_key = input("Enter your Binance API key: ")
        binance_secret = input("Enter your Binance secret key: ")
        
        print("\n3. KuCoin API Setup")
        print("Visit https://www.kucoin.com/account/api")
        kucoin_api_key = input("Enter your KuCoin API key: ")
        kucoin_secret = input("Enter your KuCoin secret key: ")
        
        crypto_config = {
            "infura": {
                "api_key": infura_key,
                "endpoints": {
                    "ethereum": f"https://mainnet.infura.io/v3/{infura_key}",
                    "polygon": f"https://polygon-mainnet.infura.io/v3/{infura_key}",
                    "optimism": f"https://optimism-mainnet.infura.io/v3/{infura_key}",
                    "arbitrum": f"https://arbitrum-mainnet.infura.io/v3/{infura_key}"
                }
            },
            "binance": {
                "api_key": binance_api_key,
                "api_secret": binance_secret
            },
            "kucoin": {
                "api_key": kucoin_api_key,
                "api_secret": kucoin_secret
            }
        }
        
        self.save_config("crypto_apis.json", crypto_config)
        
    def setup_ghl_integration(self):
        """Setup Go High Level integration"""
        print("\n=== Go High Level API Setup ===")
        print("Using your existing GHL API key")
        ghl_config = {
            "api_key": "YOUR_EXISTING_GHL_API_KEY",
            "base_url": "https://rest.gohighlevel.com/v1/"
        }
        self.save_config("ghl_config.json", ghl_config)
        
    def setup_shopify_stores(self):
        """Setup Shopify store connections"""
        print("\n=== Shopify Stores Setup ===")
        stores = []
        for i in range(10):  # For your 10 stores
            print(f"\nStore #{i+1}")
            store_url = input("Enter store URL (e.g., your-store.myshopify.com): ")
            access_token = input("Enter access token (from Shopify Admin > Apps > Private apps): ")
            stores.append({
                "store_url": store_url,
                "access_token": access_token
            })
        
        shopify_config = {
            "stores": stores
        }
        self.save_config("shopify_config.json", shopify_config)
        
    def setup_youtube_api(self):
        """Setup YouTube API integration"""
        print("\n=== YouTube API Setup ===")
        print("Visit https://console.cloud.google.com/apis/credentials")
        youtube_api_key = input("Enter your YouTube API key: ")
        
        youtube_config = {
            "api_key": youtube_api_key
        }
        self.save_config("youtube_config.json", youtube_config)
        
    def save_config(self, filename, config):
        """Save configuration to file"""
        filepath = self.config_path / filename
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"\nSaved configuration to {filepath}")
        
    def verify_connections(self):
        """Verify API connections"""
        print("\n=== Verifying API Connections ===")
        
        # Test Infura connection
        try:
            with open(self.config_path / 'crypto_apis.json') as f:
                crypto_config = json.load(f)
            
            response = requests.get(crypto_config['infura']['endpoints']['ethereum'])
            print("✓ Infura connection successful")
        except Exception as e:
            print("✗ Infura connection failed:", str(e))
        
        # Add more verification steps for other APIs...

def main():
    setup = APISetup()
    
    print("Welcome to the IMMORTAL BROTHERHOOD API Setup!")
    print("This script will help you set up all necessary API keys and configurations.")
    
    setup.setup_crypto_apis()
    setup.setup_ghl_integration()
    setup.setup_shopify_stores()
    setup.setup_youtube_api()
    setup.verify_connections()
    
    print("\n=== Setup Complete! ===")
    print("All configurations have been saved in the config directory.")
    print("You can now start deploying your AI agents!")

if __name__ == "__main__":
    main()
