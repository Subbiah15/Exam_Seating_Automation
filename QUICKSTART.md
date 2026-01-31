# Exam Seating Engine - Quick Start Guide

## Project Setup ✅ Complete

Your Intelligent Exam Seating Engine is ready to use!

### Project Contents

```
Exam_Seating_Engine/
├── main.py              ← FastAPI application (API endpoints)
├── models.py            ← Data models (Student, Hall, Seat, etc.)
├── seating_engine.py    ← Core seating algorithm
├── test_engine.py       ← Test suite for validation
├── requirements.txt     ← Python dependencies
├── README.md            ← Full documentation
├── QUICKSTART.md        ← This file
└── venv/                ← Virtual environment
```

## Running the API Server

1. **Activate Virtual Environment**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. **Start the Server**
   ```powershell
   python main.py
   ```

   You should see:
   ```
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```

3. **Access the API**
   - API Root: http://localhost:8000
   - Swagger UI (Interactive Docs): http://localhost:8000/docs
   - ReDoc (Alternative Docs): http://localhost:8000/redoc

## Quick API Test

### Using Swagger UI (Recommended)
1. Go to http://localhost:8000/docs
2. Click on **POST /api/arrange-seating**
3. Click **Try it out**
4. Use the example JSON below and click **Execute**

### Example Request

```json
{
  "exam_id": "EXAM_CS101",
  "exam_name": "Computer Science Final Exam",
  "exam_date": "2026-02-20",
  "students": [
    {
      "student_id": "STU001",
      "name": "Alice Johnson",
      "subject": "Programming",
      "department": "Engineering"
    },
    {
      "student_id": "STU002",
      "name": "Bob Smith",
      "subject": "Programming",
      "department": "Science"
    },
    {
      "student_id": "STU003",
      "name": "Carol White",
      "subject": "Algorithms",
      "department": "Engineering"
    }
  ],
  "halls": [
    {
      "hall_id": "HALL_A",
      "name": "Main Auditorium",
      "total_seats": 50,
      "rows": 5,
      "columns": 10
    }
  ]
}
```

### Expected Response

```json
{
  "arrangement_id": "ARR_EXAM_CS101",
  "exam_id": "EXAM_CS101",
  "hall_allocations": {
    "HALL_A": [
      {
        "seat_id": "HALL_A_R0_C0",
        "hall_id": "HALL_A",
        "row": 0,
        "column": 0,
        "student_id": "STU001",
        "student_subject": "Programming",
        "student_department": "Engineering"
      }
      // ... more seats
    ]
  },
  "total_arranged": 3,
  "total_students": 3,
  "constraints_satisfied": true,
  "conflicts": []
}
```

## Running Tests

Validate the engine's functionality:

```powershell
python test_engine.py
```

Expected Output:
- ✅ Basic Seating Arrangement
- ✅ Constraint Validation
- ✅ Multiple Halls
- ✅ Insufficient Capacity Handling

## Key Features

### ✅ Constraint 1: Same-Subject Adjacency Prevention
- Students of the same subject cannot sit:
  - Left/Right adjacent
  - Above/Below adjacent

### ✅ Constraint 2: Same-Department Row Placement
- Students from the same department cannot share a row
- Prevents collusion and ensures fair seating

### ✅ Constraint 3: Efficient Hall Utilization
- Optimally distributes students across halls
- Prefers central seating (better sight lines)
- Validates sufficient capacity

## API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/api/arrange-seating` | Arrange students in exam halls |
| GET | `/api/arrangement/{id}` | Retrieve specific arrangement |
| GET | `/api/arrangements` | List all arrangements |
| POST | `/api/validate-arrangement` | Validate an arrangement |
| GET | `/api/health` | Service health status |

## Advanced Usage

### Python Script Example

```python
from models import Student, ExamHall
from seating_engine import SeatingEngine

# Create sample data
students = [
    Student(student_id="S001", name="John", subject="Math", department="Science"),
    Student(student_id="S002", name="Jane", subject="Math", department="Engineering"),
    Student(student_id="S003", name="Bob", subject="Physics", department="Science"),
]

halls = [
    ExamHall(hall_id="H1", name="Hall 1", total_seats=20, rows=4, columns=5),
]

# Run seating engine
engine = SeatingEngine()
result = engine.arrange_seating("EXAM001", students, halls)

# Check results
print(f"Arranged: {result.total_arranged}/{result.total_students}")
print(f"Success: {result.constraints_satisfied}")
```

## Troubleshooting

### Issue: "Address already in use" on port 8000
**Solution:** Change port in main.py:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Use different port
```

### Issue: Virtual environment not activating
**Solution:** If you get an execution policy error:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

### Issue: Module not found errors
**Solution:** Ensure venv is activated and dependencies installed:
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Next Steps

1. **Customize Constraints**: Modify seating_engine.py for specific requirements
2. **Database Integration**: Add SQLAlchemy for persistent storage
3. **Advanced Algorithms**: Implement genetic algorithms for optimization
4. **UI Dashboard**: Build a React/Vue frontend
5. **Authentication**: Add user authentication for API
6. **Deployment**: Deploy to AWS/Azure/Heroku

## Support

For issues or questions, refer to:
- [README.md](README.md) - Full documentation
- [seating_engine.py](seating_engine.py) - Algorithm details
- [main.py](main.py) - API implementation

---

**Happy Exam Seating! 🎓**
