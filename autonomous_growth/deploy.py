import os
import subprocess
import logging
from pathlib import Path
import streamlit as st
from resource_manager import ResourceManager
from agent_orchestrator import AgentOrchestrator
from agent_config_manager import AgentConfigManager
from marketing_automation import MarketingAutomation
from payment_handler import PaymentHandler

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
    payment_handler = PaymentHandler()
    
    # Sidebar
    st.sidebar.title("Control Panel")
    
    # Main content
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Active Agents")
        st.write("No active agents")
    
    with col2:
        st.subheader("Business Metrics")
        st.metric("Total Revenue", "$0.00")
        st.metric("Active Products", "0")
        st.metric("Customer Count", "0")
    
    with col3:
        st.subheader("Payment Status")
        st.write("No payment data available")
    
    # Marketing campaigns
    st.subheader("Marketing Campaigns")
    st.write("No active campaigns")
    
    # Products and Payments
    st.subheader("Products and Payments")
    with st.expander("Create New Product"):
        with st.form("new_product"):
            name = st.text_input("Product Name")
            description = st.text_area("Description")
            price = st.number_input("Price (USD)", min_value=0.0, step=0.01)
            if st.form_submit_button("Create"):
                try:
                    product = payment_handler.create_product(name, description, price)
                    if product:
                        st.success(f"Product created: {name}")
                    else:
                        st.error("Failed to create product")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
