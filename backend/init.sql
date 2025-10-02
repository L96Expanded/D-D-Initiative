-- Initialize the database with proper extensions and settings
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Ensure the database is properly configured
ALTER SYSTEM SET timezone = 'UTC';
SELECT pg_reload_conf();