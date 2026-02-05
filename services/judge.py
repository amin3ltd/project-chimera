"""
Judge Service - The Gatekeeper

Quality assurance and governance layer.
Real Redis integration for review processing and OCC.
"""

import json
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import redis

from services.tenancy import DEFAULT_TENANT_ID, RedisKeyspace


# Redis Configuration
REDIS_URL = "redis://localhost:6379"
GLOBAL_STATE_PREFIX = "campaign:"  # legacy; use RedisKeyspace for tenant scoping
OUTPUT_PREFIX = "output:"  # legacy; use RedisKeyspace for tenant scoping


# Confidence Thresholds (from SRS)
HIGH_CONFIDENCE = 0.90
MEDIUM_CONFIDENCE = 0.70
LOW_CONFIDENCE = 0.70

# Sensitive topics for mandatory escalation
SENSITIVE_TOPICS = [
    "politics",
    "health advice",
    "financial advice",
    "legal advice",
    "religion",
]


class JudgeDecision(BaseModel):
    """Judge decision on task result."""
    task_id: str
    tenant_id: str = Field(default=DEFAULT_TENANT_ID, description="Tenant identifier for isolation")
    decision: str  # approve | reject | escalate
    confidence_score: float
    reasoning: str
    requires_human_review: bool = False
    decided_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    def to_json(self) -> str:
        return self.model_dump_json()
    
    @classmethod
    def from_json(cls, data: str) -> "JudgeDecision":
        return cls(**json.loads(data))


class CommitResult(BaseModel):
    """Result of committing to global state."""
    success: bool
    state_version: int
    message: str


class Judge:
    """
    Judge Service - Quality control agent.
    
    Responsibilities:
    - Review Worker outputs
    - Validate against acceptance criteria
    - Enforce persona constraints
    - Escalate low confidence to HITL
    - Implement Optimistic Concurrency Control (OCC)
    """
    
    def __init__(self, redis_url: str = REDIS_URL, *, tenant_id: str = DEFAULT_TENANT_ID):
        """Initialize judge with Redis connection."""
        self.redis = redis.Redis.from_url(redis_url, decode_responses=True)
        self.keyspace = RedisKeyspace(tenant_id=tenant_id)
        self.review_queue = self.keyspace.review_queue()
        self.hitl_queue = self.keyspace.hitl_queue()
        
    def is_connected(self) -> bool:
        """Check Redis connection."""
        try:
            self.redis.ping()
            return True
        except redis.ConnectionError:
            return False
    
    def pop_review(self) -> Optional[dict]:
        """Pop result from review queue."""
        try:
            result = self.redis.rpop(self.review_queue)
            if result:
                return json.loads(result)
            return None
        except redis.RedisError as e:
            print(f"Judge: Error popping review: {e}")
            return None
    
    def pop_hitl(self) -> Optional[dict]:
        """Pop result from HITL queue."""
        try:
            result = self.redis.rpop(self.hitl_queue)
            if result:
                return json.loads(result)
            return None
        except redis.RedisError as e:
            print(f"Judge: Error popping HITL: {e}")
            return None
    
    def review(self, task_result: dict) -> JudgeDecision:
        """
        Review a task result and make a decision.
        
        Decision logic (from SRS):
        - > 0.90: Auto-approve
        - 0.70-0.90: Escalate to human
        - < 0.70: Reject with retry
        """
        task_id = task_result.get("task_id")
        confidence = task_result.get("confidence_score", 0.0)
        output = task_result.get("output", {})
        tenant_id = task_result.get("tenant_id", self.keyspace.tenant_id)
        
        # Check for sensitive content (mandatory escalation)
        if self._contains_sensitive_content(output):
            return JudgeDecision(
                task_id=task_id,
                tenant_id=tenant_id,
                decision="escalate",
                confidence_score=confidence,
                reasoning="Content contains sensitive topics - requires human review",
                requires_human_review=True,
            )
        
        # Confidence-based decision
        if confidence >= HIGH_CONFIDENCE:
            return JudgeDecision(
                task_id=task_id,
                tenant_id=tenant_id,
                decision="approve",
                confidence_score=confidence,
                reasoning=f"High confidence ({confidence}) - auto-approved",
            )
        elif confidence >= MEDIUM_CONFIDENCE:
            return JudgeDecision(
                task_id=task_id,
                tenant_id=tenant_id,
                decision="escalate",
                confidence_score=confidence,
                reasoning=f"Medium confidence ({confidence}) - human review required",
                requires_human_review=True,
            )
        else:
            return JudgeDecision(
                task_id=task_id,
                tenant_id=tenant_id,
                decision="reject",
                confidence_score=confidence,
                reasoning=f"Low confidence ({confidence}) - retry with refined prompt",
            )
    
    def _contains_sensitive_content(self, output: dict) -> bool:
        """
        Check for sensitive topics.
        
        Returns True if sensitive content detected.
        """
        content_str = str(output).lower()
        
        return any(topic in content_str for topic in SENSITIVE_TOPICS)
    
    def check_occ(self, campaign_id: str, expected_version: int) -> tuple[bool, int]:
        """
        Optimistic Concurrency Control check.
        
        Returns (is_valid, current_version).
        If is_valid is False, state has changed.
        """
        try:
            current_version = self.redis.hget(
                self.keyspace.campaign_key(campaign_id),
                self.keyspace.campaign_version_field()
            )
            current_version = int(current_version) if current_version else 0
            
            return current_version == expected_version, current_version
        except redis.RedisError as e:
            print(f"Judge OCC error: {e}")
            return False, 0
    
    def commit_result(self, task_result: dict, decision: JudgeDecision,
                      campaign_id: str) -> CommitResult:
        """
        Commit approved result to global state.
        
        Implements OCC to prevent race conditions.
        """
        try:
            # Check OCC
            task_version = task_result.get("state_version", 1)
            is_valid, current_version = self.check_occ(campaign_id, task_version)
            
            if not is_valid:
                return CommitResult(
                    success=False,
                    state_version=current_version,
                    message=f"OCC conflict - state changed from v{task_version} to v{current_version}"
                )
            
            # Store output
            output_key = self.keyspace.output_key(task_result.get("task_id"))
            self.redis.setex(
                output_key,
                86400,  # 24 hour TTL
                json.dumps({
                    "output": task_result.get("output"),
                    "decision": decision.decision,
                    "confidence": decision.confidence_score,
                    "committed_at": datetime.now().isoformat()
                })
            )
            
            # Update state version
            new_version = current_version + 1
            self.redis.hset(
                self.keyspace.campaign_key(campaign_id),
                self.keyspace.campaign_version_field(),
                str(new_version)
            )
            
            return CommitResult(
                success=True,
                state_version=new_version,
                message="Result committed successfully"
            )
            
        except redis.RedisError as e:
            return CommitResult(
                success=False,
                state_version=0,
                message=f"Redis error: {e}"
            )
    
    def push_to_hitl(self, task_result: dict) -> bool:
        """Push to HITL queue for human review."""
        try:
            self.redis.lpush(self.hitl_queue, json.dumps(task_result))
            return True
        except redis.RedisError as e:
            print(f"Judge: Error pushing to HITL: {e}")
            return False
    
    def apply_human_decision(self, task_id: str, decision: str,
                              reviewer_id: str) -> bool:
        """
        Apply human review decision to a task.
        
        Called when human approves/rejects from dashboard.
        """
        try:
            # Get task from HITL queue
            # This would need more sophisticated logic in production
            key = f"hitl_decision:{task_id}"
            self.redis.hset(key, mapping={
                "decision": decision,
                "reviewer_id": reviewer_id,
                "decided_at": datetime.now().isoformat()
            })
            self.redis.expire(key, 86400)  # 24 hour TTL
            return True
        except redis.RedisError as e:
            print(f"Judge: Error applying decision: {e}")
            return False
    
    def run(self):
        """
        Main loop: Review results from workers.
        
        This runs as a service, continuously processing results.
        """
        print("Judge service started")
        
        while True:
            try:
                # Check review queue
                result = self.pop_review()
                
                if result:
                    decision = self.review(result)
                    campaign_id = result.get("campaign_id", "default")
                    
                    if decision.decision == "approve":
                        commit = self.commit_result(result, decision, campaign_id)
                        print(f"Judge: {decision.decision} - {commit.message}")
                    elif decision.decision == "escalate":
                        self.push_to_hitl(result)
                        print(f"Judge: {decision.decision} - sent to HITL")
                    else:
                        print(f"Judge: {decision.decision} - {decision.reasoning}")
                else:
                    # No reviews, wait
                    import time
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print("Judge stopped")
                break
            except Exception as e:
                print(f"Judge error: {e}")
                import time
                time.sleep(1)


if __name__ == "__main__":
    judge = Judge()
    
    if judge.is_connected():
        print("✅ Redis connected - running judge")
        judge.run()
    else:
        print("⚠️ Redis not connected - demo mode")
        
        # Demo: Review a task result
        demo_result = {
            "task_id": f"demo-{uuid.uuid4().hex[:8]}",
            "status": "success",
            "output": {
                "content": "AI is transforming the world of technology!",
                "platform": "twitter"
            },
            "confidence_score": 0.92,
            "campaign_id": "demo"
        }
        
        decision = judge.review(demo_result)
        print(f"\nDemo decision: {decision.decision}")
        print(f"Reasoning: {decision.reasoning}")
        print(f"Confidence: {decision.confidence_score}")
