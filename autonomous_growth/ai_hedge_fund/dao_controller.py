from typing import Dict, List
import logging
from pathlib import Path
from datetime import datetime
from .hedge_fund_manager import AIHedgeFundManager
from .proposal_system import ProposalSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIHedgeFundDAO:
    def __init__(self, fund_name: str, initial_capital: float):
        self.fund_manager = AIHedgeFundManager(fund_name, initial_capital)
        self.proposal_system = ProposalSystem()
        self.members = {}
        self.governance_rules = {
            'min_stake': 1000,  # Minimum stake required to participate
            'proposal_threshold': 0.6,  # 60% approval needed
            'voting_period': 7,  # 7 days voting period
            'min_voters': 10  # Minimum number of voters required
        }

    async def submit_investment_proposal(self, proposal_data: Dict) -> str:
        """
        Submit a new investment proposal to the DAO
        """
        # Validate proposal data
        if not self._validate_proposal(proposal_data):
            raise ValueError("Invalid proposal data")

        # Submit to proposal system
        proposal_id = self.proposal_system.submit_proposal(proposal_data)
        
        # Trigger AI evaluation
        evaluation = self.fund_manager.evaluate_proposal({
            'id': proposal_id,
            **proposal_data
        })
        
        logger.info(f"New proposal submitted: {proposal_id}")
        logger.info(f"AI Evaluation score: {evaluation['score']}")
        
        return proposal_id

    async def vote_on_proposal(self, proposal_id: str, voter_address: str, vote: bool, stake_amount: float) -> bool:
        """
        Vote on an active proposal
        """
        if stake_amount < self.governance_rules['min_stake']:
            raise ValueError(f"Minimum stake required: {self.governance_rules['min_stake']}")

        success = self.proposal_system.vote_on_proposal(
            proposal_id, voter_address, vote, stake_amount
        )
        
        if success:
            self._check_proposal_status(proposal_id)
        
        return success

    async def get_fund_status(self) -> Dict:
        """
        Get current status of the hedge fund
        """
        performance = self.fund_manager.get_fund_performance()
        active_proposals = len(self.proposal_system.active_proposals)
        approved_proposals = len(self.proposal_system.approved_proposals)
        
        return {
            'fund_performance': performance,
            'active_proposals': active_proposals,
            'approved_proposals': approved_proposals,
            'total_members': len(self.members)
        }

    def _validate_proposal(self, proposal_data: Dict) -> bool:
        """
        Validate proposal data
        """
        required_fields = ['title', 'description', 'requested_amount', 'expected_return']
        return all(field in proposal_data for field in required_fields)

    def _check_proposal_status(self, proposal_id: str):
        """
        Check if proposal meets criteria for approval
        """
        status = self.proposal_system.get_proposal_status(proposal_id)
        if not status:
            return

        if (status['total_votes'] >= self.governance_rules['min_voters'] and 
            status['approval_rate'] >= self.governance_rules['proposal_threshold']):
            
            # Approve proposal
            if self.proposal_system.approve_proposal(proposal_id):
                proposal = self.proposal_system.approved_proposals[proposal_id]
                amount = proposal['data']['requested_amount']
                
                # Allocate capital
                self.fund_manager.allocate_capital(proposal_id, amount)
                logger.info(f"Proposal {proposal_id} approved and funded")
