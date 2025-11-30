# CORS and 500 Error Fixes - 2025-11-30

## Issues Identified

### 1. Preset Schema Validation Error
**Error:** `pydantic_core._pydantic_core.ValidationError: 1 validation error for CreatureCreate - encounter_id: Field required`

**Location:** `backend/app/routers/presets.py` lines 81, 121, 173

**Root Cause:** 
- The `PresetResponse` schema was using `List[CreatureCreate]` which requires `encounter_id`
- Presets are templates without encounters, so they shouldn't have `encounter_id`
- The `get_preset`, `create_preset`, and `update_preset` endpoints were creating `CreatureCreate` objects without the required `encounter_id` field

**Fix:**
- Changed `PresetResponse.creatures` to use `List[CreatureCreateNested]` instead of `List[CreatureCreate]`
- `CreatureCreateNested` extends `CreatureBase` without requiring `encounter_id`
- Updated all three preset endpoints to use `CreatureCreateNested` when building responses

**Files Modified:**
- `backend/app/models/schemas.py` - Line 107: Changed creatures field type
- `backend/app/routers/presets.py` - Lines 7, 81, 121, 173: Import and usage updates

### 2. Database Schema Mismatch - Missing Column
**Error:** `psycopg2.errors.UndefinedColumn: column encounters.round_number does not exist`

**Location:** `backend/app/routers/encounters.py` - Any query accessing the Encounter model

**Root Cause:**
- The `Encounter` model in `backend/app/models/models.py` includes a `round_number` column
- The production PostgreSQL database was created before this column was added to the model
- SQLAlchemy tried to SELECT the column, but it didn't exist in the database

**Fix:**
- Created database migration script: `backend/migrations/001_add_round_number.sql`
- Created Python migration runner: `backend/migrations/run_migration.py`
- Added firewall rule to allow local IP (81.34.22.250) access to Azure PostgreSQL
- Executed migration: `ALTER TABLE encounters ADD COLUMN round_number INTEGER NOT NULL DEFAULT 1;`
- Verified column was created with proper type and default value

**Migration Details:**
```sql
ALTER TABLE encounters ADD COLUMN round_number INTEGER NOT NULL DEFAULT 1;
```

**Firewall Rule Added:**
```bash
az postgres flexible-server firewall-rule create \
  --resource-group BCSAI2025-DEVOPS-STUDENTS-A \
  --name dnd-initiative-db \
  --rule-name AllowMyIP \
  --start-ip-address 81.34.22.250 \
  --end-ip-address 81.34.22.250
```

## CORS Configuration (Current State)

### Azure App Service CORS
- **Status:** Disabled (empty `allowedOrigins`)
- **Reason:** Azure CORS doesn't properly handle credentials with FastAPI

### FastAPI CORS Middleware
- **Status:** Active and configured correctly
- **Configuration:**
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=settings.CORS_ORIGINS,  # From environment variable
      allow_credentials=True,
      allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
      allow_headers=["*"],
      expose_headers=["*"],
      max_age=3600,
  )
  ```

### CORS_ORIGINS Environment Variable
```json
[
  "https://wonderful-stone-035aba410.3.azurestaticapps.net",
  "https://karsusinitiative.com",
  "https://www.karsusinitiative.com",
  "https://dnd-initiative-prod.azurewebsites.net",
  "https://api.karsusinitiative.com",
  "http://localhost:3000"
]
```

## Resolution Steps Taken

1. **Identified Issues from Logs:**
   - Used `az webapp log tail` to capture live application logs
   - Found two distinct error patterns in production

2. **Fixed Preset Schema:**
   - Changed `CreatureCreate` to `CreatureCreateNested` in 4 locations
   - Committed: `77ffc01` - "Fix preset schema to use CreatureCreateNested instead of CreatureCreate"

3. **Applied Database Migration:**
   - Created migration script with idempotent check
   - Added IP to PostgreSQL firewall
   - Executed migration successfully
   - Verified column creation
   - Committed: `e9ce052` - "Add database migration for round_number column"

4. **Restarted App Service:**
   - Triggered deployment via GitHub push
   - Manually restarted app service to ensure changes loaded

## Expected Result

- ✅ **Presets:** GET, POST, PUT operations will now work without validation errors
- ✅ **Encounters:** GET, POST, PUT, DELETE operations will work without database errors
- ✅ **CORS:** Proper headers sent from FastAPI middleware with credentials support

## Testing Verification

To verify the fixes work:

1. **Test Preset GET:**
   ```bash
   curl -X GET "https://dnd-initiative-prod.azurewebsites.net/presets/{id}" \
     -H "Authorization: Bearer {token}"
   ```

2. **Test Encounter GET:**
   ```bash
   curl -X GET "https://dnd-initiative-prod.azurewebsites.net/encounters/{id}" \
     -H "Authorization: Bearer {token}"
   ```

3. **Verify CORS Headers:**
   ```bash
   curl -X OPTIONS "https://dnd-initiative-prod.azurewebsites.net/presets" \
     -H "Origin: https://karsusinitiative.com" \
     -H "Access-Control-Request-Method: GET" \
     -v
   ```

Expected response should include:
- `Access-Control-Allow-Origin: https://karsusinitiative.com`
- `Access-Control-Allow-Credentials: true`

## Files Changed

### Schema Fix
- `backend/app/models/schemas.py`
- `backend/app/routers/presets.py`

### Database Migration
- `backend/migrations/001_add_round_number.sql` (NEW)
- `backend/migrations/run_migration.py` (NEW)

## Commits
- `77ffc01` - Fix preset schema to use CreatureCreateNested instead of CreatureCreate
- `e9ce052` - Add database migration for round_number column
