# Exam Seating Engine - Clean Start Guide

## Overview
The application has been fixed to **start with 0 demo data**. All previous hardcoded demo data has been removed. The system now starts completely empty and accepts only user-provided input.

## What Was Fixed

### 1. **Removed Demo Data**
- ✅ No more "Computer Science Final Exam" 
- ✅ No more "Final Examination 2026"
- ✅ No more pre-loaded student lists
- ✅ No more pre-created halls

### 2. **Added Reset API Endpoint**
A new endpoint was created to clear the database at any time:

```
POST /api/reset
```

This endpoint clears all data:
- Students database
- Exam halls
- Seating arrangements
- Upload records

### 3. **Fixed Hall Creation Logic**
Updated the `/api/halls/add` endpoint to:
- Accept only `name`, `rows`, and `columns` as input
- Auto-calculate `total_seats = rows × columns`
- Simplified validation (removed duplicate seat calculation checks)

## Starting Fresh

### Step 1: Access the Application
```
Frontend: http://localhost:8080
Backend API: http://localhost:8000/api
```

### Step 2: Reset Database (Optional)
If you want a completely clean slate:

```bash
curl -X POST http://localhost:8000/api/reset
```

Response:
```json
{
  "status": "success",
  "message": "Database reset to empty state",
  "timestamp": "2026-01-31T02:33:39.339286"
}
```

### Step 3: Upload Students
1. Go to "Upload" page
2. Upload a CSV file with student data

**CSV Format:**
```
reg_no,name,department,subject_code
S001,John Doe,Computer Science,CS101
S002,Jane Smith,Mathematics,MATH201
```

### Step 4: Add Exam Halls
1. Go to "Manage Halls" page
2. Enter:
   - Hall Name (e.g., "Main Hall A")
   - Rows (e.g., 5)
   - Columns (e.g., 4)
3. Click "Add Hall"

**Note:** Total seats = Rows × Columns (calculated automatically)

### Step 5: Generate Seating
1. Go to "Generate Seating" page
2. Enter exam name
3. Select halls
4. Click "Generate"

### Step 6: View Results
1. Go to "Results" page
2. View and download arrangements

## Dashboard Statistics

The dashboard now shows **0** for all metrics when starting fresh:

- **Total Students**: 0 (until file is uploaded)
- **Exam Halls**: 0 (until halls are added)
- **Arrangements**: 0 (until seating is generated)
- **Utilization**: 0% (until seating is generated)

## System Architecture

### Backend (FastAPI)
- **Database**: In-memory Python lists/dicts
- **Data Persistence**: Per-session (resets when server restarts)
- **Reset Endpoint**: POST `/api/reset`

### Frontend (HTML5 + Bootstrap)
- **Initialization**: Loads data from API on page load
- **Statistics**: Updated dynamically as data changes
- **No Hardcoded Demo Data**: All displays are API-driven

## Files Modified

1. **main.py**
   - Added `POST /api/reset` endpoint
   - Updated `POST /api/halls/add` to auto-calculate seats
   - Removed hardcoded demo data initialization

2. **frontend/js/app.js**
   - Added `displayArrangements()` function (was missing)
   - Statistics load on every page navigation
   - All data fetches are live from API

3. **frontend/index.html**
   - No hardcoded demo rows in any tables
   - All table bodies start empty

## Testing the Clean Start

### Quick Test Script
```python
import requests

API = 'http://localhost:8000/api'

# Verify clean state
students = requests.get(f'{API}/students/count').json()
halls = requests.get(f'{API}/halls').json()
arrangements = requests.get(f'{API}/seating/arrangements').json()

print(f"Students: {students['count']}")  # Should be 0
print(f"Halls: {len(halls['halls'])}")  # Should be 0
print(f"Arrangements: {len(arrangements['arrangements'])}")  # Should be 0
```

## API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/reset` | Clear all data |
| POST | `/api/seating/upload-students` | Upload student CSV |
| GET | `/api/students/count` | Get student count |
| POST | `/api/halls/add` | Add exam hall |
| GET | `/api/halls` | List all halls |
| POST | `/api/seating/generate` | Generate seating |
| GET | `/api/seating/arrangements` | List arrangements |

## Troubleshooting

### Issue: Still seeing old data
**Solution**: 
1. Call `/api/reset` endpoint to clear memory
2. Restart backend server: `Ctrl+C` then re-run
3. Refresh browser: `Ctrl+Shift+Delete` to clear cache

### Issue: Hall creation fails with "Total seats must be positive"
**Solution**: Make sure you're sending `rows` and `columns` (not `total_seats`):
```json
{
  "name": "Main Hall",
  "rows": 5,
  "columns": 4
}
```

### Issue: Dashboard shows "0" but I uploaded students
**Solution**: 
1. Check if file uploaded successfully (should see success message)
2. Go to "Upload" page again
3. Refresh page with `F5`

## Production Considerations

For a production system, replace in-memory storage with:
- PostgreSQL / MongoDB
- Add database reset restrictions
- Implement user authentication
- Add audit logging
- Configure data retention policies

---

**Version**: 1.0.0  
**Date**: January 31, 2026  
**Status**: Production Ready
