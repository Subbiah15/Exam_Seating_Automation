# CSV/Excel Upload Format Guide

## File Requirements

### Accepted Formats
- ✅ **CSV** (.csv) - Comma-Separated Values
- ✅ **Excel** (.xlsx) - Microsoft Excel Spreadsheet

### Minimum Requirements
- At least **2 columns required**: Student ID and Name
- Other columns are **optional**
- First row must contain **column headers**

---

## Column Names (Flexible)

The system accepts multiple column name variations for flexibility:

### Required Columns

#### Column 1: Student ID / Registration Number
Any of these names will work:
- `reg_no` (recommended)
- `Student ID`
- `Reg No`
- `enrollment_no`
- `Enrollment Number`

**Example values:** S001, REG123, E001, 1001

#### Column 2: Student Name
Any of these names will work:
- `name` (recommended)
- `Name`
- `student_name`
- `Student Name`

**Example values:** John Doe, Alice Smith, Bob Johnson

### Optional Columns

#### Column 3: Department (Optional)
Any of these names will work:
- `department` (recommended)
- `Department`
- `dept`
- `Dept`

**Example values:** Computer Science, Mathematics, Physics, Engineering

#### Column 4: Subject/Course Code (Optional)
Any of these names will work:
- `subject_code` (recommended)
- `Subject`
- `Course Code`
- `Course`
- `subject`

**Example values:** CS101, MATH201, PHY301, CS102

---

## Example CSV Formats

### Format 1: Minimal (Required Only)
```
reg_no,name
S001,Alice Johnson
S002,Bob Smith
S003,Carol White
S004,David Brown
S005,Eve Davis
```

### Format 2: With Department (Recommended)
```
reg_no,name,department,subject_code
S001,Alice Johnson,Computer Science,CS101
S002,Bob Smith,Computer Science,CS101
S003,Carol White,Mathematics,MATH201
S004,David Brown,Mathematics,MATH201
S005,Eve Davis,Physics,PHY301
```

### Format 3: Alternative Column Names
```
Student ID,Name,Department,Course Code
S001,Alice Johnson,Computer Science,CS101
S002,Bob Smith,Computer Science,CS101
S003,Carol White,Mathematics,MATH201
```

### Format 4: Mixed Naming (Also Works)
```
enrollment_no,student_name,dept,subject
S001,Alice Johnson,CS,CS101
S002,Bob Smith,CS,CS101
S003,Carol White,MATH,MATH201
```

---

## Excel File Format

Create an Excel file with headers in the first row:

| reg_no | name | department | subject_code |
|--------|------|-----------|--------------|
| S001 | Alice Johnson | Computer Science | CS101 |
| S002 | Bob Smith | Computer Science | CS101 |
| S003 | Carol White | Mathematics | MATH201 |
| S004 | David Brown | Mathematics | MATH201 |
| S005 | Eve Davis | Physics | PHY301 |

---

## Data Validation Rules

✅ **Valid Data:**
- Student ID is unique (not checked, but recommended)
- Name is not empty
- Department can be any text
- Subject code can be any text

❌ **Invalid Data (Rows Skipped):**
- Missing Student ID → Row ignored
- Missing Name → Row ignored
- Extra whitespace → Automatically trimmed
- Empty rows → Skipped
- Rows with errors → Logged and skipped

---

## Sample Download

### Minimal Template
```csv
reg_no,name
S001,Student Name
S002,Another Student
```

### Full Template (Recommended)
```csv
reg_no,name,department,subject_code
S001,John Doe,Computer Science,CS101
S002,Jane Smith,Computer Science,CS101
S003,Mike Johnson,Mathematics,MATH201
S004,Sarah Williams,Mathematics,MATH201
S005,Tom Brown,Physics,PHY301
S006,Lisa Davis,Physics,PHY301
S007,David Miller,Chemistry,CHEM101
S008,Emma Wilson,Chemistry,CHEM101
S009,James Moore,Biology,BIO202
S010,Olivia Taylor,Biology,BIO202
```

---

## Real-World Examples

### Example 1: University Exam
```
reg_no,name,department,subject_code
A001,Raj Kumar,Electronics,EC101
A002,Priya Singh,Electronics,EC101
B001,Amit Patel,Mechanical,ME201
B002,Kavya Sharma,Mechanical,ME201
C001,Vikram Desai,Civil,CV301
C002,Anjali Nair,Civil,CV301
```

### Example 2: College Board Exam
```
Student ID,Name,Department,Course
101,Alice Brown,Science,Physics
102,Bob Green,Science,Chemistry
201,Carol Red,Commerce,Accounts
202,David Blue,Commerce,Economics
```

### Example 3: School Entrance Test
```
enrollment_no,student_name,section,exam_code
1001,Ravi Kumar,A,MATH001
1002,Priya Gupta,A,MATH001
1003,Arjun Singh,B,MATH001
1004,Divya Patel,B,MATH001
```

---

## Upload Process

1. **Go to Upload Page**
   - Click "Upload" in navigation menu

2. **Select File**
   - CSV or Excel file with proper format

3. **Click "Upload"**
   - System validates the file
   - Parses all rows with valid data

4. **Success Message**
   - Shows how many students were added
   - Shows total students in system

---

## Common Issues & Solutions

### Issue: "File must be CSV or Excel format"
**Solution:** Use .csv or .xlsx file extension

### Issue: No students uploaded
**Possible Causes:**
1. Column names don't match
2. Student ID or Name is missing
3. File encoding is not UTF-8

**Solution:**
- Ensure `reg_no` and `name` columns exist
- Check file is saved as UTF-8
- Use exact column names from the guide

### Issue: Only some students uploaded
**Possible Causes:**
- Some rows have missing Student ID or Name
- Some rows have extra spaces

**Solution:**
- Review data for empty cells
- Trim extra whitespace manually
- Re-upload corrected file

### Issue: Special characters causing problems
**Solution:**
- Use UTF-8 encoding
- Avoid quotes in CSV unless data contains commas
- Excel usually handles this automatically

---

## Best Practices

1. **Use Recommended Column Names**
   ```
   reg_no, name, department, subject_code
   ```

2. **Keep Consistent Data**
   - Same department spelling across rows
   - Consistent student ID format

3. **No Extra Spaces**
   - Trim leading/trailing whitespace
   - Single spaces between first/last names

4. **Use UTF-8 Encoding**
   - Save CSV as UTF-8 in text editor
   - Excel usually does this automatically

5. **Backup Original File**
   - Keep original before uploading
   - Useful if you need to re-upload

---

## API Response Examples

### Success Response
```json
{
  "message": "Students uploaded successfully",
  "count": 10,
  "total_students": 10,
  "timestamp": "2026-01-31T10:30:45.123456"
}
```

### Error Response
```json
{
  "detail": "File must be CSV or Excel format"
}
```

---

## Column Mapping Logic

The system uses this mapping (in order):

```python
# Student ID - tries these in order
reg_no OR Student ID OR Reg No

# Name - tries these in order
name OR Name OR student_name OR Student Name

# Department - tries these in order
department OR Department OR dept OR Dept

# Subject - tries these in order
subject_code OR Subject OR Course Code OR Course OR subject
```

If the first option doesn't exist, it tries the next one.

---

## Data Storage

When uploaded, each student record stores:
- **student_id** → From Student ID column
- **name** → From Name column
- **department** → From Department column (optional)
- **subject** → From Subject/Course Code column (optional)

This data is used later for:
- Seating constraint checking (same subject avoidance)
- Department-based row grouping
- Seating arrangement reporting

---

**Last Updated:** January 31, 2026  
**Version:** 1.0  
**Status:** Production Ready
