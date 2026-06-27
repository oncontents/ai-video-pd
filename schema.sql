CREATE TABLE IF NOT EXISTS job_postings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dedupe_key TEXT NOT NULL UNIQUE,
    source TEXT NOT NULL,
    organization TEXT NOT NULL,
    title TEXT NOT NULL,
    job_name TEXT,
    location TEXT,
    employment_type TEXT,
    deadline TEXT,
    posted_at TEXT,
    url TEXT NOT NULL,
    first_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sent_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_job_postings_deadline ON job_postings(deadline);
CREATE INDEX IF NOT EXISTS idx_job_postings_sent_at ON job_postings(sent_at);
CREATE INDEX IF NOT EXISTS idx_job_postings_source ON job_postings(source);
