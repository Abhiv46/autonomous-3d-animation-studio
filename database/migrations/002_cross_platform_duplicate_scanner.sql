CREATE TABLE IF NOT EXISTS platform_indexed_videos (
    id TEXT PRIMARY KEY,
    platform TEXT NOT NULL, -- 'YOUTUBE' or 'TIKTOK'
    title TEXT NOT NULL,
    normalized_title TEXT NOT NULL,
    keywords TEXT,
    source_type TEXT NOT NULL, -- 'CHANNEL_HISTORY', 'SCHEDULE_QUEUE', 'STUDIO_POSTED', 'API_SCAN'
    status TEXT NOT NULL DEFAULT 'PUBLISHED',
    video_url TEXT,
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_indexed_norm_title ON platform_indexed_videos(normalized_title);
CREATE INDEX IF NOT EXISTS idx_indexed_platform ON platform_indexed_videos(platform);
