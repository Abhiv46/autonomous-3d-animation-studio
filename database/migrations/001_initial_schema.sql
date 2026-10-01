-- Autonomous AI Content Operations Engine
-- Schema Migration 001: Core Content Operations & Registry

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS accounts (
    id TEXT PRIMARY KEY,
    slot_index INTEGER UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    tier TEXT NOT NULL CHECK(tier IN ('FREE', 'PRO', 'ENTERPRISE')),
    project_id TEXT,
    project_name TEXT,
    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE', 'COOLDOWN', 'ERROR', 'AUTHENTICATION_REQUIRED', 'DISABLED')),
    available_credits INTEGER DEFAULT 50,
    last_credit_check TIMESTAMP,
    last_used TIMESTAMP,
    cooldown_until TIMESTAMP,
    consecutive_errors INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS characters (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    age INTEGER,
    appearance_description TEXT NOT NULL,
    locked_clothing TEXT NOT NULL,
    voice_description TEXT,
    is_locked BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stories (
    id TEXT PRIMARY KEY, -- Format: TND-YYYY-XXXXXX
    title TEXT NOT NULL,
    concept_summary TEXT NOT NULL,
    structure_type TEXT NOT NULL, -- e.g. PROBLEM_ESCALATION_PAYOFF, MYSTERY_REVEAL
    story_hash TEXT UNIQUE NOT NULL,
    total_parts INTEGER NOT NULL DEFAULT 3,
    target_duration_seconds INTEGER DEFAULT 60,
    state TEXT NOT NULL DEFAULT 'QUEUED' CHECK(state IN (
        'QUEUED', 'GENERATING', 'PARTIAL', 'WAITING_FOR_CREDITS', 
        'WAITING_FOR_ACCOUNT', 'RETRY_REQUIRED', 'COMPLETING', 
        'COMPLETED', 'QUALITY_CHECK', 'READY_TO_PUBLISH', 
        'PUBLISHED', 'FAILED', 'ABANDONED'
    )),
    priority INTEGER DEFAULT 2, -- P0=recovery, P1=scheduled, P2=standard, P3=experiment
    scorecard_score REAL DEFAULT 0.0,
    scorecard_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS story_parts (
    id TEXT PRIMARY KEY, -- Format: TND-YYYY-XXXXXX-P01
    story_id TEXT NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    part_number INTEGER NOT NULL,
    scene_label TEXT NOT NULL,
    prompt_text TEXT NOT NULL,
    prompt_hash TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'GENERATING', 'COMPLETED', 'FAILED')),
    assigned_account_id TEXT REFERENCES accounts(id),
    google_flow_project_id TEXT,
    raw_video_path TEXT,
    duration_seconds REAL DEFAULT 0.0,
    file_size_bytes INTEGER DEFAULT 0,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    generated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(story_id, part_number)
);

CREATE TABLE IF NOT EXISTS content_fingerprints (
    id TEXT PRIMARY KEY,
    story_id TEXT NOT NULL REFERENCES stories(id),
    prompt_hash TEXT NOT NULL,
    title_hash TEXT NOT NULL,
    semantic_signature TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS assets (
    id TEXT PRIMARY KEY,
    story_id TEXT NOT NULL REFERENCES stories(id),
    asset_type TEXT NOT NULL CHECK(asset_type IN ('RAW_PART', 'MERGED_SHORT', 'THUMBNAIL', 'LONG_COMPILATION', 'METADATA')),
    file_path TEXT NOT NULL UNIQUE,
    file_size_bytes INTEGER NOT NULL,
    checksum_sha256 TEXT NOT NULL,
    resolution TEXT,
    duration_seconds REAL,
    is_valid BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS publishing_jobs (
    id TEXT PRIMARY KEY,
    story_id TEXT NOT NULL REFERENCES stories(id),
    platform TEXT NOT NULL CHECK(platform IN ('YOUTUBE', 'TIKTOK', 'INSTAGRAM', 'FACEBOOK')),
    target_channel_id TEXT NOT NULL,
    scheduled_for TIMESTAMP,
    published_at TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'VALIDATED', 'IN_PROGRESS', 'PUBLISHED', 'FAILED', 'BLOCKED_POLICY')),
    platform_video_id TEXT,
    platform_url TEXT,
    title TEXT NOT NULL,
    description TEXT,
    tags TEXT,
    compliance_classification TEXT NOT NULL DEFAULT 'MADE_FOR_KIDS',
    human_approved BOOLEAN DEFAULT 0,
    error_log TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS system_errors (
    id TEXT PRIMARY KEY,
    component TEXT NOT NULL,
    error_type TEXT NOT NULL,
    severity TEXT NOT NULL CHECK(severity IN ('INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    message TEXT NOT NULL,
    stack_trace TEXT,
    story_id TEXT,
    account_id TEXT,
    screenshot_path TEXT,
    recovery_attempted TEXT,
    recovery_successful BOOLEAN DEFAULT 0,
    resolved BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS policy_checks (
    id TEXT PRIMARY KEY,
    policy_name TEXT NOT NULL,
    platform TEXT NOT NULL,
    last_verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'COMPLIANT',
    notes TEXT
);

CREATE TABLE IF NOT EXISTS analytics_snapshots (
    id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,
    platform_video_id TEXT NOT NULL,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    avg_view_duration_seconds REAL DEFAULT 0.0,
    completion_rate REAL DEFAULT 0.0,
    retention_score REAL DEFAULT 0.0,
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stories_state ON stories(state);
CREATE INDEX IF NOT EXISTS idx_stories_priority ON stories(priority);
CREATE INDEX IF NOT EXISTS idx_story_parts_status ON story_parts(status);
CREATE INDEX IF NOT EXISTS idx_fingerprints_hash ON content_fingerprints(prompt_hash);
CREATE INDEX IF NOT EXISTS idx_publishing_status ON publishing_jobs(status);
