-- Initialize the database with proper extensions and settings
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types
DO $$ BEGIN
    CREATE TYPE creaturetype AS ENUM ('PLAYER', 'ENEMY', 'ALLY', 'OTHER');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Ensure the database is properly configured
ALTER SYSTEM SET timezone = 'UTC';
SELECT pg_reload_conf();