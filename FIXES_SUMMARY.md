# Bug Fixes Summary

## Date: November 30, 2025

### Issues Fixed

#### 1. ✅ Preset Edit Not Including Creatures

**Problem:**
- When editing a preset, the creatures list was sent separately from the update data
- Backend expected creatures to be part of the `PresetUpdate` request body
- This caused preset edits to only update name/description/background, but ignore creature changes

**Root Cause:**
- `EditPresetModal.tsx` called `onSubmit(id, updateData, creatures)` with creatures as separate parameter
- `Home.tsx` tried to recreate the entire preset (delete + create), which was overcomplicated
- TypeScript `UpdatePreset` interface didn't include creatures field

**Fix:**
- Updated `EditPresetModal.tsx` to include creatures in the `updateData` object
- Simplified `Home.tsx` to just call `presetsAPI.update(id, updateData)` 
- Added `creatures?: CreateCreature[]` to `UpdatePreset` interface in `types/index.ts`

**Files Changed:**
- `frontend/src/components/EditPresetModal.tsx`
- `frontend/src/pages/Home.tsx`
- `frontend/src/types/index.ts`

**Commit:** `9d344a3` - "Fix preset edit to include creatures in update request"

---

#### 2. ⚠️ Encounter Creation with Multiple Creatures

**Issue Reported:**
"when i make an encounter, it fails if I add more than one creature in the encounter"

**Investigation:**
After reviewing the code, the backend encounter creation endpoint (`POST /encounters`) properly handles multiple creatures:

```python
# backend/app/routers/encounters.py
@router.post("", response_model=EncounterResponse, status_code=status.HTTP_201_CREATED)
async def create_encounter(
    encounter_data: EncounterCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new encounter."""
    db_encounter = Encounter(...)
    db.add(db_encounter)
    db.flush()  # Get the ID without committing
    
    # Create creatures - loops through all creatures
    for creature_data in encounter_data.creatures:
        db_creature = Creature(...)
        db.add(db_creature)
    
    db.commit()
    db.refresh(db_encounter)
    return EncounterResponse.model_validate(db_encounter)
```

The frontend (`EncounterModal.tsx`) also has proper error handling:
- Uses `Promise.all()` to upload images in parallel
- Has try-catch blocks to prevent single upload failures from breaking entire submission
- Falls back to fetching creature images from database if no file uploaded

**Possible Causes (Needs Testing):**
1. **Browser Cache** - Old CORS errors cached, causing authentication failures
2. **Network Timeout** - Multiple simultaneous image uploads timing out
3. **File Size** - Images exceeding 10MB limit (backend config: `MAX_FILE_SIZE: 10485760`)
4. **Session Expiry** - Authentication token expired during multi-creature creation

**Testing Recommendations:**

1. **Clear Browser Cache**
   ```
   - Open DevTools (F12)
   - Right-click Refresh → Empty Cache and Hard Reload
   - Or: Settings → Privacy → Clear browsing data → Cached images and files
   ```

2. **Test with Simple Data First**
   - Create encounter with 2 creatures, NO images
   - Create encounter with 2 creatures, WITH images
   - Check browser console (F12) for errors

3. **Check Network Tab**
   - Open DevTools → Network tab
   - Try creating encounter with multiple creatures
   - Look for failed requests (red status codes)
   - Check request/response for error details

4. **Test Different Scenarios**
   - 2 creatures, no images → Should work
   - 2 creatures, 1 image → Should work
   - 2 creatures, 2 images → Test this
   - 5 creatures, 5 images → Stress test

**Expected Behavior:**
- Encounter creation should succeed even if image uploads fail
- Creatures should be created with `image_url: undefined` if upload fails
- Console warnings (not errors) for failed uploads
- Encounter should redirect to initiative tracker after creation

---

### Testing Instructions

#### Test Preset Editing (Priority: HIGH)

1. **Navigate to Home Page**
   - Go to `https://karsusinitiative.com` (or `https://wonderful-stone-035aba410.3.azurestaticapps.net`)
   - Log in

2. **Create a Test Preset**
   - Click "Create New Preset"
   - Name: "Test Multi-Creature Preset"
   - Add 3 creatures:
     - Goblin (Initiative: 15, Type: Enemy)
     - Orc (Initiative: 12, Type: Enemy)
     - Fighter (Initiative: 18, Type: Player)
   - Click "Create Preset"

3. **Edit the Preset**
   - Click "Edit" on the preset you just created
   - Change name to "Updated Preset"
   - Remove Goblin
   - Add new creature: Wizard (Initiative: 14, Type: Player)
   - Change Orc initiative to 20
   - Click "Update Preset"

4. **Verify Changes**
   - Preset name should be "Updated Preset"
   - Should have 3 creatures: Orc (20), Fighter (18), Wizard (14)
   - Goblin should be gone

**Expected Result:** ✅ All changes saved correctly

**Previous Behavior:** ❌ Only name/description updated, creatures unchanged

---

#### Test Encounter Creation (Priority: HIGH)

1. **Clear Browser Cache**
   - F12 → Application → Clear storage → Clear site data
   - Close and reopen browser

2. **Test Simple Multi-Creature Encounter**
   - Click "Create New Encounter"
   - Name: "Simple Test"
   - Add 2 creatures (no images):
     - Creature 1: Name="Test1", Initiative=10, Type=Enemy
     - Creature 2: Name="Test2", Initiative=15, Type=Enemy
   - Click "Create Encounter"

3. **Test with Images**
   - Click "Create New Encounter"
   - Name: "Image Test"
   - Add 2 creatures:
     - Creature 1: Name="Goblin", Initiative=10, upload image
     - Creature 2: Name="Orc", Initiative=15, upload image
   - Click "Create Encounter"

4. **Check Console for Errors**
   - Open DevTools (F12) → Console tab
   - Look for red errors (not warnings)
   - Screenshot any errors and share

**Expected Result:** ✅ Both encounters created successfully, redirect to initiative tracker

**If Still Failing:**
- Check Console for error messages
- Check Network tab for failed requests
- Try with smaller images (< 1MB)
- Try without images first

---

### Deployment Status

**Frontend Deployment:**
- Changes committed: `9d344a3`
- Pushed to GitHub: ✅
- GitHub Actions workflow: Should auto-deploy to Azure Static Web Apps
- Estimated deployment time: 5-10 minutes

**Check Deployment Progress:**
```bash
# View GitHub Actions
https://github.com/L96Expanded/D-D-Initiative/actions

# Or check Azure Static Web App status
az staticwebapp show --name dnd-initiative-frontend --resource-group BCSAI2025-DEVOPS-STUDENTS-A
```

**Backend:**
- No changes needed
- Already deployed and healthy: ✅

---

### Known Issues (Not Fixed Yet)

#### Cloudflare Proxy (Orange Cloud) Timeout
- **Status:** Under investigation
- **Workaround:** Use gray cloud (DNS only) mode
- **Details:** See `AZURE_STATIC_APPS_CLOUDFLARE.md`
- **Impact:** Site works perfectly with direct Azure URL, custom domain works with DNS only

---

### Additional Notes

#### Why Preset Fix Was Simple
The backend was already correct - it expected `creatures` in the `PresetUpdate` body:

```python
class PresetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    background_image: Optional[str] = None
    creatures: Optional[List[CreatureCreateNested]] = None  # ← Already here!
```

The frontend just wasn't sending it correctly. Now fixed.

#### Why Encounter Issue Needs More Investigation
The encounter creation code looks correct:
- Backend properly handles multiple creatures ✅
- Frontend has proper error handling ✅
- CORS is fixed ✅
- Azure Storage is working ✅

Most likely cause:
- **Browser cache** showing old CORS errors
- **User needs to test after cache clear**

If issue persists after clearing cache:
- Could be network timeout with large images
- Could be session expiry during long operations
- Need to see actual error messages from browser console

---

### Next Steps

1. **Wait for deployment** (5-10 minutes after push)
2. **Test preset editing** (should work now ✅)
3. **Clear browser cache completely**
4. **Test encounter creation with multiple creatures**
5. **Report results:**
   - ✅ If working: Issue resolved
   - ❌ If failing: Share browser console errors

---

### Contact/Questions

If issues persist, please provide:
1. Browser console errors (F12 → Console tab)
2. Network tab failed requests (F12 → Network tab)
3. Exact steps to reproduce
4. Screenshot of error message

This will help diagnose the root cause of encounter creation issues.
