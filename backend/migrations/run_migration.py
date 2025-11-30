import psycopg2
import sys

# Azure PostgreSQL connection details
connection_string = "host=dnd-initiative-db.postgres.database.azure.com port=5432 dbname=dnd_initiative user=dbadmin password=Momento90 sslmode=require"

migration_sql = """
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'encounters'
        AND column_name = 'round_number'
    ) THEN
        ALTER TABLE encounters
        ADD COLUMN round_number INTEGER NOT NULL DEFAULT 1;
        
        RAISE NOTICE 'Column round_number added to encounters table';
    ELSE
        RAISE NOTICE 'Column round_number already exists in encounters table';
    END IF;
END $$;
"""

try:
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(connection_string)
    cursor = conn.cursor()
    
    print("Executing migration...")
    cursor.execute(migration_sql)
    conn.commit()
    
    print("Migration completed successfully!")
    
    # Verify the column was added
    cursor.execute("""
        SELECT column_name, data_type, column_default
        FROM information_schema.columns
        WHERE table_name = 'encounters'
        AND column_name = 'round_number';
    """)
    
    result = cursor.fetchone()
    if result:
        print(f"Verified: Column '{result[0]}' exists with type '{result[1]}' and default '{result[2]}'")
    else:
        print("Warning: Column not found after migration!")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
