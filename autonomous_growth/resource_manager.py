import logging
import json
from typing import Dict, List
import streamlit as st
from datetime import datetime

class ResourceManager:
    def __init__(self):
        self.setup_logging()
        self.resources = {}
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def allocate_resource(self, resource_type: str, amount: float) -> bool:
        """Allocate resources for an operation"""
        try:
            if resource_type not in self.resources:
                self.resources[resource_type] = 0
                
            self.resources[resource_type] += amount
            self.logger.info(f"Allocated {amount} of {resource_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error allocating resource: {str(e)}")
            return False
            
    def release_resource(self, resource_type: str, amount: float) -> bool:
        """Release allocated resources"""
        try:
            if resource_type in self.resources:
                if self.resources[resource_type] >= amount:
                    self.resources[resource_type] -= amount
                    self.logger.info(f"Released {amount} of {resource_type}")
                    return True
                else:
                    self.logger.warning(f"Insufficient {resource_type} to release")
                    return False
            else:
                self.logger.warning(f"Resource type {resource_type} not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Error releasing resource: {str(e)}")
            return False
            
    def get_resource_status(self) -> Dict:
        """Get current status of all resources"""
        return self.resources.copy()
        
    def clear_resources(self):
        """Clear all resource allocations"""
        self.resources.clear()
        self.logger.info("All resources cleared")
