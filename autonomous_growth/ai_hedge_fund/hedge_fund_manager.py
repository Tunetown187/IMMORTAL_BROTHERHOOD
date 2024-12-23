from typing import List, Dict
import numpy as np
from datetime import datetime
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIHedgeFundManager:
    def __init__(self, fund_name: str, initial_capital: float):
        self.fund_name = fund_name
        self.capital = initial_capital
        self.portfolio = {}
        self.proposals = []
        self.performance_history = []
        self.risk_threshold = 0.3  # 30% max risk tolerance
        
    def evaluate_proposal(self, proposal: Dict) -> Dict:
        """
        Evaluate an investment proposal using AI analysis
        """
        score = 0
        
        # Evaluate based on multiple criteria
        criteria = {
            'market_potential': self._analyze_market_potential(proposal),
            'risk_assessment': self._assess_risk(proposal),
            'team_capability': self._evaluate_team(proposal),
            'innovation_score': self._rate_innovation(proposal)
        }
        
        weighted_score = (
            criteria['market_potential'] * 0.3 +
            criteria['risk_assessment'] * 0.3 +
            criteria['team_capability'] * 0.2 +
            criteria['innovation_score'] * 0.2
        )
        
        return {
            'proposal_id': proposal['id'],
            'score': weighted_score,
            'criteria': criteria,
            'recommendation': 'accept' if weighted_score > 0.7 else 'reject'
        }
    
    def allocate_capital(self, proposal_id: str, amount: float) -> bool:
        """
        Allocate capital to an approved proposal
        """
        if amount > self.capital:
            logger.warning(f"Insufficient funds for proposal {proposal_id}")
            return False
            
        self.portfolio[proposal_id] = {
            'amount': amount,
            'timestamp': datetime.now(),
            'status': 'active'
        }
        self.capital -= amount
        return True
    
    def _analyze_market_potential(self, proposal: Dict) -> float:
        # AI analysis of market potential
        # Placeholder for actual market analysis logic
        return np.random.uniform(0.5, 1.0)
    
    def _assess_risk(self, proposal: Dict) -> float:
        # AI risk assessment
        # Placeholder for actual risk assessment logic
        return np.random.uniform(0.3, 0.9)
    
    def _evaluate_team(self, proposal: Dict) -> float:
        # AI team evaluation
        # Placeholder for actual team evaluation logic
        return np.random.uniform(0.4, 1.0)
    
    def _rate_innovation(self, proposal: Dict) -> float:
        # AI innovation rating
        # Placeholder for actual innovation rating logic
        return np.random.uniform(0.6, 1.0)
    
    def get_fund_performance(self) -> Dict:
        """
        Calculate and return fund performance metrics
        """
        return {
            'total_capital': self.capital,
            'active_investments': len(self.portfolio),
            'total_return': sum(inv['amount'] for inv in self.portfolio.values()),
            'performance_history': self.performance_history
        }
