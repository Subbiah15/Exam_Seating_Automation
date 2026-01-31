"""
Intelligent Exam Seating Engine - FastAPI Application
Main entry point for the exam seating system
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Dict, Optional
import uuid
from datetime import datetime
import io
import csv
import os
import json
from threading import Lock
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from models import (
    Student, ExamHall, Seat, ExamRequest, SeatingArrangement
)
from seating_engine import SeatingEngine
from auth import (
    LoginRequest, SignupRequest, TokenResponse, 
    hash_password, verify_password, create_access_token, decode_token
)
from users_db import (
    create_user, get_user_by_username, user_exists, 
    get_user_by_id, get_user_by_student_id
)

app = FastAPI(
    title="Intelligent Exam Seating Engine",
    description="Automate exam seating with intelligent constraint satisfaction",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize seating engine
seating_engine = SeatingEngine()

# In-memory data stores (replace with database in production)
students_db: List[Student] = []
halls_db: Dict[str, ExamHall] = {}
arrangements_db: Dict[str, dict] = {}
uploads_db: List[dict] = []

# Simple persistent JSON store (keeps last used counter and data)
DATA_STORE_FILE = os.path.join(os.path.dirname(__file__), 'data_store.json')
data_lock = Lock()
store_counters = {"last_id": 0}


def _get_assigned_seats_from_arrangement(arrangement):
    """Extract all assigned seats from an arrangement"""
    assigned_seats = []
    for hall_allocation in arrangement.get('hall_allocations', []):
        for seat_info in hall_allocation.get('seats', []):
            seat = Seat(**seat_info)
            assigned_seats.append(seat)
    return assigned_seats


def _generate_id(prefix: Optional[str] = None) -> str:
    """Generate a simple sequential ID: PREFIX_1 or ID_1"""
    with data_lock:
        store_counters['last_id'] += 1
        nid = store_counters['last_id']
    if prefix:
        return f"{prefix}_{nid}"
    return f"ID_{nid}"


def save_data_store():
    """Persist current in-memory DBs to JSON file."""
    with data_lock:
        dump = {
            'students': [s.dict() for s in students_db],
            'halls': {hid: h.dict() for hid, h in halls_db.items()},
            'arrangements': {},
            'uploads': uploads_db,
            'counters': store_counters
        }

        # For arrangements, store metadata and arrangement dict
        for aid, arr in arrangements_db.items():
            arr_copy = dict(arr)
            # If arrangement contains Pydantic model, convert to dict
            arrangement_obj = arr_copy.get('arrangement')
            try:
                if hasattr(arrangement_obj, 'dict'):
                    arr_copy['arrangement'] = arrangement_obj.dict()
            except Exception:
                pass

            dump['arrangements'][aid] = arr_copy

        with open(DATA_STORE_FILE, 'w', encoding='utf-8') as f:
            json.dump(dump, f, ensure_ascii=False, indent=2)


def load_data_store():
    """Load persisted data into in-memory stores at startup."""
    global students_db, halls_db, arrangements_db, uploads_db, store_counters
    if not os.path.exists(DATA_STORE_FILE):
        return

    with open(DATA_STORE_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Load students
    students_db.clear()
    for s in data.get('students', []):
        try:
            students_db.append(Student.parse_obj(s))
        except Exception:
            continue

    # Load halls
    halls_db.clear()
    for hid, h in data.get('halls', {}).items():
        try:
            halls_db[hid] = ExamHall.parse_obj(h)
        except Exception:
            continue

    # Load arrangements
    arrangements_db.clear()
    for aid, a in data.get('arrangements', {}).items():
        try:
            arr = dict(a)
            # If arrangement stored as dict, try to rehydrate SeatingArrangement
            arrangement_obj = arr.get('arrangement')
            if isinstance(arrangement_obj, dict):
                arr['arrangement'] = SeatingArrangement.parse_obj(arrangement_obj)
            arrangements_db[aid] = arr
        except Exception:
            arrangements_db[aid] = a

    uploads_db.clear()
    uploads_db.extend(data.get('uploads', []))

    store_counters = data.get('counters', store_counters)


# Load persisted data on startup
load_data_store()


# ==================== HEALTH & INFO ENDPOINTS ====================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Intelligent Exam Seating Engine API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Exam Seating Engine"
    }


@app.post("/api/reset")
async def reset_database():
    """Reset all data to start fresh (development only)"""
    global students_db, halls_db, arrangements_db, uploads_db
    students_db.clear()
    halls_db.clear()
    arrangements_db.clear()
    uploads_db.clear()
    # Reset counters
    with data_lock:
        store_counters['last_id'] = 0
    # Persist empty store
    save_data_store()

    return {
        "status": "success",
        "message": "Database reset to empty state",
        "timestamp": datetime.now().isoformat()
    }


# ==================== STUDENT ENDPOINTS ====================

@app.post("/api/seating/upload-students")
async def upload_students(file: UploadFile = File(...)):
    """
    Upload students from CSV file
    Expected columns: Student ID, Name, Enrollment No, Department, Subject
    """
    try:
        if not file.filename.endswith(('.csv', '.xlsx')):
            raise HTTPException(
                status_code=400,
                detail="File must be CSV or Excel format"
            )
        
        contents = await file.read()
        
        # Parse CSV - accept both "Student ID/reg_no", "Name/name", "Department/department", "Subject/subject_code"
        if file.filename.endswith('.csv'):
            stream = io.StringIO(contents.decode('utf-8'))
            reader = csv.DictReader(stream)
            
            uploaded_students = []
            for row in reader:
                try:
                    reg_no = (row.get('reg_no') or row.get('Student ID') or row.get('Reg No', '')).strip()
                    name = (row.get('name') or row.get('Name', '')).strip()
                    dept = (row.get('department') or row.get('Department', '')).strip()
                    subject = (row.get('subject_code') or row.get('Subject', '')).strip()
                    if not reg_no or not name:
                        continue
                    student = Student(
                        student_id=reg_no,
                        name=name,
                        department=dept,
                        subject=subject
                    )
                    uploaded_students.append(student)
                except Exception as e:
                    continue
            
            # Store in database
            students_db.extend(uploaded_students)
            # Persist
            uploads_db.append({
                'filename': file.filename,
                'timestamp': datetime.now().isoformat(),
                'count': len(uploaded_students),
                'status': 'success'
            })
            save_data_store()

            return {
                "message": "Students uploaded successfully",
                "count": len(uploaded_students),
                "total_students": len(students_db),
                "timestamp": datetime.now().isoformat()
            }
        else:
            # For Excel files, basic parsing
            return {
                "message": "Excel files require pandas library",
                "count": 0,
                "detail": "Install pandas: pip install pandas openpyxl"
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/api/students/count")
async def get_students_count():
    """Get total number of uploaded students"""
    return {"count": len(students_db)}


@app.get("/api/students/subjects")
async def get_available_subjects():
    """Get all unique subjects from uploaded students"""
    subjects = set()
    subject_count = {}
    
    for student in students_db:
        if student.subject:
            subjects.add(student.subject)
            subject_count[student.subject] = subject_count.get(student.subject, 0) + 1
    
    return {
        "subjects": sorted(list(subjects)),
        "subject_details": [
            {"code": subj, "count": subject_count[subj]}
            for subj in sorted(subjects)
        ],
        "total_unique_subjects": len(subjects)
    }


@app.get("/api/students")
async def list_students():
    """List all students"""
    return {
        "total": len(students_db),
        "students": [
            {
                "student_id": s.student_id,
                "name": s.name,
                "department": s.department,
                "subject": s.subject
            }
            for s in students_db
        ]
    }


# ==================== EXAM HALL ENDPOINTS ====================

@app.post("/api/halls/add")
async def add_hall(hall_data: dict):
    """
    Create a new exam hall
    Expected fields: name, rows, columns (total_seats is calculated)
    """
    try:
        name = hall_data.get('name', '').strip()
        rows = int(hall_data.get('rows', 0))
        cols = int(hall_data.get('columns', 0))
        
        # Validation
        if not name:
            raise HTTPException(status_code=400, detail="Hall name is required")
        if rows <= 0 or cols <= 0:
            raise HTTPException(status_code=400, detail="Rows and columns must be positive")
        
        # Calculate total seats
        total_seats = rows * cols
        
        # Create hall id
        hall_id = _generate_id('HALL')
        hall = ExamHall(
            hall_id=hall_id,
            name=name,
            total_seats=total_seats,
            rows=rows,
            columns=cols
        )
        
        halls_db[hall_id] = hall
        # Persist
        save_data_store()

        return {
            "message": "Hall added successfully",
            "hall": {
                "id": hall_id,
                "name": hall.name,
                "total_seats": hall.total_seats,
                "rows": hall.rows,
                "columns": hall.columns
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error adding hall: {str(e)}")


@app.get("/api/halls")
async def get_halls():
    """List all exam halls"""
    return {
        "total": len(halls_db),
        "halls": [
            {
                "id": hall_id,
                "name": hall.name,
                "total_seats": hall.total_seats,
                "rows": hall.rows,
                "columns": hall.columns
            }
            for hall_id, hall in halls_db.items()
        ]
    }


@app.get("/api/halls/{hall_id}")
async def get_hall(hall_id: str):
    """Get specific hall details"""
    if hall_id not in halls_db:
        raise HTTPException(status_code=404, detail="Hall not found")
    
    hall = halls_db[hall_id]
    return {
        "id": hall_id,
        "name": hall.name,
        "total_seats": hall.total_seats,
        "rows": hall.rows,
        "columns": hall.columns
    }


@app.delete("/api/halls/{hall_id}")
async def delete_hall(hall_id: str):
    """Delete an exam hall"""
    if hall_id not in halls_db:
        raise HTTPException(status_code=404, detail="Hall not found")
    
    hall = halls_db.pop(hall_id)
    # Persist changes
    save_data_store()

    return {
        "message": "Hall deleted successfully",
        "hall_name": hall.name,
        "timestamp": datetime.now().isoformat()
    }


# ==================== SEATING GENERATION ENDPOINTS ====================

@app.post("/api/seating/generate")
async def generate_seating(request_data: dict):
    """
    Generate seating arrangement for specific exam date and subjects
    Expected fields: 
    - hall_ids (list): Selected exam halls
    - exam_date (string): Exam date (YYYY-MM-DD)
    - subject_codes (list): Subject codes to generate seating for
    - algorithm (string): 'greedy' or 'genetic' (optional)
    """
    try:
        hall_ids = request_data.get('hall_ids', [])
        exam_date = request_data.get('exam_date', '')
        subject_codes = request_data.get('subject_codes', [])
        algorithm = request_data.get('algorithm', 'greedy')
        
        # Validation
        if not hall_ids:
            raise HTTPException(status_code=400, detail="No halls selected")
        if not exam_date:
            raise HTTPException(status_code=400, detail="Exam date is required (YYYY-MM-DD)")
        if not subject_codes:
            raise HTTPException(status_code=400, detail="At least one subject must be selected")
        if not students_db:
            raise HTTPException(status_code=400, detail="No students uploaded")
        
        # Get selected halls
        selected_halls = [halls_db[hid] for hid in hall_ids if hid in halls_db]
        if not selected_halls:
            raise HTTPException(status_code=400, detail="Selected halls not found")
        
        # Filter students by subject codes (case-insensitive)
        filtered_students = [
            s for s in students_db 
            if s.subject and s.subject.upper() in [sc.upper() for sc in subject_codes]
        ]
        
        if not filtered_students:
            raise HTTPException(
                status_code=400, 
                detail=f"No students found for subjects: {', '.join(subject_codes)}"
            )
        
        # Check capacity
        total_capacity = sum(h.total_seats for h in selected_halls)
        total_students = len(filtered_students)
        
        if total_capacity < total_students:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient capacity ({total_capacity}) for {total_students} students writing these subjects"
            )
        
        # Run seating algorithm
        try:
            exam_id = _generate_id('EXAM')
            arrangement = seating_engine.arrange_seating(
                exam_id=exam_id,
                students=filtered_students,
                halls=selected_halls
            )

            # Store arrangement with clear sequential ID
            arrangement_id = _generate_id('ARR')
            total_cap = sum(h.total_seats for h in selected_halls)
            utilization = round((arrangement.total_arranged / total_cap * 100), 1) if total_cap else 0
            arrangements_db[arrangement_id] = {
                'arrangement': arrangement,
                'id': arrangement_id,
                'created_at': datetime.now().isoformat(),
                'exam_date': exam_date,
                'exam_name': f"Exam {exam_date}",
                'subjects': subject_codes,
                'hall_names': [h.name for h in selected_halls],
                'total_assigned': arrangement.total_arranged,
                'total_students': total_students,
                'total_conflicts': len(arrangement.conflicts) if hasattr(arrangement, 'conflicts') else 0,
                'utilization': utilization
            }

            # Persist
            save_data_store()

            return {
                "message": "Seating arrangement generated successfully",
                "arrangement_id": arrangement_id,
                "exam_date": exam_date,
                "subjects": subject_codes,
                "assigned": arrangement.total_arranged,
                "total_students": total_students,
                "conflicts": len(arrangement.conflicts) if hasattr(arrangement, 'conflicts') else 0,
                "halls": [h.name for h in selected_halls],
                "utilization": f"{utilization}%",
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as algo_error:
            raise HTTPException(
                status_code=500,
                detail=f"Algorithm failed: {str(algo_error)}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.get("/api/seating/arrangements")
async def list_arrangements():
    """List all seating arrangements"""
    return {
        "total": len(arrangements_db),
        "arrangements": [
            {
                "id": arr_id,
                "created_at": arr.get('created_at'),
                "exam_name": arr.get('exam_name', ''),
                "exam_date": arr.get('exam_date', ''),
                "subjects": arr.get('subjects', []),
                "hall_name": ', '.join(arr.get('hall_names', ['All Halls'])),
                "total_assigned": arr.get('total_assigned', 0),
                "total_conflicts": arr.get('total_conflicts', 0),
                "utilization": arr.get('utilization', 0)
            }
            for arr_id, arr in arrangements_db.items()
        ]
    }


def _get_assigned_seats_from_arrangement(arrangement):
    """Flatten hall_allocations to list of assigned seats."""
    seats_list = []
    if not hasattr(arrangement, 'hall_allocations'):
        return seats_list
    for hall_id, seats in arrangement.hall_allocations.items():
        for seat in seats:
            if getattr(seat, 'student_id', None):
                seats_list.append(seat)
    return seats_list


@app.get("/api/seating/arrangement/{arrangement_id}")
async def get_arrangement(arrangement_id: str):
    """Get specific seating arrangement details"""
    if arrangement_id not in arrangements_db:
        raise HTTPException(status_code=404, detail="Arrangement not found")
    
    arr_data = arrangements_db[arrangement_id]
    arrangement = arr_data['arrangement']
    assigned_seats = _get_assigned_seats_from_arrangement(arrangement)
    
    return {
        "id": arrangement_id,
        "hall_name": ', '.join(arr_data.get('hall_names', [])),
        "total_assigned": arrangement.total_arranged,
        "total_students": arrangement.total_students,
        "exam_date": arr_data.get('exam_date'),
        "subjects": arr_data.get('subjects', []),
        "success_rate": f"{(arrangement.total_arranged / max(1, arrangement.total_students) * 100):.2f}%",
        "constraints_satisfied": arrangement.constraints_satisfied,
        "created_at": arr_data.get('created_at'),
        "seats_data": [
            {
                "hall": seat.hall_id,
                "row": seat.row,
                "column": seat.column,
                "student_id": seat.student_id,
                "student_name": next(
                    (s.name for s in students_db if s.student_id == seat.student_id),
                    "Unknown"
                ),
                "student_subject": getattr(seat, 'student_subject', None),
                "student_department": getattr(seat, 'student_department', None)
            }
            for seat in assigned_seats
        ][:100]
    }


@app.post("/api/arrangements/search")
async def search_student_seating(request: Dict):
    """
    Search for student's seating assignment
    Expects: {"student_id": "STU001"} in request body
    """
    student_id = request.get('student_id') or request.get('value')
    
    if not student_id:
        raise HTTPException(status_code=400, detail="student_id is required")
    
    results = []
    
    # Search through all arrangements
    for arrangement_id, arr_data in arrangements_db.items():
        arrangement = arr_data.get('arrangement')
        if not arrangement:
            continue
        
        # Search in hall allocations
        if hasattr(arrangement, 'hall_allocations'):
            for hall_id, seats in arrangement.hall_allocations.items():
                for seat in seats:
                    # Handle seat as object (primary) or dict (fallback)
                    s_id = getattr(seat, 'student_id', None)
                    if s_id is None and isinstance(seat, dict):
                        s_id = seat.get('student_id')
                        
                    if s_id == student_id:
                        # Found the student's seat
                        # Get student info
                        student = next(
                            (s for s in students_db if s.student_id == student_id),
                            None
                        )
                        
                        # Get hall info
                        hall = halls_db.get(hall_id)
                        
                        # Extract seat info safely (Object or Dict)
                        def get_val(obj, attr, default=None):
                            val = getattr(obj, attr, None)
                            if val is None and isinstance(obj, dict):
                                val = obj.get(attr)
                            return val if val is not None else default

                        seat_num = get_val(seat, 'seat_number')
                        row = get_val(seat, 'row')
                        col = get_val(seat, 'column')
                        if col is None: col = get_val(seat, 'col')
                        
                        subj = get_val(seat, 'subject_code')
                        if not subj and student:
                            subj = getattr(student, 'subject', None)

                        # Generate seat number if missing
                        if not seat_num and row is not None and col is not None:
                            seat_num = f"R{int(row)+1}-C{int(col)+1}"

                        dept = get_val(seat, 'department')
                        if not dept and student:
                            dept = getattr(student, 'department', None)
                        
                        results.append({
                            "arrangement_id": arrangement_id,
                            "exam_date": arr_data.get('exam_date'),
                            "subjects": arr_data.get('subjects', []),
                            "student_id": student_id,
                            "student_name": student.name if student else "Unknown",
                            "student_email": student.email if hasattr(student, 'email') else "N/A",
                            "seat_number": seat_num,
                            "row": row,
                            "column": col,
                            "hall_id": hall_id,
                            "hall_name": hall.name if hall else "Unknown Hall",
                            "hall_location": hall.location if hall and hasattr(hall, 'location') else "N/A",
                            "hall_capacity": hall.total_seats if hall and hasattr(hall, 'total_seats') else 0,
                            "subject_code": subj,
                            "department": dept or "N/A"
                        })
    
    return {
        "success": True,
        "count": len(results),
        "results": results
    }


@app.get("/api/seating/arrangement/{arrangement_id}/pdf")
async def download_pdf(arrangement_id: str):
    """Download seating arrangement as professional PDF"""
    if arrangement_id not in arrangements_db:
        raise HTTPException(status_code=404, detail="Arrangement not found")
    
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    except ImportError:
        # Fallback to text if reportlab not available
        return await download_pdf_text(arrangement_id)
    
    arr_data = arrangements_db[arrangement_id]
    arrangement = arr_data['arrangement']
    assigned_seats = _get_assigned_seats_from_arrangement(arrangement)
    
    # PDF metadata
    exam_date = arr_data.get('exam_date', 'N/A')
    subjects = ', '.join(arr_data.get('subjects', []))
    halls = ', '.join(arr_data.get('hall_names', []))
    
    # Create temporary PDF file
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False)
    temp_path = temp_file.name
    temp_file.close()
    
    # Create PDF document
    doc = SimpleDocTemplate(
        temp_path,
        pagesize=A4,
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Container for PDF elements
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1f4788'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=colors.HexColor('#2c5aa0'),
        spaceAfter=8,
        spaceBefore=10,
        fontName='Helvetica-Bold',
        borderColor=colors.HexColor('#2c5aa0'),
        borderPadding=5
    )
    
    # Title
    title = Paragraph("EXAM SEATING ARRANGEMENT REPORT", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.15*inch))
    
    # Exam Details Section
    elements.append(Paragraph("EXAMINATION DETAILS", heading_style))
    
    exam_details = [
        ['Arrangement ID:', arrangement_id],
        ['Exam Date:', exam_date],
        ['Subjects:', subjects],
        ['Halls:', halls],
        ['Created:', arr_data.get('created_at', 'N/A')[:19]],
    ]
    
    exam_table = Table(exam_details, colWidths=[2*inch, 4*inch])
    exam_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0f8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d0d0d0')),
    ]))
    elements.append(exam_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Summary Statistics Section
    elements.append(Paragraph("SUMMARY STATISTICS", heading_style))
    
    success_rate = (arrangement.total_arranged / max(1, arrangement.total_students) * 100)
    stats_data = [
        ['Total Students:', str(arrangement.total_students)],
        ['Students Arranged:', str(arrangement.total_arranged)],
        ['Success Rate:', f'{success_rate:.1f}%'],
        ['Total Conflicts:', str(len(arrangement.conflicts) if hasattr(arrangement, 'conflicts') else 0)],
        ['Constraints Satisfied:', 'YES' if arrangement.constraints_satisfied else 'NO'],
        ['Hall Utilization:', f'{arr_data.get("utilization", 0)}%'],
    ]
    
    stats_table = Table(stats_data, colWidths=[2*inch, 4*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f8e8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d0d0d0')),
    ]))
    elements.append(stats_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Seating Assignments Section
    elements.append(Paragraph("SEATING ASSIGNMENTS", heading_style))
    
    # Build seating table data
    seat_table_data = [
        ['No.', 'Hall', 'Row', 'Seat', 'Student ID', 'Student Name', 'Subject']
    ]
    
    for i, seat in enumerate(assigned_seats, 1):
        student_obj = next(
            (s for s in students_db if s.student_id == seat.student_id),
            None
        )
        student_name = student_obj.name if student_obj else "Unknown"
        student_subject = getattr(seat, 'student_subject', 'N/A')
        
        seat_table_data.append([
            str(i),
            seat.hall_id,
            str(seat.row),
            str(seat.column),
            seat.student_id,
            student_name[:20],  # Truncate long names
            student_subject
        ])
    
    seat_table = Table(
        seat_table_data,
        colWidths=[0.4*inch, 0.8*inch, 0.4*inch, 0.4*inch, 0.9*inch, 1.5*inch, 0.8*inch]
    )
    
    seat_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        
        # Data rows - alternating colors
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        
        # All cells
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 1), (3, -1), 'CENTER'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cccccc')),
    ]))
    
    elements.append(seat_table)
    
    # Footer
    elements.append(Spacer(1, 0.3*inch))
    footer_text = f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Exam Seating Engine v2.0"
    elements.append(Paragraph(footer_text, ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=TA_CENTER
    )))
    
    # Build PDF
    doc.build(elements)
    
    return FileResponse(
        temp_path,
        media_type='application/pdf',
        filename=f'seating-arrangement-{arrangement_id}.pdf'
    )


async def download_pdf_text(arrangement_id: str):
    """Fallback text report when reportlab not available"""
    if arrangement_id not in arrangements_db:
        raise HTTPException(status_code=404, detail="Arrangement not found")
    
    arr_data = arrangements_db[arrangement_id]
    arrangement = arr_data['arrangement']
    assigned_seats = _get_assigned_seats_from_arrangement(arrangement)
    
    exam_date = arr_data.get('exam_date', 'N/A')
    subjects = ', '.join(arr_data.get('subjects', []))
    halls = ', '.join(arr_data.get('hall_names', []))
    
    report = f"""
{'=' * 80}
EXAM SEATING ARRANGEMENT REPORT
{'=' * 80}

EXAMINATION DETAILS
{'-' * 80}
Arrangement ID:      {arrangement_id}
Exam Date:           {exam_date}
Subjects:            {subjects}
Created:             {arr_data.get('created_at', 'N/A')}
Halls:               {halls}

SUMMARY STATISTICS
{'-' * 80}
Total Students:      {arrangement.total_students}
Students Arranged:   {arrangement.total_arranged}
Success Rate:        {(arrangement.total_arranged / max(1, arrangement.total_students) * 100):.2f}%
Total Conflicts:     {len(arrangement.conflicts) if hasattr(arrangement, 'conflicts') else 0}
Constraints Met:     {'YES' if arrangement.constraints_satisfied else 'NO'}
Hall Utilization:    {arr_data.get('utilization', 0)}%

SEATING ASSIGNMENTS
{'-' * 80}
{'S.No.':<6} {'Hall':<12} {'Row':<5} {'Seat':<5} {'Student ID':<12} {'Student Name':<20} {'Subject':<12}
{'-' * 80}
"""
    
    for i, seat in enumerate(assigned_seats, 1):
        student_obj = next(
            (s for s in students_db if s.student_id == seat.student_id),
            None
        )
        student_name = student_obj.name if student_obj else "Unknown"
        student_subject = getattr(seat, 'student_subject', 'N/A')
        
        report += f"{i:<6} {seat.hall_id:<12} {seat.row:<5} {seat.column:<5} {seat.student_id:<12} {student_name:<20} {student_subject:<12}\n"
    
    report += f"\n{'=' * 80}\n"
    report += f"Report Generated: {datetime.now().isoformat()}\n"
    report += f"{'=' * 80}\n"
    
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(report)
        temp_path = f.name
    
    return FileResponse(
        temp_path,
        media_type='text/plain',
        filename=f'seating-arrangement-{arrangement_id}.txt'
    )


@app.delete("/api/seating/arrangement/{arrangement_id}")
async def delete_arrangement(arrangement_id: str):
    """Delete a seating arrangement"""
    if arrangement_id not in arrangements_db:
        raise HTTPException(status_code=404, detail="Arrangement not found")
    arrangements_db.pop(arrangement_id)
    # Persist
    save_data_store()

    return {
        "message": "Arrangement deleted successfully",
        "arrangement_id": arrangement_id,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/seating/arrangement/{arrangement_id}/seat-map")
async def get_seat_map_image(arrangement_id: str):
    """Generate a visual seat map image for the arrangement"""
    if arrangement_id not in arrangements_db:
        raise HTTPException(status_code=404, detail="Arrangement not found")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        raise HTTPException(status_code=500, detail="PIL library not available")
    
    arr_data = arrangements_db[arrangement_id]
    arrangement = arr_data['arrangement']
    assigned_seats = _get_assigned_seats_from_arrangement(arrangement)
    
    # Group seats by hall
    seats_by_hall = {}
    for seat in assigned_seats:
        if seat.hall_id not in seats_by_hall:
            seats_by_hall[seat.hall_id] = []
        seats_by_hall[seat.hall_id].append(seat)
    
    # Color palette for different subjects
    subject_colors = {
        'CS101': '#FF6B6B',
        'EC201': '#4ECDC4', 
        'ME301': '#FFE66D',
        'DBMS101': '#95E1D3',
        'CIVIL101': '#FFA07A',
    }
    
    # Generate image for each hall
    images = []
    
    for hall_id, seats in sorted(seats_by_hall.items()):
        # Find max row and col
        max_row = max(s.row for s in seats) if seats else 0
        max_col = max(s.column for s in seats) if seats else 0
        
        # Seat dimensions
        seat_width = 60
        seat_height = 60
        padding = 10
        margin = 40
        
        # Calculate image size
        img_width = (max_col + 1) * (seat_width + padding) + 2 * margin
        img_height = (max_row + 1) * (seat_height + padding) + 2 * margin + 60  # Extra space for title
        
        # Create image
        img = Image.new('RGB', (img_width, img_height), color='#FFFFFF')
        draw = ImageDraw.Draw(img)
        
        # Try to use a better font, fallback to default
        try:
            title_font = ImageFont.truetype("arial.ttf", 20)
            seat_font = ImageFont.truetype("arial.ttf", 8)
            label_font = ImageFont.truetype("arial.ttf", 7)
        except:
            title_font = ImageFont.load_default()
            seat_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
        
        # Draw title
        title_text = f"Hall: {hall_id}"
        draw.text((margin, 10), title_text, fill='#2C3E50', font=title_font)
        
        # Create seat lookup
        seat_map = {(s.row, s.column): s for s in seats}
        
        # Draw all seats in the hall
        for row in range(max_row + 1):
            for col in range(max_col + 1):
                x = margin + col * (seat_width + padding)
                y = margin + 40 + row * (seat_height + padding)
                
                if (row, col) in seat_map:
                    seat = seat_map[(row, col)]
                    student_subject = getattr(seat, 'student_subject', 'N/A')
                    
                    # Get color for subject
                    color_hex = subject_colors.get(student_subject, '#B3E5FC')
                    
                    # Draw seat rectangle
                    draw.rectangle(
                        [x, y, x + seat_width, y + seat_height],
                        fill=color_hex,
                        outline='#333333',
                        width=2
                    )
                    
                    # Draw student ID
                    id_text = seat.student_id[:8]  # Truncate long IDs
                    draw.text(
                        (x + 5, y + 8),
                        id_text,
                        fill='#000000',
                        font=seat_font
                    )
                    
                    # Draw subject code
                    subj_text = student_subject[:12]
                    draw.text(
                        (x + 5, y + 28),
                        subj_text,
                        fill='#000000',
                        font=label_font
                    )
                else:
                    # Empty seat
                    draw.rectangle(
                        [x, y, x + seat_width, y + seat_height],
                        fill='#EEEEEE',
                        outline='#CCCCCC',
                        width=1
                    )
                    draw.text(
                        (x + 20, y + 25),
                        'EMPTY',
                        fill='#999999',
                        font=label_font
                    )
        
        images.append((hall_id, img))
    
    # If multiple halls, combine them vertically
    if len(images) == 1:
        final_img = images[0][1]
    else:
        total_height = sum(img.height + 20 for _, img in images)
        final_width = max(img.width for _, img in images)
        final_img = Image.new('RGB', (final_width, total_height), color='#FFFFFF')
        
        current_y = 0
        for hall_id, img in images:
            final_img.paste(img, (0, current_y))
            current_y += img.height + 20
    
    # Save to temporary file
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(mode='wb', suffix='.png', delete=False)
    temp_path = temp_file.name
    temp_file.close()
    
    final_img.save(temp_path, format='PNG')
    
    return FileResponse(
        temp_path,
        media_type='image/png',
        filename=f'seat-map-{arrangement_id}.png'
    )


# ==================== LEGACY ENDPOINTS ====================

@app.post("/api/arrange-seating")
async def arrange_seating_legacy(exam_request: ExamRequest):
    """
    Legacy endpoint - Arrange seating for an exam with constraint satisfaction
    Use POST /api/seating/generate instead
    """
    try:
        if not exam_request.students:
            raise HTTPException(status_code=400, detail="No students provided")
        if not exam_request.halls:
            raise HTTPException(status_code=400, detail="No exam halls provided")
        
        total_seats = sum(hall.total_seats for hall in exam_request.halls)
        if total_seats < len(exam_request.students):
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient seats ({total_seats}) for students ({len(exam_request.students)})"
            )
        
        arrangement = seating_engine.arrange_seating(
            exam_id=exam_request.exam_id,
            students=exam_request.students,
            halls=exam_request.halls
        )
        
        arrangement_id = _generate_id('ARR')
        arrangements_db[arrangement_id] = {'arrangement': arrangement, 'created_at': datetime.now().isoformat()}
        save_data_store()

        return arrangement
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/arrangement/{arrangement_id}")
async def get_arrangement_legacy(arrangement_id: str):
    """Legacy endpoint - Retrieve a saved seating arrangement"""
    if arrangement_id not in arrangements_db:
        raise HTTPException(status_code=404, detail="Arrangement not found")
    
    return arrangements_db[arrangement_id].get('arrangement')


@app.post("/api/validate-arrangement")
async def validate_arrangement(arrangement_id: str):
    """Validate a seating arrangement against all constraints"""
    if arrangement_id not in arrangements_db:
        raise HTTPException(status_code=404, detail="Arrangement not found")
    
    arr_data = arrangements_db[arrangement_id]
    arrangement = arr_data.get('arrangement')
    
    if not arrangement:
        raise HTTPException(status_code=404, detail="Arrangement data not found")
    
    is_valid, issues = seating_engine.validate_arrangement(arrangement)
    
    return {
        "arrangement_id": arrangement_id,
        "is_valid": is_valid,
        "issues": issues,
        "total_students": arrangement.total_students,
        "total_arranged": arrangement.total_arranged,
        "success_rate": f"{(arrangement.total_arranged / arrangement.total_students * 100):.2f}%"
    }


@app.get("/api/arrangements")
async def list_arrangements_legacy():
    """List all saved seating arrangements (legacy)"""
    return {
        "total_arrangements": len(arrangements_db),
        "arrangements": [
            {
                "arrangement_id": arr_id,
                "total_arranged": arr.get('arrangement').total_arranged if arr.get('arrangement') else 0,
                "total_students": arr.get('arrangement').total_students if arr.get('arrangement') else 0,
            }
            for arr_id, arr in arrangements_db.items()
        ]
    }


@app.post("/api/optimize-arrangement/{arrangement_id}")
async def optimize_arrangement(arrangement_id: str):
    """
    Optimize an existing arrangement to improve constraint satisfaction
    """
    if arrangement_id not in arrangements_db:
        raise HTTPException(status_code=404, detail="Arrangement not found")
    
    return {
        "status": "optimization_in_progress",
        "arrangement_id": arrangement_id,
        "message": "Optimization feature coming soon"
    }


# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/api/auth/signup", response_model=Dict)
async def signup(request: SignupRequest):
    """
    Create a new user account (admin, teacher, or student)
    """
    # Check if username already exists
    if user_exists(request.username):
        raise HTTPException(
            status_code=400, 
            detail=f"Username '{request.username}' already exists"
        )
    
    # Hash password
    password_hash = hash_password(request.password)
    
    # Create user in database
    user = create_user(
        username=request.username,
        password_hash=password_hash,
        email=request.email,
        role=request.role,  # admin, teacher, or student
        name=request.name,
        student_id=request.student_id if request.role == "student" else None
    )
    
    return {
        "success": True,
        "message": f"User '{request.username}' created successfully",
        "user_id": user['user_id'],
        "username": user['username'],
        "role": user['role'],
        "redirect": "/login.html"
    }


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and return JWT token
    """
    # Get user by username
    user = get_user_by_username(request.username)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    
    # Verify password
    if not verify_password(request.password, user['password_hash']):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    
    # Check if user is active
    if not user.get('is_active', True):
        raise HTTPException(
            status_code=403,
            detail="User account is inactive"
        )
    
    # Create JWT token
    token_data = {
        "user_id": user['user_id'],
        "username": user['username'],
        "role": user['role']
    }
    access_token = create_access_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        token_type="Bearer",
        role=user['role'],
        user_id=user['user_id'],
        username=user['username']
    )


@app.get("/api/auth/me")
async def get_current_user(authorization: str = Header(None)):
    """
    Get current user info from JWT token
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization header")
    
    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = parts[1]
    
    # Decode token
    token_data = decode_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Get user details
    user = get_user_by_id(token_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user['user_id'],
        "username": user['username'],
        "email": user['email'],
        "role": user['role'],
        "name": user['name'],
        "student_id": user.get('student_id'),
        "created_at": user['created_at']
    }


@app.post("/api/auth/logout")
async def logout():
    """
    Logout endpoint (client-side token deletion is primary logout mechanism)
    """
    return {
        "success": True,
        "message": "Logged out successfully. Please delete the token from localStorage."
    }


if __name__ == "__main__":
    import uvicorn
    # Use port 8081 and bind to localhost
    uvicorn.run(app, host="127.0.0.1", port=8081)
