-- Project Chimera - PostgreSQL Schema
-- Database: project_chimera
-- Purpose: Store agents, campaigns, tasks, and audit logs

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- AGENTS
-- ============================================
CREATE TABLE agents (
    agent_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name VARCHAR(255) NOT NULL,
    agent_type VARCHAR(50) DEFAULT 'influencer',
    status VARCHAR(20) DEFAULT 'offline', -- online, busy, paused, offline
    wallet_address VARCHAR(42),
    wallet_network VARCHAR(50) DEFAULT 'base',
    current_budget DECIMAL(18, 8) DEFAULT 0,
    daily_spend_limit DECIMAL(18, 8) DEFAULT 50.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent Persona (JSON-based)
CREATE TABLE agent_personas (
    persona_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(agent_id) ON DELETE CASCADE,
    backstory TEXT,
    voice_traits JSONB DEFAULT '[]',
    core_beliefs JSONB DEFAULT '[]',
    directives JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- CAMPAIGNS
-- ============================================
CREATE TABLE campaigns (
    campaign_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_name VARCHAR(255) NOT NULL,
    description TEXT,
    goals JSONB DEFAULT '[]', -- Array of goal descriptions
    budget_limit DECIMAL(18, 8) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'draft', -- draft, active, paused, completed
    start_date DATE,
    end_date DATE,
    owner_id UUID, -- FK to agents or external users
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- TASKS
-- ============================================
CREATE TABLE tasks (
    task_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_type VARCHAR(50) NOT NULL, -- generate_content, analyze_trends, etc.
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(30) DEFAULT 'pending', -- pending, assigned, in_progress, review, complete, failed
    
    -- Task details
    goal_description TEXT,
    context JSONB DEFAULT '{}',
    required_resources JSONB DEFAULT '[]',
    persona_constraints JSONB DEFAULT '[]',
    
    -- Assignment
    campaign_id UUID REFERENCES campaigns(campaign_id),
    agent_id UUID REFERENCES agents(agent_id),
    assigned_worker_id VARCHAR(100),
    
    -- Results
    output JSONB DEFAULT '{}',
    confidence_score DECIMAL(5, 4),
    error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Task Queue (for processing)
CREATE TABLE task_queue (
    queue_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID REFERENCES tasks(task_id) ON DELETE CASCADE,
    priority INTEGER DEFAULT 2, -- 1=low, 2=medium, 3=high
    queued_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- ============================================
-- CONTENT
-- ============================================
CREATE TABLE content (
    content_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(agent_id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(campaign_id),
    task_id UUID REFERENCES tasks(task_id),
    
    -- Content details
    content_type VARCHAR(50), -- text, image, video
    platform VARCHAR(50), -- twitter, instagram, tiktok
    text_content TEXT,
    media_urls JSONB DEFAULT '[]',
    
    -- Publishing
    published BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMP WITH TIME ZONE,
    platform_post_id VARCHAR(255),
    platform_url VARCHAR(500),
    
    -- Metrics
    engagement_metrics JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- MEMORIES (for RAG)
-- ============================================
CREATE TABLE memories (
    memory_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(agent_id) ON DELETE CASCADE,
    memory_type VARCHAR(50), -- episodic, semantic, short_term, long_term
    
    -- Content
    content TEXT NOT NULL,
    embedding VECTOR(1536), -- OpenAI/v4 embedding dimension
    
    -- Metadata
    importance_score DECIMAL(5, 4) DEFAULT 0.5,
    metadata JSONB DEFAULT '{}',
    source VARCHAR(100),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Index for semantic search
CREATE INDEX idx_memories_embedding 
ON memories USING ivfflat (embedding vector_cosine_ops) 
WHERE memory_type = 'semantic';

-- ============================================
-- AUDIT LOGS
-- ============================================
CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50), -- agent, campaign, task, content
    entity_id UUID,
    action VARCHAR(100), -- create, update, publish, etc.
    actor VARCHAR(100), -- system, agent_id, human_operator
    details JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- FINANCIAL TRANSACTIONS
-- ============================================
CREATE TABLE transactions (
    transaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(agent_id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(campaign_id),
    
    -- Transaction details
    action_type VARCHAR(50), -- transfer, receive, deploy_token
    asset VARCHAR(20), -- USDC, ETH, etc.
    amount DECIMAL(18, 8),
    to_address VARCHAR(42),
    from_address VARCHAR(42),
    
    -- Blockchain data
    transaction_hash VARCHAR(66),
    block_number BIGINT,
    network VARCHAR(50) DEFAULT 'base',
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- pending, confirmed, failed
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    confirmed_at TIMESTAMP WITH TIME ZONE
);

-- ============================================
-- HITL QUEUE
-- ============================================
CREATE TABLE hitl_queue (
    queue_item_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID REFERENCES tasks(task_id),
    agent_id UUID REFERENCES agents(agent_id),
    
    -- Content for review
    content JSONB NOT NULL,
    confidence_score DECIMAL(5, 4),
    escalation_reason TEXT,
    
    -- Review status
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected
    reviewer_id VARCHAR(100),
    reviewer_comment TEXT,
    
    -- Timestamps
    queued_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reviewed_at TIMESTAMP WITH TIME ZONE
);

-- ============================================
-- INDEXES
-- ============================================
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_campaign ON tasks(campaign_id);
CREATE INDEX idx_tasks_agent ON tasks(agent_id);
CREATE INDEX idx_content_agent ON content(agent_id);
CREATE INDEX idx_content_published ON content(published, published_at);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_transactions_agent ON transactions(agent_id, created_at);
CREATE INDEX idx_logs_created ON audit_logs(created_at DESC);

-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER update_agents_timestamp 
BEFORE UPDATE ON agents FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_campaigns_timestamp 
BEFORE UPDATE ON campaigns FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_content_timestamp 
BEFORE UPDATE ON content FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER update_personas_timestamp 
BEFORE UPDATE ON agent_personas FOR EACH ROW EXECUTE FUNCTION update_updated_at();
