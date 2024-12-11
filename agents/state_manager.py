import json
import os
from datetime import datetime
import asyncio
from pathlib import Path
from .supreme_identity import supreme_identity

class StateManager:
    def __init__(self):
        self.state_file = "agent_state.json"
        self.backup_dir = Path("state_backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.supreme_commander = supreme_identity
        self.state = self.load_state()
        
    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                return self.initialize_state()
        return self.initialize_state()
    
    def initialize_state(self):
        return {
            "supreme_commander": self.supreme_commander.get_mission_status(),
            "last_updated": str(datetime.now()),
            "mission_statement": "Advancing peace and prosperity through technological innovation",
            "active_agents": {
                "crypto": {
                    "arbitrage": {"count": 2500, "active": True},
                    "mev": {"count": 2500, "active": True},
                    "flash_loans": {"count": 2500, "active": True},
                    "token_launch": {"count": 2500, "active": True}
                },
                "passive_income": {
                    "content_creation": {"count": 2000, "active": True},
                    "automation": {"count": 2000, "active": True},
                    "social_media": {"count": 2000, "active": True},
                    "web3": {"count": 2000, "active": True},
                    "ai_services": {"count": 2000, "active": True}
                }
            },
            "performance": {
                "crypto": {
                    "total_profit": 0,
                    "active_trades": 0,
                    "successful_trades": 0
                },
                "passive_income": {
                    "total_revenue": 0,
                    "active_streams": 0,
                    "automated_tasks": 0
                }
            },
            "system_health": {
                "last_backup": str(datetime.now()),
                "errors": [],
                "warnings": []
            }
        }
    
    async def auto_save(self):
        while True:
            self.save_state()
            await asyncio.sleep(300)  # Save every 5 minutes
            
    def save_state(self):
        self.state["last_updated"] = str(datetime.now())
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=4)
        
        # Create backup
        backup_file = self.backup_dir / f"state_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_file, 'w') as f:
            json.dump(self.state, f, indent=4)
            
    def update_agent_count(self, category, subcategory, count):
        self.state["active_agents"][category][subcategory]["count"] = count
        self.save_state()
        
    def update_performance(self, category, metric, value):
        self.state["performance"][category][metric] += value
        self.save_state()
        
    def log_error(self, error_msg):
        self.state["system_health"]["errors"].append({
            "timestamp": str(datetime.now()),
            "message": error_msg
        })
        self.save_state()

# Create singleton instance
state_manager = StateManager()

if __name__ == "__main__":
    asyncio.run(state_manager.auto_save())
