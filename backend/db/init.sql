-- ExamGuard AI — Database initialisation
-- Auto-runs when Postgres container first starts

CREATE TABLE IF NOT EXISTS sessions (
    id              VARCHAR(64) PRIMARY KEY,
    student_id      VARCHAR(64) NOT NULL,
    exam_id         VARCHAR(64) NOT NULL,
    started_at      TIMESTAMP DEFAULT NOW(),
    ended_at        TIMESTAMP,
    integrity_score INTEGER DEFAULT 100,
    verdict         VARCHAR(20) DEFAULT 'CLEAR',
    is_active       BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS incidents (
    id              SERIAL PRIMARY KEY,
    session_id      VARCHAR(64) REFERENCES sessions(id),
    timestamp       TIMESTAMP DEFAULT NOW(),
    integrity_score INTEGER,
    verdict         VARCHAR(20),
    reasoning       TEXT,
    triggered_by    JSONB DEFAULT '[]',
    report_url      VARCHAR(512)
);

CREATE TABLE IF NOT EXISTS audit_events (
    id          SERIAL PRIMARY KEY,
    session_id  VARCHAR(64) REFERENCES sessions(id),
    timestamp   TIMESTAMP DEFAULT NOW(),
    event_type  VARCHAR(50),
    severity    VARCHAR(10),
    confidence  FLOAT,
    description TEXT,
    metadata    JSONB DEFAULT '{}',
    frame_b64   TEXT
);

-- Demo session so dashboard isn't empty for judges
INSERT INTO sessions (id, student_id, exam_id, integrity_score, verdict, is_active)
VALUES ('demo_session_001', 'STUDENT_001', 'CS301_MidSem', 100, 'CLEAR', TRUE)
ON CONFLICT DO NOTHING;
