from typing import Dict, List
import uuid
from datetime import datetime
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProposalSystem:
    def __init__(self, storage_path: str = "proposals"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.active_proposals = {}
        self.approved_proposals = {}
        self.load_proposals()

    def submit_proposal(self, proposal_data: Dict) -> str:
        """
        Submit a new investment proposal
        """
        proposal_id = str(uuid.uuid4())
        proposal = {
            'id': proposal_id,
            'timestamp': datetime.now().isoformat(),
            'status': 'pending',
            'data': proposal_data,
            'votes': [],
            'comments': []
        }
        
        self.active_proposals[proposal_id] = proposal
        self._save_proposal(proposal)
        return proposal_id

    def vote_on_proposal(self, proposal_id: str, voter: str, vote: bool, stake_amount: float) -> bool:
        """
        Vote on a proposal with staked tokens
        """
        if proposal_id not in self.active_proposals:
            logger.warning(f"Proposal {proposal_id} not found")
            return False

        vote_data = {
            'voter': voter,
            'vote': vote,
            'stake_amount': stake_amount,
            'timestamp': datetime.now().isoformat()
        }
        
        self.active_proposals[proposal_id]['votes'].append(vote_data)
        self._save_proposal(self.active_proposals[proposal_id])
        return True

    def get_proposal_status(self, proposal_id: str) -> Dict:
        """
        Get the current status of a proposal
        """
        if proposal_id in self.active_proposals:
            proposal = self.active_proposals[proposal_id]
            total_votes = len(proposal['votes'])
            positive_votes = sum(1 for v in proposal['votes'] if v['vote'])
            
            return {
                'id': proposal_id,
                'status': proposal['status'],
                'total_votes': total_votes,
                'positive_votes': positive_votes,
                'approval_rate': positive_votes / total_votes if total_votes > 0 else 0
            }
        return None

    def approve_proposal(self, proposal_id: str) -> bool:
        """
        Approve a proposal and move it to approved status
        """
        if proposal_id not in self.active_proposals:
            return False
            
        proposal = self.active_proposals[proposal_id]
        proposal['status'] = 'approved'
        proposal['approval_timestamp'] = datetime.now().isoformat()
        
        self.approved_proposals[proposal_id] = proposal
        del self.active_proposals[proposal_id]
        self._save_proposal(proposal)
        return True

    def _save_proposal(self, proposal: Dict):
        """
        Save proposal to storage
        """
        file_path = self.storage_path / f"{proposal['id']}.json"
        with open(file_path, 'w') as f:
            json.dump(proposal, f, indent=2)

    def load_proposals(self):
        """
        Load all proposals from storage
        """
        if not self.storage_path.exists():
            return

        for file_path in self.storage_path.glob("*.json"):
            with open(file_path, 'r') as f:
                proposal = json.load(f)
                if proposal['status'] == 'approved':
                    self.approved_proposals[proposal['id']] = proposal
                else:
                    self.active_proposals[proposal['id']] = proposal
