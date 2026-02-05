"""
Planner Service - The Strategist

Decomposes high-level goals into executable tasks.
Real Redis integration for task queuing.
"""

import json
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
import redis


# Redis Configuration
REDIS_URL = "redis://localhost:6379"
TASK_QUEUE = "task_queue"
GLOBAL_STATE_PREFIX = "campaign:"


# Task Schema
class Task(BaseModel):
    """Task schema for Planner → Worker handoff."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str  # generate_content | reply_comment | execute_transaction | analyze_trends
    priority: str = "medium"  # high | medium | low
    goal_description: str
    persona_constraints: list[str] = Field(default_factory=list)
    required_resources: list[str] = Field(default_factory=list)
    assigned_worker_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    status: str = "pending"  # pending | in_progress | review | complete
    campaign_id: Optional[str] = None
    
    def to_json(self) -> str:
        return self.model_dump_json()
    
    @classmethod
    def from_json(cls, data: str) -> "Task":
        return cls(**json.loads(data))


class GlobalState(BaseModel):
    """Global state containing campaign goals."""
    campaign_id: str
    goals: list[str] = Field(default_factory=list)
    budget_limit: float = 0.0
    status: str = "active"  # active | paused | completed
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    state_version: int = 1
    
    def to_json(self) -> str:
        return self.model_dump_json()
    
    @classmethod
    def from_json(cls, data: str) -> "GlobalState":
        return cls(**json.loads(data))


class Planner:
    """
    Planner Service - Strategic thinking agent.
    
    Responsibilities:
    - Monitor GlobalState for campaign goals
    - Decompose goals into atomic tasks
    - Push tasks to Redis task_queue
    - Dynamic re-planning on context changes
    """
    
    def __init__(self, redis_url: str = REDIS_URL):
        """Initialize planner with Redis connection."""
        self.redis = redis.Redis.from_url(redis_url, decode_responses=True)
        self.queue_name = TASK_QUEUE
        self.state_prefix = GLOBAL_STATE_PREFIX
        
    def is_connected(self) -> bool:
        """Check Redis connection."""
        try:
            self.redis.ping()
            return True
        except redis.ConnectionError:
            return False
    
    def read_global_state(self, campaign_id: str) -> Optional[GlobalState]:
        """Read current campaign state from Redis."""
        try:
            data = self.redis.hget(f"{self.state_prefix}{campaign_id}", "state")
            if data:
                return GlobalState.from_json(data)
            return None
        except redis.RedisError as e:
            print(f"Error reading global state: {e}")
            return None
    
    def write_global_state(self, state: GlobalState) -> bool:
        """Write campaign state to Redis."""
        try:
            state.updated_at = datetime.now().isoformat()
            state.state_version += 1
            self.redis.hset(
                f"{self.state_prefix}{state.campaign_id}",
                "state",
                state.to_json()
            )
            return True
        except redis.RedisError as e:
            print(f"Error writing global state: {e}")
            return False
    
    def decompose_goal(self, goal: str, campaign_id: str) -> List[Task]:
        """
        Decompose a goal into subtasks.
        
        Uses LLM-style decomposition based on goal type.
        """
        task_type_map = {
            "trend": "analyze_trends",
            "content": "generate_content",
            "post": "post_content",
            "engage": "reply_comment",
            "commerce": "execute_transaction",
        }
        
        goal_lower = goal.lower()
        
        # Determine task type based on goal content
        task_type = "generate_content"
        for key, task in task_type_map.items():
            if key in goal_lower:
                task_type = task
                break
        
        # Create subtasks based on complexity
        subtasks = []
        
        # Always add analysis task if trends are involved
        if "trend" in goal_lower or "research" in goal_lower:
            subtasks.append(Task(
                task_type="analyze_trends",
                priority="high",
                goal_description=f"Analyze trends for: {goal}",
                campaign_id=campaign_id,
            ))
        
        # Add content generation
        subtasks.append(Task(
            task_type=task_type,
            priority="medium",
            goal_description=goal,
            persona_constraints=["professional", "engaging"],
            required_resources=["news://trends/latest"],
            campaign_id=campaign_id,
        ))
        
        return subtasks
    
    def create_task(self, task_data: dict, campaign_id: str) -> Task:
        """Create a Task object."""
        return Task(
            campaign_id=campaign_id,
            **task_data
        )
    
    def push_task(self, task: Task) -> bool:
        """Push task to Redis queue with priority."""
        try:
            # Use Redis sorted set for priority queuing
            priority_score = {"high": 3, "medium": 2, "low": 1}[task.priority]
            
            self.redis.zadd(
                self.queue_name,
                {task.to_json(): priority_score}
            )
            print(f"Pushed task {task.task_id} to {self.queue_name}")
            return True
        except redis.RedisError as e:
            print(f"Error pushing task: {e}")
            return False
    
    def pop_task(self) -> Optional[Task]:
        """Pop highest priority task from queue."""
        try:
            # Get highest priority task (highest score first)
            result = self.redis.zpopmax(self.queue_name, count=1)
            if result:
                member, _score = result[0]
                return Task.from_json(member)
            return None
        except redis.RedisError as e:
            print(f"Error popping task: {e}")
            return None
    
    def run(self, campaign_id: str):
        """
        Main loop: Monitor campaign and create tasks.
        
        This runs as a service, polling for new goals.
        """
        print(f"Planner started for campaign: {campaign_id}")
        
        while True:
            try:
                state = self.read_global_state(campaign_id)
                
                if state and state.status == "active":
                    print(f"Processing campaign {campaign_id} with {len(state.goals)} goals")
                    
                    for goal in state.goals:
                        subtasks = self.decompose_goal(goal, campaign_id)
                        for task in subtasks:
                            self.push_task(task)
                            
                # Poll every 5 seconds
                self._sleep(5)
                
            except KeyboardInterrupt:
                print("Planner stopped")
                break
    
    def _sleep(self, seconds: float):
        """Sleep helper for testing."""
        import time
        time.sleep(seconds)


if __name__ == "__main__":
    # Demo with Redis
    planner = Planner()
    
    if planner.is_connected():
        print("✅ Redis connected successfully")
        
        # Create a sample campaign
        campaign = GlobalState(
            campaign_id="test-campaign-001",
            goals=["Research AI trends in Ethiopia", "Generate content about AI agents"],
            budget_limit=100.0
        )
        
        planner.write_global_state(campaign)
        
        # Decompose and push tasks
        tasks = planner.decompose_goal("Research AI trends in Ethiopia", campaign.campaign_id)
        for task in tasks:
            planner.push_task(task)
            
        print(f"✅ Created {len(tasks)} tasks")
        
    else:
        print("⚠️ Redis not connected - running in demo mode")
        
        # Demo without Redis
        demo_task = Task(
            task_type="analyze_trends",
            priority="high",
            goal_description="Analyze AI trends",
            campaign_id="demo",
        )
        print(f"Demo task created: {demo_task.task_id}")
