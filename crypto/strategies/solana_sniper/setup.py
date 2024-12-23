import os
import shutil
from pathlib import Path

def setup_sniper_bot():
    """Setup the Solana Sniper Bot directory structure"""
    
    # Base paths
    source_dir = Path("C:/Users/p8tty/Downloads/Pump.Fun-Sniper-Bot-main/Pump.Fun-Sniper-Bot-main")
    target_dir = Path("c:/Users/p8tty/Downloads/agency-swarm-0.2.0/crypto/strategies/solana_sniper")
    
    # Create necessary directories
    directories = [
        "core",
        "agents",
        "strategies",
        "config",
        "logs"
    ]
    
    for dir_name in directories:
        os.makedirs(target_dir / dir_name, exist_ok=True)
    
    # Copy core bot files
    core_files = [
        "divine_master_bot.py",
        "PumpFunBot.py",
        "EnhancedPumpBot.py"
    ]
    
    for file in core_files:
        if (source_dir / file).exists():
            shutil.copy2(source_dir / file, target_dir / "core" / file)
    
    # Copy configuration files
    config_files = [
        "config.json",
        "token_list.json"
    ]
    
    for file in config_files:
        if (source_dir / file).exists():
            shutil.copy2(source_dir / file, target_dir / "config" / file)
    
    # Copy requirements file
    if (source_dir / "requirements_enhanced.txt").exists():
        shutil.copy2(
            source_dir / "requirements_enhanced.txt",
            target_dir / "requirements.txt"
        )

if __name__ == "__main__":
    setup_sniper_bot()
