import os
import subprocess
import logging
from pathlib import Path
import streamlit as st
from resource_manager import ResourceManager
from agent_orchestrator import AgentOrchestrator
from agent_config_manager import AgentConfigManager
from marketing_automation import MarketingAutomation

class Deployment:
    def __init__(self):
        self.setup_logging()
        self.resource_manager = ResourceManager()
        self.agent_orchestrator = AgentOrchestrator()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    async def prepare_deployment(self):
        """Prepare all resources for deployment"""
        try:
            # Scan and prepare local resources
            self.logger.info("Scanning local resources...")
            await self.resource_manager.scan_local_resources()
            await self.resource_manager.scan_browser_profiles()
            
            # Prepare deployment resources
            self.logger.info("Preparing deployment resources...")
            deploy_dir = await self.resource_manager.prepare_for_deployment()
            
            if not deploy_dir:
                raise Exception("Failed to prepare deployment resources")
                
            return deploy_dir
            
        except Exception as e:
            self.logger.error(f"Error preparing deployment: {str(e)}")
            return None

    async def push_to_github(self, repo_url: str, branch: str = "main"):
        """Push code to GitHub"""
        try:
            # Initialize git if needed
            if not os.path.exists(".git"):
                subprocess.run(["git", "init"])
                
            # Add remote if not exists
            try:
                subprocess.run(["git", "remote", "add", "origin", repo_url])
            except:
                pass
                
            # Add all files
            subprocess.run(["git", "add", "."])
            
            # Commit
            subprocess.run(["git", "commit", "-m", "Autonomous deployment"])
            
            # Push
            subprocess.run(["git", "push", "-u", "origin", branch])
            
            self.logger.info(f"Successfully pushed to {repo_url}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error pushing to GitHub: {str(e)}")
            return False

    def setup_streamlit(self):
        """Create Streamlit app configuration"""
        try:
            config_dir = Path(".streamlit")
            config_dir.mkdir(exist_ok=True)
            
            # Create config.toml
            config_path = config_dir / "config.toml"
            config_content = """
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
font = "sans serif"

[server]
runOnSave = true
"""
            config_path.write_text(config_content)
            
            # Create secrets.toml template
            secrets_path = config_dir / "secrets.toml"
            secrets_content = """
# API Keys
OPENAI_API_KEY = ""
ANTHROPIC_API_KEY = ""
GOOGLE_API_KEY = ""
MISTRAL_API_KEY = ""
TOGETHER_API_KEY = ""
PERPLEXITY_API_KEY = ""
SKYVERN_API_KEY = ""

# Service Credentials
STRIPE_SECRET_KEY = ""
SENDGRID_API_KEY = ""
TWILIO_ACCOUNT_SID = ""
TWILIO_AUTH_TOKEN = ""

# Database
DATABASE_URL = ""
"""
            secrets_path.write_text(secrets_content)
            
            self.logger.info("Streamlit configuration created")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up Streamlit: {str(e)}")
            return False

def main():
    st.set_page_config(
        page_title="AI Business Agent",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 AI Business Agent")
    
    # Initialize components
    resource_manager = ResourceManager()
    agent_orchestrator = AgentOrchestrator()
    marketing = MarketingAutomation()
    
    # Sidebar
    st.sidebar.title("Control Panel")
    
    if st.sidebar.button("Spawn New Agent"):
        agent_id = agent_orchestrator.spawn_agent("business_builder")
        st.success(f"New agent spawned: {agent_id}")
    
    if st.sidebar.button("Start Business Operations"):
        business = agent_orchestrator.start_business_operations(agent_id)
        st.success(f"Business operations started: {business['name']}")
    
    # Main content
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Active Agents")
        agents = agent_orchestrator.get_active_agents()
        for agent in agents:
            st.write(f"Agent ID: {agent['id']}")
            st.write(f"Status: {agent['status']}")
            st.write(f"Business: {agent['business_name']}")
            st.write("---")
    
    with col2:
        st.subheader("Business Metrics")
        metrics = agent_orchestrator.get_business_metrics()
        st.metric("Total Revenue", f"${metrics['total_revenue']:,.2f}")
        st.metric("Active Products", metrics['active_products'])
        st.metric("Customer Count", metrics['customer_count'])
    
    # Marketing campaigns
    st.subheader("Marketing Campaigns")
    campaigns = marketing.get_active_campaigns()
    for campaign in campaigns:
        with st.expander(f"Campaign: {campaign['name']}"):
            st.write(f"Type: {campaign['type']}")
            st.write(f"Status: {campaign['status']}")
            st.write(f"Performance: {campaign['metrics']}")

if __name__ == "__main__":
    main()
