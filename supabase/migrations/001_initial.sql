-- SkillBridge AI Initial Supabase Migration
-- Enable UUID and pgvector extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Profiles Table
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users ON DELETE CASCADE,
    email TEXT,
    target_skill_goal TEXT,
    preferred_provider TEXT DEFAULT 'gemini',
    learning_style TEXT DEFAULT 'practical',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Documents Table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    file_type TEXT DEFAULT 'pdf',
    file_size INT,
    storage_path TEXT,
    extracted_text TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Document Chunks Table with Full-Text Search
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    page_number INT,
    tsv TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS chunks_tsv_idx ON document_chunks USING GIN(tsv);
CREATE INDEX IF NOT EXISTS chunks_doc_idx ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS chunks_user_idx ON document_chunks(user_id);

-- 4. Chat Sessions Table
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    title TEXT DEFAULT 'New Learning Session',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Chat Messages Table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    role TEXT CHECK (role IN ('user', 'assistant', 'system')) NOT NULL,
    content TEXT NOT NULL,
    command_used TEXT,
    cited_chunk_ids JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS messages_session_idx ON messages(session_id);

-- 6. User Topic Progress (Direct Supabase-based progress tracking)
CREATE TABLE IF NOT EXISTS user_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    topic_name TEXT NOT NULL,
    status TEXT DEFAULT 'in_progress' CHECK (status IN ('not_started', 'in_progress', 'completed')),
    quizzes_taken INT DEFAULT 0,
    best_score FLOAT DEFAULT 0.0,
    last_studied_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, topic_name)
);

CREATE INDEX IF NOT EXISTS progress_user_topic_idx ON user_progress(user_id, topic_name);

-- 7. Quiz Attempts Table
CREATE TABLE IF NOT EXISTS quiz_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
    topic TEXT NOT NULL,
    score INT NOT NULL,
    total_questions INT NOT NULL,
    percentage FLOAT GENERATED ALWAYS AS ((score::FLOAT / NULLIF(total_questions, 0)) * 100.0) STORED,
    answers_json JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS quiz_user_topic_idx ON quiz_attempts(user_id, topic);

-- 8. Daily Study Activity (Streak Tracking)
CREATE TABLE IF NOT EXISTS daily_activity (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    activity_date DATE DEFAULT CURRENT_DATE,
    actions_count INT DEFAULT 1,
    UNIQUE(user_id, activity_date)
);

CREATE INDEX IF NOT EXISTS daily_activity_user_date ON daily_activity(user_id, activity_date);

-- Enable Row Level Security (RLS) on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_attempts ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_activity ENABLE ROW LEVEL SECURITY;

-- Default RLS Policies
CREATE POLICY "Users can access their own profile" ON profiles 
    FOR ALL USING (auth.uid() = id);

CREATE POLICY "Users can access their own documents" ON documents 
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can access their own document chunks" ON document_chunks 
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can access their own sessions" ON sessions 
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can access messages for their sessions" ON messages 
    FOR ALL USING (
        EXISTS (SELECT 1 FROM sessions WHERE sessions.id = messages.session_id AND sessions.user_id = auth.uid())
    );

CREATE POLICY "Users can access their own progress" ON user_progress 
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can access their own quiz attempts" ON quiz_attempts 
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can access their own daily activity" ON daily_activity 
    FOR ALL USING (auth.uid() = user_id);

