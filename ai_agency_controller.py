import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json
import asyncio
from typing import Dict, List, Optional
import logging

# Import our AI hedge fund components
from ai_hedge_fund.crypto.crypto_intelligence_engine import CryptoIntelligenceEngine
from ai_hedge_fund.crypto.defi_integration_engine import DefiIntegrationEngine
from ai_hedge_fund.crypto.social_amm_engine import SocialAMMEngine
from ai_hedge_fund.hedge_fund_manager import AIHedgeFundManager
from ai_hedge_fund.dao_controller import DAOController

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIAgencyController:
    def __init__(self):
        self.crypto_engine = CryptoIntelligenceEngine()
        self.defi_engine = DefiIntegrationEngine()
        self.social_amm_engine = SocialAMMEngine()
        self.hedge_fund_manager = AIHedgeFundManager("AI Hedge Fund", 1000000)
        self.dao_controller = DAOController()
        
        # Load configurations
        with open('config/solana_config.json', 'r') as f:
            self.solana_config = json.load(f)
            
    async def get_system_status(self) -> Dict:
        """Get status of all AI agency components"""
        return {
            'crypto_intelligence': await self.crypto_engine.get_status(),
            'defi_integration': await self.defi_engine.deploy_cross_chain_strategy(),
            'social_amm': await self.social_amm_engine.manage_automated_market_making(),
            'hedge_fund': self.hedge_fund_manager.get_performance_metrics(),
            'dao': self.dao_controller.get_status()
        }
        
    async def get_market_opportunities(self) -> List[Dict]:
        """Get current market opportunities"""
        return await self.crypto_engine.analyze_opportunities()
        
    async def get_defi_positions(self) -> List[Dict]:
        """Get current DeFi positions"""
        return await self.defi_engine.optimize_yield_farming()
        
    async def get_amm_metrics(self) -> Dict:
        """Get AMM performance metrics"""
        return await self.social_amm_engine.optimize_trading_strategies()
        
    def run_streamlit_app(self):
        """Run the Streamlit dashboard"""
        st.set_page_config(page_title="AI Agency Controller", layout="wide")
        
        # Sidebar
        st.sidebar.title("AI Agency Controller")
        page = st.sidebar.selectbox(
            "Select Page",
            ["Overview", "Crypto Intelligence", "DeFi Integration", "Social AMM", "Hedge Fund", "DAO"]
        )
        
        if page == "Overview":
            self._render_overview_page()
        elif page == "Crypto Intelligence":
            self._render_crypto_page()
        elif page == "DeFi Integration":
            self._render_defi_page()
        elif page == "Social AMM":
            self._render_amm_page()
        elif page == "Hedge Fund":
            self._render_hedge_fund_page()
        elif page == "DAO":
            self._render_dao_page()
            
    def _render_overview_page(self):
        st.title("AI Agency Overview")
        
        # System Status
        st.header("System Status")
        status = asyncio.run(self.get_system_status())
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Active Strategies", len(status['hedge_fund']['active_strategies']))
            
        with col2:
            st.metric("Total Value Locked", f"${status['defi_integration']['tvl']:,.2f}")
            
        with col3:
            st.metric("24h Volume", f"${status['social_amm']['volume_24h']:,.2f}")
            
        # Performance Chart
        st.header("Performance Overview")
        performance_data = pd.DataFrame(status['hedge_fund']['performance_history'])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=performance_data['date'], y=performance_data['value'],
                                mode='lines', name='Portfolio Value'))
        st.plotly_chart(fig)
        
    def _render_crypto_page(self):
        st.title("Crypto Intelligence")
        
        # Market Opportunities
        st.header("Market Opportunities")
        opportunities = asyncio.run(self.get_market_opportunities())
        
        if opportunities:
            df = pd.DataFrame(opportunities)
            st.dataframe(df)
            
        # Trend Analysis
        st.header("Trend Analysis")
        trends = self.crypto_engine.get_current_trends()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top Trending Assets")
            st.write(trends['top_assets'])
            
        with col2:
            st.subheader("Emerging Patterns")
            st.write(trends['patterns'])
            
    def _render_defi_page(self):
        st.title("DeFi Integration")
        
        # DeFi Positions
        st.header("Active DeFi Positions")
        positions = asyncio.run(self.get_defi_positions())
        
        if positions:
            df = pd.DataFrame(positions)
            st.dataframe(df)
            
        # Yield Farming Opportunities
        st.header("Yield Farming Opportunities")
        opportunities = self.defi_engine.get_yield_opportunities()
        
        if opportunities:
            df = pd.DataFrame(opportunities)
            st.dataframe(df)
            
    def _render_amm_page(self):
        st.title("Social AMM")
        
        # AMM Metrics
        st.header("AMM Performance")
        metrics = asyncio.run(self.get_amm_metrics())
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Liquidity", f"${metrics['total_liquidity']:,.2f}")
            
        with col2:
            st.metric("24h Fees", f"${metrics['fees_24h']:,.2f}")
            
        with col3:
            st.metric("Active LPs", metrics['active_lps'])
            
        # Pool Performance
        st.header("Pool Performance")
        pool_data = pd.DataFrame(metrics['pool_performance'])
        st.dataframe(pool_data)
            
    def _render_hedge_fund_page(self):
        st.title("Hedge Fund Management")
        
        # Fund Metrics
        metrics = self.hedge_fund_manager.get_performance_metrics()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("AUM", f"${metrics['aum']:,.2f}")
            
        with col2:
            st.metric("Monthly Return", f"{metrics['monthly_return']:.2f}%")
            
        with col3:
            st.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.2f}")
            
        # Portfolio Composition
        st.header("Portfolio Composition")
        portfolio = pd.DataFrame(metrics['portfolio'])
        st.dataframe(portfolio)
            
    def _render_dao_page(self):
        st.title("DAO Governance")
        
        # Active Proposals
        st.header("Active Proposals")
        proposals = self.dao_controller.get_active_proposals()
        
        if proposals:
            df = pd.DataFrame(proposals)
            st.dataframe(df)
            
        # Voting Power Distribution
        st.header("Voting Power Distribution")
        voting_power = pd.DataFrame(self.dao_controller.get_voting_power_distribution())
        fig = go.Figure(data=[go.Pie(labels=voting_power['holder'],
                                    values=voting_power['power'])])
        st.plotly_chart(fig)

if __name__ == "__main__":
    controller = AIAgencyController()
    controller.run_streamlit_app()
