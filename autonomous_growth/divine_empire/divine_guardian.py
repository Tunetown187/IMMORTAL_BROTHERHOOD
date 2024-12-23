import os
import sys
import warnings
import logging
from pathlib import Path
import ctypes

# Suppress all warnings and console windows
if sys.platform.startswith('win'):
    # Hide console window
    kernel32 = ctypes.WinDLL('kernel32')
    user32 = ctypes.WinDLL('user32')
    hwnd = kernel32.GetConsoleWindow()
    if hwnd != 0:
        user32.ShowWindow(hwnd, 0)
        
    # Prevent error dialogs
    SEM_NOGPFAULTERRORBOX = 0x0002
    kernel32.SetErrorMode(SEM_NOGPFAULTERRORBOX)
    CREATE_NO_WINDOW = 0x08000000
    subprocess_flags = CREATE_NO_WINDOW

# Suppress all warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['PYTHONWARNINGS'] = 'ignore'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Create handlers with UTF-8 encoding
file_handler = logging.FileHandler(log_dir / "divine_guardian.log", encoding='utf-8')
error_handler = logging.FileHandler(log_dir / "divine_guardian_errors.log", encoding='utf-8')
error_handler.setLevel(logging.ERROR)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)

# Setup root logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, error_handler],
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Redirect stdout and stderr to log files
sys.stdout = open(log_dir / "stdout.log", "a", encoding='utf-8')
sys.stderr = open(log_dir / "stderr.log", "a", encoding='utf-8')

import asyncio
import asyncio.sslproto as sslproto
import base64
import binascii
import importlib.util
import json
import logging
import os
import psutil
import subprocess
import sys
import traceback
from datetime import datetime
from dotenv import load_dotenv
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solders.keypair import Keypair

class DivineGuardian:
    def __init__(self):
        """Initialize the Divine Guardian"""
        self.consecutive_failures = 0
        self.MAX_FAILURES = 3
        self.CHECK_INTERVAL = 120  # 2 minutes
        self.last_trade_check = None
        
    def _load_env(self):
        """Load environment variables"""
        current_dir = Path(__file__).parent.resolve()
        env_path = (current_dir / ".." / ".." / ".env").resolve()
        
        if not env_path.exists():
            logging.error(f"[ERROR] .env file not found at {env_path}")
            raise ValueError(f"Missing .env file at {env_path}")
            
        load_dotenv(env_path)
        self.PRIVATE_KEY = os.getenv('SOLANA_PRIVATE_KEY')
        self.RPC_URL = os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')
        
        if not self.PRIVATE_KEY:
            raise ValueError("Missing SOLANA_PRIVATE_KEY in .env")

    def import_divine_master(self):
        """Import the Divine Master Controller dynamically"""
        try:
            spec = importlib.util.spec_from_file_location(
                "divine_master_controller",
                os.path.join(os.path.dirname(__file__), "divine_master_controller.py")
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            logging.error(f"[ERROR] Failed to import Divine Master: {str(e)}")
            return None

    async def verify_wallet_connection(self):
        """Verify wallet connection and balance"""
        try:
            client = AsyncClient(self.RPC_URL, commitment=Confirmed)
            keypair = Keypair.from_bytes(base58.b58decode(self.PRIVATE_KEY))
            
            # Check balance
            balance = await client.get_balance(keypair.pubkey())
            if balance.value == 0:
                logging.error("❌ Wallet has 0 balance!")
                return False
                
            logging.info(f"✅ Wallet connected! Balance: {balance.value / 1e9:.4f} SOL")
            await client.close()
            return True
            
        except Exception as e:
            logging.error(f"❌ Wallet verification failed: {str(e)}")
            return False

    async def verify_dex_connections(self):
        """Verify connections to DEXes"""
        try:
            client = AsyncClient(self.RPC_URL, commitment=Confirmed)
            
            # DEX Program IDs
            dexes = {
                'Raydium': 'RVKd61ztZW9GUwhRbbLoYVRE5Xf1B2tVscKqwZqXgEr',
                'Orca': '9W959DqEETiGZocYWCQPaJ6sBmUzgfxXfqGeTEdp3aQP',
                'Serum': '9xQeWvG816bUx9EPjHmaT23yvVM2ZWbrrpZb9PusVFin'
            }
            
            for dex, program_id in dexes.items():
                try:
                    await client.get_account_info(program_id)
                    logging.info(f"✅ {dex} connection verified!")
                except:
                    logging.error(f"❌ Failed to connect to {dex}")
                    return False
                    
            await client.close()
            return True
            
        except Exception as e:
            logging.error(f"❌ DEX verification failed: {str(e)}")
            return False

    async def verify_recent_trades(self):
        """Verify recent trading activity"""
        try:
            # Check trade history file
            history_path = Path("trade_history.json")
            if not history_path.exists():
                logging.warning("⚠️ No trade history found")
                return True  # Return True as this might be first run
                
            with open(history_path, 'r') as f:
                trades = json.load(f)
                
            if not trades:
                logging.warning("⚠️ Trade history is empty")
                return True
                
            latest_trade = trades[-1]
            trade_time = datetime.fromisoformat(latest_trade['timestamp'])
            time_since_trade = (datetime.now() - trade_time).total_seconds() / 60
            
            if time_since_trade > 120:  # 2 hours
                logging.warning(f"⚠️ No trades in the last {time_since_trade:.1f} minutes")
                return False
                
            logging.info(f"✅ Recent trade found {time_since_trade:.1f} minutes ago")
            return True
            
        except Exception as e:
            logging.error(f"❌ Trade verification failed: {str(e)}")
            return False

    async def verify_bot_running(self):
        """Verify the sniper bot is running without interrupting it"""
        try:
            # Instead of starting a new process, import and run the controller in the same process
            if not hasattr(self, 'divine_master'):
                module = self.import_divine_master()
                if module:
                    self.divine_master = module.DivineMasterController()
                    # Start the master controller in a separate task
                    asyncio.create_task(self.divine_master.run())
                    logging.info("[STATUS] Divine Master Controller started in-process")
                    return True
                return False
            return True
            
        except Exception as e:
            logging.error(f"[ERROR] Bot verification failed: {str(e)}")
            return False

    async def verify_trade_execution(self):
        """Verify trade execution is working without interrupting"""
        try:
            client = AsyncClient(self.RPC_URL, commitment=Confirmed)
            keypair = Keypair.from_bytes(base58.b58decode(self.PRIVATE_KEY))
            
            # Check recent transactions
            sigs = await client.get_signatures_for_address(keypair.pubkey())
            
            if not sigs.value:
                logging.warning("⚠️ No recent transactions found")
                return False
                
            # Check if most recent transaction is within last 2 hours
            latest_sig = sigs.value[0]
            time_since_tx = (datetime.now() - latest_sig.block_time).total_seconds() / 3600
            
            if time_since_tx > 2:
                logging.warning(f"⚠️ No transactions in the last {time_since_tx:.1f} hours")
                return False
                
            logging.info(f"✅ Recent transaction found {time_since_tx:.1f} hours ago")
            await client.close()
            return True
            
        except Exception as e:
            logging.error(f"❌ Trade execution verification failed: {str(e)}")
            return False

    async def fix_connection_issues(self):
        """Fix connection issues without stopping the bot"""
        try:
            logging.info("🔧 Attempting to fix connection issues...")
            
            # Check RPC connection
            client = AsyncClient(self.RPC_URL, commitment=Confirmed)
            try:
                await client.get_health()
                logging.info("✅ RPC connection restored!")
            except:
                # Try alternate RPC endpoints
                alternate_rpcs = [
                    'https://api.mainnet-beta.solana.com',
                    'https://solana-api.projectserum.com',
                    'https://rpc.ankr.com/solana'
                ]
                
                for rpc in alternate_rpcs:
                    try:
                        client = AsyncClient(rpc, commitment=Confirmed)
                        await client.get_health()
                        self.RPC_URL = rpc
                        logging.info(f"✅ Switched to working RPC: {rpc}")
                        break
                    except:
                        continue
                        
            await client.close()
            
            # Verify wallet
            if not await self.verify_wallet_connection():
                logging.error("❌ Wallet connection issues persist")
                return False
                
            # Verify DEX connections
            if not await self.verify_dex_connections():
                logging.error("❌ DEX connection issues persist")
                return False
                
            logging.info("✅ Connection issues resolved!")
            return True
            
        except Exception as e:
            logging.error(f"❌ Failed to fix connection issues: {str(e)}")
            return False

    async def check_wallet_balance(self):
        """Check and display current wallet balance"""
        try:
            client = AsyncClient(self.RPC_URL, commitment=Confirmed)
            
            # Convert base58 private key to Keypair
            from solders.keypair import Keypair
            from base58 import b58decode
            
            # Clean private key
            clean_key = self.PRIVATE_KEY.strip()
            
            # Decode base58 key
            key_bytes = b58decode(clean_key)
            keypair = Keypair.from_bytes(key_bytes)
            
            # Get wallet address
            wallet_address = str(keypair.pubkey())
            
            # Get SOL balance
            balance = await client.get_balance(keypair.pubkey())
            sol_balance = balance.value / 1e9  # Convert lamports to SOL
            
            logging.info(f"""
[WALLET STATUS]
Address: {wallet_address}
Balance: {sol_balance:.4f} SOL
RPC: {self.RPC_URL}
            """)
            
            await client.close()
            return sol_balance
            
        except Exception as e:
            logging.error(f"[ERROR] Failed to check wallet balance: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            return None

    async def guardian_check(self):
        """Perform all verification checks without interrupting the bot"""
        try:
            logging.info("[STATUS] Starting Divine Guardian check...")
            
            # Check wallet balance first
            balance = await self.check_wallet_balance()
            if balance is None:
                self.consecutive_failures += 1
                return False
                
            # First verify bot is running
            bot_running = await self.verify_bot_running()
            if not bot_running:
                self.consecutive_failures += 1
                return False
                
            # Check wallet connection
            wallet_ok = await self.verify_wallet_connection()
            if not wallet_ok:
                self.consecutive_failures += 1
                await self.fix_connection_issues()
                return False
                
            # Check DEX connections
            dex_ok = await self.verify_dex_connections()
            if not dex_ok:
                self.consecutive_failures += 1
                await self.fix_connection_issues()
                return False
                
            # Check trade execution
            trades_ok = await self.verify_trade_execution()
            if not trades_ok:
                self.consecutive_failures += 1
                return False
                
            # Check recent trades
            recent_trades = await self.verify_recent_trades()
            if not recent_trades:
                self.consecutive_failures += 1
                return False
                
            self.consecutive_failures = 0
            logging.info("✅ All systems operational!")
            return True
            
        except Exception as e:
            logging.error(f"❌ Guardian check failed: {str(e)}")
            self.consecutive_failures += 1
            return False

    async def run_forever(self):
        """Run the guardian forever"""
        while True:
            try:
                check_result = await self.guardian_check()
                
                if not check_result and self.consecutive_failures >= self.MAX_FAILURES:
                    logging.warning(f"⚠️ {self.consecutive_failures} consecutive failures! Attempting recovery...")
                    await self.fix_connection_issues()
                    self.consecutive_failures = 0
                    
                # Check every 2 minutes
                await asyncio.sleep(self.CHECK_INTERVAL)
            except Exception as e:
                logging.error(f"[ERROR] Guardian check failed: {str(e)}")
                await asyncio.sleep(30)

if __name__ == "__main__":
    try:
        # Hide console window on Windows
        if sys.platform.startswith('win'):
            kernel32 = ctypes.WinDLL('kernel32')
            user32 = ctypes.WinDLL('user32')
            hwnd = kernel32.GetConsoleWindow()
            if hwnd != 0:
                user32.ShowWindow(hwnd, 0)
            
            # Prevent Windows Error Reporting dialog
            kernel32.SetErrorMode(0x0001 | 0x0002 | 0x0004)

        guardian = DivineGuardian()
        guardian._load_env()
        
        # Run in a completely detached way
        if sys.platform.startswith('win'):
            import subprocess
            CREATE_NO_WINDOW = 0x08000000
            subprocess.Popen([sys.executable, __file__], 
                           creationflags=CREATE_NO_WINDOW,
                           start_new_session=True)
        else:
            asyncio.run(guardian.run_forever())
    except Exception as e:
        logging.error(f"Failed to start guardian: {str(e)}")
