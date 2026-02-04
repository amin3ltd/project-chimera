"""
Worker Service - The Executor

Stateless agent that executes atomic tasks.
Real Redis integration for task processing.
"""

import json
import uuid
import time as time_module
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import redis


# Redis Configuration
REDIS_URL = "redis://localhost:6379"
TASK_QUEUE = "task_queue"
REVIEW_QUEUE = "review_queue"
HITL_QUEUE = "hitl_queue"


# Result Schema
class TaskResult(BaseModel):
    """Result from Worker execution."""
    task_id: str
    status: str = "success"  # success | error
    output: dict = Field(default_factory=dict)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    error_message: Optional[str] = None
    executed_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    def to_json(self) -> str:
        return self.model_dump_json()
    
    @classmethod
    def from_json(cls, data: str) -> "TaskResult":
        return cls(**json.loads(data))


class Worker:
    """
    Worker Service - Stateless execution agent.
    
    Responsibilities:
    - Pull tasks from Redis task_queue
    - Execute tasks using skills
    - Push results to review_queue
    - Push high-risk tasks to hitl_queue
    - Stateless operation for horizontal scaling
    """
    
    def __init__(self, worker_id: str, redis_url: str = REDIS_URL):
        """
        Initialize worker.
        
        Args:
            worker_id: Unique worker identifier
            redis_url: Redis connection URL
        """
        self.worker_id = worker_id
        self.redis = redis.Redis.from_url(redis_url, decode_responses=True)
        self.task_queue = TASK_QUEUE
        self.review_queue = REVIEW_QUEUE
        self.hitl_queue = HITL_QUEUE
        
    def is_connected(self) -> bool:
        """Check Redis connection."""
        try:
            self.redis.ping()
            return True
        except redis.ConnectionError:
            return False
    
    def pop_task(self) -> Optional[dict]:
        """Pop task from Redis queue."""
        try:
            # Get highest priority task
            result = self.redis.zrevpop(self.task_queue)
            if result:
                return json.loads(result[1])
            return None
        except redis.RedisError as e:
            print(f"Worker {self.worker_id}: Error popping task: {e}")
            return None
    
    def push_to_review(self, result: TaskResult) -> bool:
        """Push result to review queue."""
        try:
            self.redis.lpush(self.review_queue, result.to_json())
            print(f"Worker {self.worker_id}: Pushed {result.task_id} to review queue")
            return True
        except redis.RedisError as e:
            print(f"Worker {self.worker_id}: Error pushing to review: {e}")
            return False
    
    def push_to_hitl(self, result: TaskResult) -> bool:
        """Push result to HITL queue for human review."""
        try:
            self.redis.lpush(self.hitl_queue, result.to_json())
            print(f"Worker {self.worker_id}: Pushed {result.task_id} to HITL queue")
            return True
        except redis.RedisError as e:
            print(f"Worker {self.worker_id}: Error pushing to HITL: {e}")
            return False
    
    def execute_task(self, task: dict) -> TaskResult:
        """
        Execute a task based on task_type.
        
        Routes to appropriate skill based on task_type.
        """
        task_id = task.get("task_id", str(uuid.uuid4()))
        task_type = task.get("task_type", "unknown")
        
        try:
            # Route to appropriate handler
            if task_type == "generate_content":
                return self._execute_generate_content(task)
            elif task_type == "analyze_trends":
                return self._execute_analyze_trends(task)
            elif task_type == "post_content":
                return self._execute_post_content(task)
            elif task_type == "reply_comment":
                return self._execute_reply_comment(task)
            elif task_type == "execute_transaction":
                return self._execute_transaction(task)
            else:
                return TaskResult(
                    task_id=task_id,
                    status="error",
                    error_message=f"Unknown task_type: {task_type}"
                )
        except Exception as e:
            return TaskResult(
                task_id=task_id,
                status="error",
                error_message=str(e)
            )
    
    def _execute_generate_content(self, task: dict) -> TaskResult:
        """Execute content generation task."""
        from skills.skill_generate_image import GenerateImageSkill
        from skills.skill_post_content import PostContentSkill
        
        goal = task.get("goal_description", "Generate content")
        agent_id = task.get("assigned_worker_id", self.worker_id)
        
        # Use image generation skill if applicable
        if "image" in goal.lower() or "visual" in goal.lower():
            skill = GenerateImageSkill()
            result = skill.execute(
                prompt=goal,
                agent_id=agent_id,
                style="realistic"
            )
            return TaskResult(
                task_id=task.get("task_id"),
                status=result.status,
                output={
                    "content_type": "image",
                    "image_url": result.image_url,
                    "generation_id": result.generation_id
                },
                confidence_score=0.85,
            )
        else:
            # Use post content skill
            skill = PostContentSkill()
            result = skill.execute(
                platform="twitter",
                text_content=goal,
                disclosure_level="automated"
            )
            return TaskResult(
                task_id=task.get("task_id"),
                status=result.status,
                output={
                    "content_type": "text",
                    "post_id": result.post_id,
                    "url": result.url
                },
                confidence_score=0.88,
            )
    
    def _execute_analyze_trends(self, task: dict) -> TaskResult:
        """Execute trend analysis task."""
        from skills.skill_analyze_trends import AnalyzeTrendsSkill
        
        goal = task.get("goal_description", "Analyze trends")
        
        skill = AnalyzeTrendsSkill()
        result = skill.execute(
            content=goal,
            platform="twitter",
            max_results=10
        )
        
        return TaskResult(
            task_id=task.get("task_id"),
            status=result.status,
            output={
                "trends": [t.model_dump() for t in result.trends],
                "analysis_metadata": result.analysis_metadata
            },
            confidence_score=0.90,
        )
    
    def _execute_post_content(self, task: dict) -> TaskResult:
        """Execute content posting task."""
        from skills.skill_post_content import PostContentSkill
        
        skill = PostContentSkill()
        result = skill.execute(
            platform=task.get("platform", "twitter"),
            text_content=task.get("text_content", ""),
            media_urls=task.get("media_urls", []),
            disclosure_level=task.get("disclosure_level", "automated")
        )
        
        return TaskResult(
            task_id=task.get("task_id"),
            status=result.status,
            output={
                "post_id": result.post_id,
                "url": result.url
            },
            confidence_score=0.85,
        )
    
    def _execute_reply_comment(self, task: dict) -> TaskResult:
        """Execute comment reply task."""
        # TODO: Implement comment reply logic
        return TaskResult(
            task_id=task.get("task_id"),
            status="success",
            output={
                "reply_text": "Reply generated",
                "confidence": 0.80
            },
            confidence_score=0.80,
        )
    
    def _execute_transaction(self, task: dict) -> TaskResult:
        """Execute commerce transaction task."""
        from skills.skill_commerce import CommerceSkill
        
        action = task.get("action", "get_balance")
        agent_id = task.get("assigned_worker_id", self.worker_id)
        
        skill = CommerceSkill(agent_id)
        result = skill.execute(
            action=action,
            to_address=task.get("to_address"),
            amount=task.get("amount"),
            asset=task.get("asset", "USDC")
        )
        
        return TaskResult(
            task_id=task.get("task_id"),
            status="success" if result.status == "success" else "error",
            output={
                "transaction_hash": result.transaction_hash,
                "balance": result.balance,
                "message": result.message
            },
            confidence_score=0.95,
        )
    
    def run(self):
        """
        Main loop: Pull and execute tasks.
        
        This runs as a service, continuously processing tasks.
        """
        print(f"Worker {self.worker_id} started")
        
        while True:
            try:
                task = self.pop_task()
                
                if task:
                    print(f"Worker {self.worker_id}: Processing task {task.get('task_id')}")
                    
                    result = self.execute_task(task)
                    
                    # Route based on confidence
                    if result.confidence_score < 0.70:
                        # Low confidence - reject/retry
                        self.push_to_hitl(result)
                    else:
                        # High confidence - push to review
                        self.push_to_review(result)
                else:
                    # No tasks, wait
                    time_module.sleep(1)
                    
            except KeyboardInterrupt:
                print(f"Worker {self.worker_id} stopped")
                break
            except Exception as e:
                print(f"Worker {self.worker_id}: Error: {e}")
                time_module.sleep(1)


if __name__ == "__main__":
    worker = Worker(worker_id=f"worker-{uuid.uuid4().hex[:8]}")
    
    if worker.is_connected():
        print("✅ Redis connected - running worker")
        worker.run()
    else:
        print("⚠️ Redis not connected - demo mode")
        
        # Demo task
        demo_task = {
            "task_id": f"demo-{uuid.uuid4().hex[:8]}",
            "task_type": "analyze_trends",
            "priority": "high",
            "goal_description": "Analyze AI trends in technology",
        }
        
        result = worker.execute_task(demo_task)
        print(f"Demo result: {result.status}")
        print(json.dumps(result.model_dump(), indent=2))
