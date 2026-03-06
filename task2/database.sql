CREATE TABLE call_records (
    id SERIAL PRIMARY KEY,
    customer_phone VARCHAR(20) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    transcript TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    intent_type VARCHAR(100),
    outcome VARCHAR(20) NOT NULL,
    confidence NUMERIC(3,2) NOT NULL,
    csat_score INTEGER,
    duration INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CHECK (confidence >= 0 AND confidence <= 1),
    CHECK (csat_score BETWEEN 1 AND 5 OR csat_score IS NULL)
);

-- Index to quickly find records by phone
CREATE INDEX idx_phone ON call_records(customer_phone);

-- Index to quickly fetch recent calls
CREATE INDEX idx_created_at ON call_records(created_at DESC);

-- Index for analytics by intent type
CREATE INDEX idx_intent ON call_records(intent_type);