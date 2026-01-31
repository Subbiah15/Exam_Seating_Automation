# Advanced Seating Generation Guide

## New Features (v2.0)

The seating generation system now supports **date-based, subject-filtered seating arrangements** with intelligent mixing of students from different subjects on the same date.

---

## How It Works

### Step 1: Upload Students with Subject Codes
Upload a CSV with students including their subject codes.

**Example:**
```csv
reg_no,name,department,subject_code
S001,Alice Johnson,CSE,CS101
S002,Bob Smith,CSE,CS101
S003,Carol White,ECE,EC201
S004,David Brown,ECE,EC201
S005,Eve Davis,MECH,ME301
```

### Step 2: Navigate to "Generate Seating"

### Step 3: Select Exam Parameters

#### Exam Date
- Pick the date when the exam will be conducted
- Format: YYYY-MM-DD (e.g., 2026-02-15)
- Default: Today's date

#### Select Subjects
- Choose which subjects will be conducted on this date
- Only students enrolled in selected subjects will be seated
- **Example:** If you select "CS101" and "EC201", only those students will be arranged (not ME301 students)

#### Select Halls
- Choose which exam halls to use
- System distributes students evenly across selected halls

### Step 4: Click "Generate"

System will:
1. Filter students for selected subjects
2. Apply seating constraints
3. Generate optimized arrangement
4. Display results

---

## Seating Constraints Applied

### Rule 1: Same Subject Separation
**❌ NOT Allowed:** Two students writing the SAME subject sitting adjacent

**Example:**
- ❌ CS101 Student + CS101 Student (side by side)
- ✅ CS101 Student + EC201 Student (side by side)

**Purpose:** Prevent cheating by separating students taking the same exam

### Rule 2: Same Department Spreading
**❌ NOT Allowed:** Multiple students from SAME department in SAME row

**Example:**
```
Row 1: [CSE-S1] [CSE-S2] [CSE-S3]  ❌ Not Allowed
Row 1: [CSE-S1] [ECE-S1] [MECH-S1] ✅ Allowed
```

**Purpose:** Spread students geographically to prevent mass cheating

### Rule 3: Subject Mixing
**✅ REQUIRED:** Mix students from different subjects in same hall

**Example:**
```
Hall A contains:
- CS101 students (x3)
- EC201 students (x4)
Mixed together with proper spacing
```

**Purpose:** Ensures diverse supervision, different exam papers visible

### Rule 4: Hall Optimization
**✅ REQUIRED:** Distribute students evenly across selected halls

**Example with 2 halls and 7 students:**
```
Hall A: 4 students (57% utilization)
Hall B: 3 students (43% utilization)
```

**Purpose:** Prevent overcrowding in one hall

---

## Real-World Scenario

### Example: Engineering College Exam Day

**Date:** February 15, 2026

**Students Uploaded:**
```csv
reg_no,name,department,subject_code
E001,Raj Kumar,CSE,CS101
E002,Priya Singh,CSE,CS101
E003,Amit Patel,CSE,DBMS101
E004,Kavya Sharma,ECE,EC201
E005,Vikram Desai,ECE,EC201
E006,Anjali Nair,ECE,NETWORK201
E007,Arjun Singh,MECH,ME301
E008,Divya Patel,MECH,ME301
```

**Scenario 1: CS101 Exam at 9:00 AM**

Generate Seating:
- Exam Date: 2026-02-15
- Subjects: CS101
- Halls: Hall A, Hall B

Result:
- E001 (CS101-CSE) + E002 (CS101-CSE) → **NOT seated adjacent**
- Total Students: 2
- Halls Used: 1 (Hall A with 2 students)

---

**Scenario 2: EC201 + NETWORK201 Exam at 2:00 PM**

Generate Seating:
- Exam Date: 2026-02-15
- Subjects: EC201, NETWORK201
- Halls: Hall A, Hall B

Result:
- E004 (EC201-ECE) + E005 (EC201-ECE) → **NOT seated adjacent**
- E006 (NETWORK201-ECE) can sit anywhere
- Halls A+B mixed: EC201 + NETWORK201 students together
- Total Students: 3
- Utilization: ~21% (3/30 seats across 2 halls)

---

## API Endpoints

### Get Available Subjects
```
GET /api/students/subjects
```

**Response:**
```json
{
  "subjects": ["CS101", "DBMS101", "EC201"],
  "subject_details": [
    {"code": "CS101", "count": 2},
    {"code": "DBMS101", "count": 1},
    {"code": "EC201", "count": 2}
  ],
  "total_unique_subjects": 3
}
```

### Generate Seating
```
POST /api/seating/generate
```

**Request Body:**
```json
{
  "exam_date": "2026-02-15",
  "subject_codes": ["CS101", "EC201"],
  "hall_ids": ["hall-uuid-1", "hall-uuid-2"]
}
```

**Response:**
```json
{
  "message": "Seating arrangement generated successfully",
  "arrangement_id": "arr-uuid-123",
  "exam_date": "2026-02-15",
  "subjects": ["CS101", "EC201"],
  "assigned": 4,
  "total_students": 4,
  "conflicts": 0,
  "halls": ["Hall A", "Hall B"],
  "utilization": "26.7%",
  "timestamp": "2026-01-31T10:30:45.123456"
}
```

---

## Multi-Subject Exam Days

### Handling Multiple Exams on Same Date

**Example: Full Day Exam Schedule**

| Time | Subjects | Students | Halls |
|------|----------|----------|-------|
| 9:00 AM | CS101 | 5 | Hall A, B |
| 11:00 AM | EC201 + NETWORK201 | 6 | Hall A, B, C |
| 2:00 PM | DBMS101 + ME301 | 8 | All Halls |

**Process:**
1. Generate seating separately for each time slot
2. Each generation filters students by that slot's subjects
3. Creates independent arrangements

**Important:** Students can be seated differently in different exams (different time slots create new arrangements)

---

## Key Benefits

### For Administrators
- ✅ **Flexible Scheduling:** Create exam schedules with multiple subjects per day
- ✅ **Subject Filtering:** Only arrange students writing that subject
- ✅ **Automatic Mixing:** Different subjects mixed in same room
- ✅ **Optimization:** Efficient hall utilization

### For Exam Supervisors
- ✅ **Clear Arrangements:** Know exactly who sits where
- ✅ **Subject Info:** See which subjects are in each hall
- ✅ **Conflict Prevention:** Students taking same exam separated

### For Students
- ✅ **Fairness:** Objective seating (no favoritism)
- ✅ **Cheating Prevention:** Separated from classmates taking same exam
- ✅ **Transparency:** Clear rules applied consistently

---

## Common Use Cases

### Use Case 1: Single Subject Exam
**Date:** Feb 15, 2026  
**Subject:** CS101  
**Halls:** Hall A (30 seats)  
**Students:** 15 CS101 students

System arranges only CS101 students, prevents all 15 from clustering, separates them optimally.

### Use Case 2: Concurrent Exams
**Date:** Feb 15, 2026  
**Time Slot 1 (9 AM):** CS101 (5 students)  
**Time Slot 2 (11 AM):** EC201 (4 students)

Create two separate arrangements:
- Arrangement 1: CS101 students on Feb 15, 9 AM
- Arrangement 2: EC201 students on Feb 15, 11 AM

### Use Case 3: Mixed Subject Day
**Date:** Feb 15, 2026  
**Subjects:** CS101, DBMS101 (taught to same department)  
**Halls:** Hall A, Hall B  
**Students:** 5 CS101 + 5 DBMS101 = 10 total

System mixes both groups:
- Hall A: 2 CS101 + 3 DBMS101
- Hall B: 3 CS101 + 2 DBMS101
- Ensures no same-subject adjacency
- Different subjects interleaved

---

## Tips & Best Practices

### Before Generating
1. **Verify Subject Codes:** Ensure students have valid subject codes in upload
2. **Check Hall Capacity:** Total seats ≥ Students writing that subject
3. **Choose Appropriate Halls:** Use larger halls for many students, smaller for few

### During Generation
1. **Monitor Conflicts:** Check conflict count (should be 0)
2. **Review Utilization:** 60-80% utilization is typical
3. **Verify Dates:** Double-check exam date is correct

### After Generation
1. **Download Results:** Save arrangement for records
2. **Inform Students:** Publish seating arrangements 1-2 days before
3. **Print Seat Maps:** Physical maps in exam halls helpful

---

## Troubleshooting

### Issue: "No students found for subjects: CS101"
**Cause:** No uploaded students have CS101 as subject code  
**Solution:** Check CSV upload, ensure subject_code column values match selection

### Issue: "Insufficient capacity"
**Cause:** Not enough hall seats for students in selected subjects  
**Solution:** Add more halls or combine into larger halls

### Issue: High conflict count (>0)
**Cause:** Constraints cannot be fully satisfied with current configuration  
**Solution:** 
- Add more halls
- Spread over multiple time slots
- Use larger hall layouts (more rows/columns)

### Issue: Low utilization
**Cause:** Selected subjects have few students compared to hall size  
**Solution:**
- Use fewer, smaller halls
- Combine multiple subjects for same time slot
- Accept lower utilization for security

---

## Advanced Features

### Randomization
System applies randomness to prevent predictable patterns:
- Same setup generates different arrangements each time
- Good for preventing cheating strategies

### Department Awareness
System considers departments when spreading students:
- Same subject + same department → Extra separation
- Different subjects → Flexible placement

### Subject-Subject Awareness
When multiple subjects on same date:
- System mixes them efficiently
- Prevents blocks of one subject

---

## System Output Fields

Each arrangement stores:
- **exam_date:** Date of examination
- **subjects:** Subjects conducted
- **total_assigned:** Students successfully seated
- **total_students:** Students available to seat
- **utilization:** Percentage of seats used
- **conflicts:** Number of constraint violations
- **halls:** Which halls were used

---

**Version:** 2.0  
**Release Date:** January 31, 2026  
**Status:** Production Ready
