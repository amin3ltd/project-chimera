"""
Planner Service - The Strategist

Decomposes high-level goals into executable tasks.
"""

import json
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import redis


# Task Schema
class Task(BaseModel):
    """Task schema for Planner -> Worker handoff."""
    task_id: str
    task_type: str  # generate_content | reply_comment | execute_transaction
    priority: str  # high | medium | low
    goal_description: str
    persona_constraints: list[str] = Field(default_factory=list)
    required_resources: list[str] = Field(default_factory=list)
    assigned_worker_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    status: str = "pending"


class GlobalState(BaseModel):
    """Global state containing campaign goals."""
    campaign_id: str
    goals: list[str]
    budget_limit: float
    status: str = "active"  # active | paused | completed
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class Planner:
    """
    Planner Service - Strategic thinking agent.
    
    Responsibilities:
    - Monitor GlobalState for campaign goals
    - Decompose goals into atomic tasks
    - Push tasks to Redis task_queue
    - Dynamic re-planning on context changes
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """Initialize planner."""
        self.redis = redis.Redis.from_url(redis_url)
        self.queue_name = "task_queue"
        
    def read_global_state(self, campaign_id: str) -> Optional[GlobalState]:
        """Read current campaign state from Redis."""
        data = self.redis.hget(f"campaign:{campaign_id}", "state")
        if data:
            return GlobalState(**json.loads(data))
        return None
    
    def decompose_goal(self, goal: str) -> list[dict]:
        """
        Decompose a goal into subtasks.
        
        TODO: Use LLM for intelligent decomposition
        """
        # Placeholder: Return structured tasks
        return [
            {
                "task_type": "analyze_trends",
                "priority": "high",
                "goal_description": f"Analyze trends for: {goal}",
            },
            {
                "task_type": "generate_content",
                "priority": "medium", 
                "goal_description": f"Generate content about: {goal}",
            },
        ]
    
    def create_task(self, task_data: dict, campaign_id: str) -> Task:
        """Create a Task object."""
        import uuid
        return Task(
            task_id=str(uuid.uuid4()),
            campaign_id=campaign_id,
            **task_data
        )
    
    def push_task(self, task: Task):
        """Push task to Redis queue."""
        self.redis.lpush(self.queue_name, task.model_dump_json())
    
    def run(self, campaign_id: str):
        """
        Main loop: Monitor campaign and create tasks.
        
        This would run as a service, polling for new goals.
        """
        while True:
            state = self.read_global_state(campaign_id)
            if state and state.status == "active":
                for goal in state.goals:
                    subtasks = self.decompose_goal(goal)
                    for task_data in subtasks:
                        task = self.create_task(task_data, campaign_id)
                        self.push_task(task)
            # Sleep before next check
            # time.sleep(5)


if __name__ == "__main__":
    planner = Planner()
    
    # Demo: Create a task
    task = Task(
        task_id="task_001",
        task_type="generate_content",
        priority="high",
        goal_description="Create post about AI trends",
        persona_constraints=["professional", "engaging"],
        required_resources=["news://ai/trends"],
    )
    
    print(task.model_dump_json(indent=2))
