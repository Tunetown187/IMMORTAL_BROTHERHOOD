import asyncio
import signal
import sys
from solana_sniper_strategy import SolanaSniper
import logging

# Global flag for graceful shutdown
shutdown = False

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global shutdown
    print("\n🛑 Received shutdown signal. Closing positions and stopping gracefully...")
    shutdown = True

async def main():
    """Main entry point"""
    try:
        # Setup signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Initialize sniper
        sniper = SolanaSniper()
        
        print("""
        🏰 Divine Empire Solana Sniper 🏰
        ================================
        ⚔️  Monitoring DEXes for opportunities
        🛡️  Divine Blessing protection enabled
        💰  Max SOL per trade: {sniper.max_sol_per_trade}
        🎯  Risk threshold: {sniper.risk_threshold}
        ⛔️  Stop loss: {sniper.stop_loss_percentage}%
        ✨  Take profit: {sniper.take_profit_percentage}%
        🔄  Max daily trades: {sniper.max_daily_trades}
        """)
        
        # Start monitoring
        while not shutdown:
            await sniper.monitor_tokens()
            await asyncio.sleep(1)  # Prevent CPU overload
            
        # Graceful shutdown
        print("Shutting down Divine Empire Sniper...")
        
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Divine Empire Sniper stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)
