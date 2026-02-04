"""
Skill: skill_commerce

Agentic Commerce using Coinbase AgentKit for financial autonomy.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field


# Configuration
MAX_DAILY_SPEND = 50.0  # USDC
MAX_TRANSACTION_AMOUNT = 10.0  # USDC


# Input Schema
class CommerceInput(BaseModel):
    """Input contract for skill_commerce"""
    action: str = Field(..., description="Action: get_balance | transfer | deploy_token")
    to_address: Optional[str] = None
    amount: Optional[float] = None
    asset: str = Field(default="USDC", description="Asset symbol")


# Output Schema
class CommerceOutput(BaseModel):
    """Output contract for skill_commerce"""
    status: str = Field(..., pattern="^(success|error|blocked)$")
    message: str
    transaction_hash: Optional[str] = None
    balance: Optional[float] = None
    error_message: Optional[str] = None


class BudgetExceededError(Exception):
    """Raised when transaction exceeds budget."""
    pass


class CommerceSkill:
    """
    Commerce skill using Coinbase AgentKit.
    
    Enables agents to:
    - Check wallet balance
    - Send transactions (within budget limits)
    - Deploy tokens
    """
    
    def __init__(self, agent_id: str):
        """Initialize the commerce skill.
        
        Args:
            agent_id: ID of the agent owning this wallet
        """
        self.agent_id = agent_id
        self.name = "skill_commerce"
        self.version = "1.0.0"
        self._wallet_initialized = False
        
        # Budget tracking
        self._daily_spend = 0.0
        
    def _check_budget(self, amount: float) -> bool:
        """Check if transaction is within budget."""
        return (self._daily_spend + amount) <= MAX_DAILY_SPEND
    
    def _check_max_transaction(self, amount: float) -> bool:
        """Check if transaction is below max per-transaction limit."""
        return amount <= MAX_TRANSACTION_AMOUNT
    
    def execute(self, action: str, to_address: str = None,
                amount: float = None, asset: str = "USDC") -> CommerceOutput:
        """
        Execute commerce action.
        
        Args:
            action: get_balance | transfer | deploy_token
            to_address: Destination wallet address
            amount: Amount to transfer
            asset: Asset symbol (USDC, ETH)
            
        Returns:
            CommerceOutput with result
        """
        # Validate action
        valid_actions = ["get_balance", "transfer", "deploy_token"]
        if action not in valid_actions:
            return CommerceOutput(
                status="error",
                message=f"Invalid action. Must be one of: {valid_actions}"
            )
        
        # get_balance - no budget check needed
        if action == "get_balance":
            return self._get_balance(asset)
        
        # Transfer - requires amount and address
        if action == "transfer":
            if not to_address or not amount:
                return CommerceOutput(
                    status="error",
                    message="transfer requires to_address and amount"
                )
            return self._transfer(to_address, amount, asset)
        
        # deploy_token - high value action, always requires CFO review
        if action == "deploy_token":
            return self._deploy_token()
    
    def _get_balance(self, asset: str) -> CommerceOutput:
        """Get wallet balance."""
        # TODO: Integrate with Coinbase AgentKit
        # from coinbase.agent import CdpEvmWalletProvider
        
        return CommerceOutput(
            status="success",
            message=f"Retrieved {asset} balance",
            balance=100.0,  # Placeholder
        )
    
    def _transfer(self, to_address: str, amount: float, 
                  asset: str) -> CommerceOutput:
        """Execute transfer with budget checks."""
        # Budget check
        if not self._check_budget(amount):
            return CommerceOutput(
                status="blocked",
                message=f"Budget exceeded. Current: {self._daily_spend}, Requested: {amount}, Limit: {MAX_DAILY_SPEND}"
            )
        
        # Max transaction check
        if not self._check_max_transaction(amount):
            return CommerceOutput(
                status="blocked",
                message=f"Transaction exceeds max amount. Max: {MAX_TRANSACTION_AMOUNT}, Requested: {amount}"
            )
        
        # TODO: Integrate with Coinbase AgentKit
        # Use erc20_action_provider for USDC transfers
        
        # Update daily spend
        self._daily_spend += amount
        
        return CommerceOutput(
            status="success",
            message=f"Transferred {amount} {asset} to {to_address}",
            transaction_hash="0x123...",  # Placeholder
        )
    
    def _deploy_token(self) -> CommerceOutput:
        """Deploy ERC-20 token."""
        # This action requires CFO (human) review
        return CommerceOutput(
            status="blocked",
            message="Token deployment requires CFO approval. Escalate to human reviewer."
        )


class CommerceManager:
    """
    Manager for multiple agent wallets.
    Handles initialization and budget tracking.
    """
    
    def __init__(self):
        self._wallets: dict[str, CommerceSkill] = {}
        
    def get_wallet(self, agent_id: str) -> CommerceSkill:
        """Get or create wallet for agent."""
        if agent_id not in self._wallets:
            self._wallets[agent_id] = CommerceSkill(agent_id)
        return self._wallets[agent_id]
    
    def get_total_daily_spend(self) -> float:
        """Get total daily spend across all agents."""
        return sum(w._daily_spend for w in self._wallets.values())


if __name__ == "__main__":
    # Demo
    manager = CommerceManager()
    wallet = manager.get_wallet("chimera-001")
    
    # Check balance
    result = wallet.execute(action="get_balance")
    print(result.model_dump_json(indent=2))
    
    # Attempt transfer
    result = wallet.execute(
        action="transfer",
        to_address="0x123...",
        amount=5.0
    )
    print(result.model_dump_json(indent=2))
