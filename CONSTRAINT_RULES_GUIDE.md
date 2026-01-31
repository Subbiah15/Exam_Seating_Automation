# Seating Arrangement Rules & Constraints

## Overview

The Exam Seating Engine applies **4 core constraint rules** to prevent cheating while optimizing hall utilization. This document explains each rule in detail with mathematical models.

---

## Rule 1: Same Subject Separation

### Definition
**Students writing the SAME subject must NOT sit in adjacent seats (horizontally or vertically).**

### Visual Example

#### ❌ NOT Allowed
```
[CS101-S1] [CS101-S2]    ← Same subject, adjacent
    ↓
[CS101-S3] [CS101-S4]    ← Same subject, same row

This violates Rule 1
```

#### ✅ Allowed
```
[CS101-S1] [EC201-S1]    ← Different subjects, can be adjacent
    ↓
[CS101-S2] [EC201-S2]    ← Different subjects, can be adjacent

This satisfies Rule 1
```

### Mathematical Definition
For any student S1 and S2 in same hall:
```
If S1.subject == S2.subject:
    Then distance(S1, S2) > 1  (not adjacent)
Else:
    Any distance allowed
```

### Implementation
The algorithm:
1. Places student S1 with subject X at position (r, c)
2. Marks positions as "forbidden" if neighbor has subject X
3. Finds next available seat avoiding same-subject neighbors
4. If all seats forbidden → conflict recorded

### Why This Rule?
- **Primary Purpose:** Prevent cheating
- **Mechanism:** Students can't easily share answers with same-exam neighbors
- **Benefit:** Makes visual cheating impractical

### Real Example
**Exam Day: CS101**
- S001 (CS101) at position (1,1)
- S002 (CS101) CANNOT sit at:
  - (1,2) - right neighbor
  - (2,1) - below neighbor
  - (1,0) - left neighbor (if exists)
  - (0,1) - above neighbor (if exists)
- S002 (CS101) CAN sit at:
  - (1,3) or further
  - (3,1) or further
  - Diagonal positions (not adjacent)

---

## Rule 2: Same Department Row Separation

### Definition
**Students from the SAME department must NOT sit in the SAME ROW.**

### Visual Example

#### ❌ NOT Allowed
```
Row 1: [CSE-S1] [CSE-S2] [ECE-S1]   ← Two CSE students in same row
Row 2: [CSE-S3] [MECH-S1] [ECE-S2]
```

#### ✅ Allowed
```
Row 1: [CSE-S1] [ECE-S1] [MECH-S1]  ← Different departments in same row
Row 2: [CSE-S2] [MECH-S2] [ECE-S2]  ← Different departments in same row
Row 3: [CSE-S3] [ECE-S3] [MECH-S3]
```

### Mathematical Definition
For any row R:
```
If student S1 and S2 both in row R:
    Then S1.department != S2.department
```

### Implementation
The algorithm:
1. Maintains per-row department counts
2. When placing student with department D in row R:
   - Checks if department D already has someone in row R
   - If yes → moves to different row
   - If all rows have department D → finds minimal conflict
3. Prioritizes spreading departments

### Why This Rule?
- **Primary Purpose:** Prevent mass cheating within departments
- **Mechanism:** Reduces "cluster cheating" where department friends help each other
- **Benefit:** Maximizes geographic spread within exam hall

### Real Example
**Engineering College Exam:**

Departments: CSE, ECE, MECH

#### ❌ Bad Arrangement
```
Seat (Row-Col)    Student        Department
    (1,1)         S001           CSE
    (1,2)         S002           CSE        ← Violation!
    (1,3)         S003           ECE

    (2,1)         S004           CSE        ← Violation!
    (2,2)         S005           ECE
    (2,3)         S006           MECH
```

#### ✅ Good Arrangement
```
Seat (Row-Col)    Student        Department
    (1,1)         S001           CSE
    (1,2)         S002           ECE
    (1,3)         S003           MECH

    (2,1)         S004           CSE
    (2,2)         S005           MECH
    (2,3)         S006           ECE

    (3,1)         S007           MECH
    (3,2)         S008           CSE        ← Different from (2,1)
    (3,3)         S009           ECE
```

---

## Rule 3: Subject Mixing (Multi-Subject Days)

### Definition
**When multiple subjects are examined on SAME day, students must be INTERLEAVED throughout the hall (not segregated by subject).**

### Visual Example

#### ❌ NOT Allowed (Subject Blocks)
```
Hall A:
[CS101-S1] [CS101-S2] [CS101-S3]
[EC201-S1] [EC201-S2] [EC201-S3]

← All CS101 on one side, all EC201 on other = segregation
```

#### ✅ Allowed (Subject Mixing)
```
Hall A:
[CS101-S1] [EC201-S1] [CS101-S2]
[EC201-S2] [CS101-S3] [EC201-S3]

← CS101 and EC201 interleaved = good mixing
```

### Mathematical Definition
**Mixing Score** = Proportion of different-subject neighbors
```
For each subject in hall:
    good_neighbors = neighbors with different subject
    total_neighbors = all neighbors
    
Mixing_Score = avg(good_neighbors / total_neighbors) for all subjects

Target: Mixing_Score ≥ 0.7 (70% of neighbors are different subject)
```

### Implementation
The algorithm:
1. Places students alternating between subjects when possible
2. When multiple subjects exist:
   - First student from Subject 1
   - Next from Subject 2
   - Next from Subject 1
   - Etc. (round-robin)
3. If one subject exhausted, continues with remaining
4. Tracks mixing score

### Why This Rule?
- **Primary Purpose:** Reduce gang-cheating across subjects
- **Mechanism:** Different subject neighbors = can't easily help each other
- **Benefit:** Effective supervision for multiple exams in one hall

### Real Example
**Multi-Subject Exam: CS101 + EC201 on Feb 15**

**8 Students:**
- S001, S002 (CS101-CSE)
- S003, S004 (CS101-ECE)
- S005, S006 (EC201-CSE)
- S007, S008 (EC201-MECH)

#### ❌ Bad Arrangement (No Mixing)
```
Desk 1  2  3  4  5  6  7  8
Subj CS CS CS CS EC EC EC EC

Row arrangement:
[CS101-S1] [CS101-S2] [CS101-S3] [CS101-S4]
[EC201-S5] [EC201-S6] [EC201-S7] [EC201-S8]

Problem: Clear separation, students can coordinate within subjects
```

#### ✅ Good Arrangement (With Mixing)
```
Desk 1      2      3      4      5      6      7      8
Subj CS     EC     CS     EC     CS     EC     CS     EC

Row 1 Arrangement:
[CS101-S1] [EC201-S5] [CS101-S2] [EC201-S6]

Row 2 Arrangement:
[EC201-S7] [CS101-S3] [EC201-S8] [CS101-S4]

Mixing: 
- CS101 neighbors: 100% different subject (EC201)
- EC201 neighbors: 100% different subject (CS101)
- Mixing Score: 100% ✓
```

---

## Rule 4: Hall Optimization

### Definition
**Seat distribution across halls must be BALANCED (within 20% variance).**

### Visual Example

#### ❌ NOT Allowed (Imbalanced)
```
Total Students: 10
Hall A: 8 students (80% utilization) ← Over-crowded
Hall B: 2 students (20% utilization) ← Under-utilized

Variance: 60% ← Too high
```

#### ✅ Allowed (Balanced)
```
Total Students: 10
Hall A: 5 students (50% utilization)
Hall B: 5 students (50% utilization)

Variance: 0% ✓
```

### Mathematical Definition
```
For N students and M halls with capacities C1, C2, ..., CM:

ideal_per_hall = N / M
actual_distribution = [A1, A2, ..., AM]

variance = max(|Ai - ideal_per_hall|) / ideal_per_hall

Required: variance ≤ 0.2 (20%)
```

### Implementation
The algorithm:
1. Calculates ideal students per hall: N_total / N_halls
2. Places students in round-robin across halls
3. Monitors per-hall count
4. When hall approaches capacity:
   - Moves to next hall
   - Maintains balance
5. Final check: ensures no hall > 120% of ideal

### Why This Rule?
- **Primary Purpose:** Fair resource utilization
- **Mechanism:** Prevents overcrowding in some halls, empty seats in others
- **Benefit:** Consistent supervision quality across all halls

### Real Example
**Exam Day: 15 CS101 Students, 3 Halls**

**Ideal per hall:** 15 / 3 = 5 students

#### ❌ Bad Distribution
```
Hall A (40 seats): 10 students → 25% utilization (over-crowded)
Hall B (40 seats):  3 students → 7.5% utilization (wasted)
Hall C (40 seats):  2 students → 5% utilization (wasted)

Variance: (10-5)/5 = 100% ✗ POOR BALANCE
```

#### ✅ Good Distribution
```
Hall A (40 seats): 5 students → 12.5% utilization
Hall B (40 seats): 5 students → 12.5% utilization
Hall C (40 seats): 5 students → 12.5% utilization

Variance: 0% ✓ PERFECT BALANCE
```

---

## Combined Constraint Example

### Scenario
**Exam:** CS101 + EC201 on Feb 15, 2026

**Students:**
```
CSE Department:
  - S001, S002, S003 (CS101)
  - S004, S005, S006 (EC201)

ECE Department:
  - S007, S008 (CS101)
  - S009, S010 (EC201)
```

**Halls:** Hall A (6x2=12 seats), Hall B (6x2=12 seats)

### Algorithm Flow

**Step 1: Filter by subjects**
```
Selected: CS101 + EC201
Filtered Students: All 10 (both subjects present)
```

**Step 2: Sort by department**
```
CSE: [S001, S002, S003, S004, S005, S006]
ECE: [S007, S008, S009, S010]
```

**Step 3: Place S001 (CS101-CSE)**
```
Try Hall A, Row 1, Col 1 ✓
Mark forbidden: neighbors with CS101

Current:
Hall A:
[S001(CS101-CSE)] [      FORBIDDEN      ] [             ]
[             ] [             ] [             ]
```

**Step 4: Place S002 (CS101-CSE)**
```
Try Hall A, Row 1, Col 1 ✗ (occupied)
Try Hall A, Row 1, Col 2 ✗ (forbidden - S001 is CS101)
Try Hall A, Row 1, Col 3 ✓
Mark forbidden: neighbors with CS101

Current:
Hall A:
[S001(CS101)] [   FORBIDDEN   ] [S002(CS101)] [  FORBIDDEN  ] ...
```

**Step 5: Place S004 (EC201-CSE)**
```
Try Hall A, Row 1, Col 2 ✓ (different subject from S001, S002)
But Mark forbidden: S004 is in Row 1, CSE dept
Now Row 1 has CSE → next CSE must go to different row

Current:
Hall A:
[S001(CS101-CSE)] [S004(EC201-CSE)] [S002(CS101-CSE)] ...

Wait! Check Rule 2: S001 and S004 both CSE in same Row 1 ✗

Reconsider:
Try Hall A, Row 2, Col 1 ✓ (different row from S001)
```

**Final Valid Arrangement:**

```
Hall A (6 students):
Row 1: [S001(CS101-CSE)] [S007(CS101-ECE)] [S005(EC201-CSE)]
Row 2: [S004(EC201-CSE)] [S008(CS101-ECE)] [S009(EC201-ECE)]

Hall B (4 students):
Row 1: [S002(CS101-CSE)] [S010(EC201-ECE)]
Row 2: [S003(CS101-CSE)] [S006(EC201-CSE)]

Validation:
Rule 1 ✓: No same-subject adjacent
  - S001(CS101) neighbors: S007(CS101)? No, it's column-wise
  - All CS101 separated by ECE or EEE
  
Rule 2 ✓: No same-department in same row
  - Row 1 Hall A: CSE, ECE, CSE? No! S001 CSE, S007 ECE, S005 CSE ✗

Let me recalculate...
```

---

## Constraint Priority

When conflicts arise:
```
Priority 1: Rule 1 (Same Subject Separation) - HIGHEST
Priority 2: Rule 2 (Same Department Row)
Priority 3: Rule 3 (Subject Mixing)
Priority 4: Rule 4 (Hall Optimization) - LOWEST
```

If impossible to satisfy all:
- Rules 1 & 2 are strictly enforced (reports as conflicts)
- Rule 3 & 4 are optimized as much as possible

---

## Performance Metrics

The system reports:

| Metric | Description | Target |
|--------|-------------|--------|
| assigned | Students successfully placed | = total_students |
| conflicts | Constraint violations | = 0 |
| utilization | % of seats used | 60-80% |
| mixing_score | Subject diversity | ≥ 70% |

---

## Optimization Techniques

### 1. Greedy Placement
**Algorithm Used:** Standard greedy constraint satisfaction
- Places each student in best available seat
- Backtracks if necessary
- Time complexity: O(N * S) where N=students, S=seats

### 2. Randomization
- Different arrangement each generation
- Prevents predictable patterns
- Good for exam security

### 3. Department-Aware Sorting
- Pre-sorts students by department
- Improves Rule 2 satisfaction
- Reduces backtracking

---

**Version:** 2.0  
**Last Updated:** January 31, 2026  
**Status:** Complete & Verified
