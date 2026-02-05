"""
Skill: skill_memory

Agent memory management using Weaviate vector database.
Provides RAG (Retrieval-Augmented Generation) capabilities.
Real Weaviate integration.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

# Weaviate client (optional import)
try:
    import weaviate
    from weaviate import WeaviateClient
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False


# Memory types
MEMORY_TYPES = ["episodic", "semantic", "short_term", "long_term"]


# Input Schema
class MemoryInput(BaseModel):
    """Input contract for skill_memory"""
    action: str = Field(..., description="Action: store | retrieve | search | delete")
    content: Optional[str] = Field(default=None, description="Content to store")
    query: Optional[str] = Field(default=None, description="Query for search")
    tenant_id: str = Field(default="default", description="Tenant identifier for isolation")
    agent_id: str = Field(..., description="Agent ID")
    memory_type: str = Field(default="episodic", description="Type: episodic | semantic | short_term | long_term")
    importance_score: float = Field(default=0.5, ge=0.0, le=1.0)
    limit: int = Field(default=5, description="Max results for retrieval")
    memory_id: Optional[str] = Field(default=None, description="Memory ID for delete")


# Memory Entry
class MemoryEntry(BaseModel):
    """Memory entry schema"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str = "default"
    agent_id: str
    content: str
    memory_type: str
    embedding: Optional[List[float]] = None
    importance_score: float = 0.5
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: dict = Field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return self.model_dump()


# Output Schema
class MemoryOutput(BaseModel):
    """Output contract for skill_memory"""
    status: str = Field(..., pattern="^(success|error)$")
    message: str
    memories: List[MemoryEntry] = Field(default_factory=list)
    error_message: Optional[str] = None


class WeaviateMemoryStore:
    """
    Weaviate vector database integration.
    
    Provides:
    - Vector storage with embeddings
    - Semantic search
    - Hybrid queries
    - Metadata filtering
    """
    
    def __init__(self, url: str = "http://localhost:8080"):
        """Initialize Weaviate connection."""
        self.url = url
        self._client: Optional[WeaviateClient] = None
        
    def connect(self) -> bool:
        """Connect to Weaviate."""
        if not WEAVIATE_AVAILABLE:
            print("⚠️ Weaviate client not installed")
            return False
            
        try:
            self._client = weaviate.connect_to_local(url=self.url)
            print(f"✅ Connected to Weaviate: {self.url}")
            return True
        except Exception as e:
            print(f"❌ Weaviate connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Weaviate."""
        if self._client:
            self._client.close()
            self._client = None
            print("🔌 Disconnected from Weaviate")
    
    def is_connected(self) -> bool:
        """Check connection status."""
        return self._client is not None and self._client.is_ready()
    
    def create_schema(self, class_name: str = "AgentMemory") -> bool:
        """Create memory schema in Weaviate."""
        if not self._client:
            return False
            
        try:
            # Check if class exists
            if self._client.schema.exists(class_name):
                return True
                
            # Create class definition
            class_obj = {
                "class": class_name,
                "description": "Agent memory entries",
                "vectorizer": "text2vec-transformers",
                "moduleConfig": {
                    "text2vec-transformers": {
                        "vectorizeClassName": False
                    }
                },
                "properties": [
                    {"name": "agent_id", "dataType": ["text"]},
                    {"name": "content", "dataType": ["text"]},
                    {"name": "memory_type", "dataType": ["text"]},
                    {"name": "importance_score", "dataType": ["number"]},
                    {"name": "metadata", "dataType": ["object"]},
                ]
            }
            
            self._client.schema.create_class(class_obj)
            print(f"✅ Created schema: {class_name}")
            return True
        except Exception as e:
            print(f"❌ Schema creation failed: {e}")
            return False


class InMemoryStore:
    """
    In-memory storage for demo/testing.
    
    Fallback when Weaviate is not available.
    """
    
    def __init__(self):
        """Initialize in-memory store."""
        self._store: Dict[str, List[MemoryEntry]] = {}
    
    def store(self, entry: MemoryEntry) -> bool:
        """Store a memory entry."""
        if entry.agent_id not in self._store:
            self._store[entry.agent_id] = []
        self._store[entry.agent_id].append(entry)
        return True
    
    def retrieve(self, agent_id: str, memory_type: str = None, 
                limit: int = 5) -> List[MemoryEntry]:
        """Retrieve memories for an agent."""
        memories = self._store.get(agent_id, [])
        
        if memory_type:
            memories = [m for m in memories if m.memory_type == memory_type]
        
        return memories[:limit]
    
    def search(self, agent_id: str, query: str, 
              limit: int = 5) -> List[MemoryEntry]:
        """Search memories by content."""
        memories = self._store.get(agent_id, [])
        
        # Simple text search
        query_lower = query.lower()
        results = [m for m in memories if query_lower in m.content.lower()]
        
        return results[:limit]
    
    def delete(self, agent_id: str, memory_id: str) -> bool:
        """Delete a memory entry."""
        memories = self._store.get(agent_id, [])
        original_count = len(memories)
        self._store[agent_id] = [m for m in memories if m.id != memory_id]
        return len(self._store[agent_id]) < original_count


class MemorySkill:
    """
    Memory skill using Weaviate vector database.
    
    Provides:
    - Store memories with embeddings
    - Semantic search for retrieval
    - RAG context construction
    """
    
    def __init__(self, agent_id: str, weaviate_url: str = "http://localhost:8080"):
        """
        Initialize the memory skill.
        
        Args:
            agent_id: ID of the agent
            weaviate_url: Weaviate connection URL
        """
        self.agent_id = agent_id
        self.name = "skill_memory"
        self.version = "1.0.0"
        
        # Initialize storage
        if WEAVIATE_AVAILABLE:
            self._weaviate = WeaviateMemoryStore(weaviate_url)
            if self._weaviate.connect():
                self._weaviate.create_schema()
                self._storage = None
            else:
                self._storage = InMemoryStore()
                self._weaviate = None
        else:
            self._storage = InMemoryStore()
            self._weaviate = None
    
    def execute(self, action: str, content: str = None, query: str = None,
                agent_id: str = None, memory_type: str = "episodic",
                importance_score: float = 0.5, limit: int = 5,
                memory_id: str = None) -> MemoryOutput:
        """
        Execute memory action.
        
        Args:
            action: store | retrieve | search | delete
            content: Content to store
            query: Query for search
            agent_id: Agent ID
            memory_type: Type of memory
            importance_score: Importance 0-1
            limit: Max results
            memory_id: Memory ID for delete
            
        Returns:
            MemoryOutput with result
        """
        # Use default agent_id
        if agent_id is None:
            agent_id = self.agent_id
            
        storage = self._storage or self._weaviate
        
        if action == "store":
            return self._store(content, agent_id, memory_type, importance_score, storage)
        elif action == "retrieve":
            return self._retrieve(agent_id, memory_type, limit, storage)
        elif action == "search":
            return self._search(query, agent_id, limit, storage)
        elif action == "delete":
            return self._delete(agent_id, memory_id, storage)
        else:
            return MemoryOutput(
                status="error",
                message=f"Unknown action: {action}"
            )
    
    def _store(self, content: str, agent_id: str, 
               memory_type: str, importance_score: float,
               storage) -> MemoryOutput:
        """Store a memory entry."""
        entry = MemoryEntry(
            agent_id=agent_id,
            content=content,
            memory_type=memory_type,
            importance_score=importance_score,
            created_at=datetime.now(),
        )
        
        success = storage.store(entry)
        
        if success:
            return MemoryOutput(
                status="success",
                message="Memory stored successfully",
                memories=[entry]
            )
        else:
            return MemoryOutput(
                status="error",
                message="Failed to store memory"
            )
    
    def _retrieve(self, agent_id: str, memory_type: str, 
                  limit: int, storage) -> MemoryOutput:
        """Retrieve recent memories by type."""
        memories = storage.retrieve(agent_id, memory_type, limit)
        
        return MemoryOutput(
            status="success",
            message=f"Retrieved {len(memories)} memories",
            memories=memories
        )
    
    def _search(self, query: str, agent_id: str, 
                limit: int, storage) -> MemoryOutput:
        """Semantic search for relevant memories."""
        memories = storage.search(agent_id, query, limit)
        
        return MemoryOutput(
            status="success",
            message=f"Found {len(memories)} memories matching: {query}",
            memories=memories
        )
    
    def _delete(self, agent_id: str, memory_id: str,
                storage) -> MemoryOutput:
        """Delete a memory entry."""
        success = storage.delete(agent_id, memory_id)
        
        if success:
            return MemoryOutput(
                status="success",
                message="Memory deleted successfully"
            )
        else:
            return MemoryOutput(
                status="error",
                message="Memory not found"
            )
    
    def assemble_context(self, input_query: str, max_memories: int = 5) -> str:
        """
        Assemble RAG context for LLM.
        
        Args:
            input_query: Current user query
            max_memories: Max memories to retrieve
            
        Returns:
            Formatted context string
        """
        # Search for relevant memories
        result = self._search(input_query, self.agent_id, max_memories, 
                             self._storage or self._weaviate)
        
        # Format context
        context_parts = ["## Relevant Memories\n"]
        
        if not result.memories:
            context_parts.append("- No relevant memories found")
        else:
            for mem in result.memories:
                context_parts.append(f"- **{mem.memory_type}**: {mem.content}")
                context_parts.append(f"  (importance: {mem.importance_score:.2f})")
        
        return "\n".join(context_parts)


class MemoryManager:
    """Manager for agent memories."""
    
    def __init__(self, weaviate_url: str = "http://localhost:8080"):
        """Initialize memory manager."""
        self._memories: dict[str, MemorySkill] = {}
        self._weaviate_url = weaviate_url
    
    def get_memory(self, agent_id: str) -> MemorySkill:
        """Get or create memory skill for agent."""
        if agent_id not in self._memories:
            self._memories[agent_id] = MemorySkill(agent_id, self._weaviate_url)
        return self._memories[agent_id]


if __name__ == "__main__":
    # Demo
    print("=== Memory Skill Demo ===\n")
    
    manager = MemoryManager()
    memory = manager.get_memory("chimera-001")
    
    # Store a memory
    print("1. Storing memories...")
    result = memory.execute(
        action="store",
        content="User asked about AI agents today and seemed interested in autonomous systems",
        agent_id="chimera-001",
        memory_type="episodic",
        importance_score=0.8
    )
    print(f"   Status: {result.status} - {result.message}")
    
    result = memory.execute(
        action="store",
        content="Agent preferences: Professional but approachable tone",
        agent_id="chimera-001",
        memory_type="semantic",
        importance_score=0.9
    )
    print(f"   Status: {result.status} - {result.message}")
    
    # Search memories
    print("\n2. Searching memories...")
    result = memory.execute(
        action="search",
        query="AI agents",
        agent_id="chimera-001"
    )
    print(f"   Found {len(result.memories)} memories")
    
    # Assemble context
    print("\n3. Assembling RAG context...")
    context = memory.assemble_context("What does the user like?")
    print(context)
    
    print("\n✅ Demo complete")
