import asyncio
import logging
from controller import SniperController
from core.divine_master_bot import DivineMasterBot

async def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("logs/sniper.log"),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger("SniperLauncher")

    try:
        # Create and initialize controller
        controller = SniperController()
        await controller.initialize()
        
        # Start the controller
        await controller.start()
        
        # Keep the script running
        while True:
            try:
                # Get and log performance stats every 5 minutes
                stats = controller.get_performance_stats()
                logger.info(f"Performance Stats: {stats}")
                
                await asyncio.sleep(300)  # 5 minutes
                
            except KeyboardInterrupt:
                logger.info("Shutdown signal received")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                await asyncio.sleep(60)  # Wait a bit before retrying
                
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
    finally:
        # Ensure clean shutdown
        if 'controller' in locals():
            await controller.stop()
        logger.info("Shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())
