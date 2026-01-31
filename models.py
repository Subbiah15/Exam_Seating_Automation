from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ExamType(str, Enum):
    WRITTEN = "written"
    PRACTICAL = "practical"


class Student(BaseModel):
    """Student model for exam seating"""
    student_id: str
    name: str
    subject: str
    department: str
    exam_type: ExamType = ExamType.WRITTEN


class ExamHall(BaseModel):
    """Exam hall/room model"""
    hall_id: str
    name: str
    total_seats: int
    rows: int
    columns: int
    available: bool = True


class Seat(BaseModel):
    """Individual seat in an exam hall"""
    seat_id: str
    hall_id: str
    row: int
    column: int
    student_id: Optional[str] = None
    student_subject: Optional[str] = None
    student_department: Optional[str] = None


class SeatingArrangement(BaseModel):
    """Complete seating arrangement for an exam"""
    arrangement_id: str
    exam_id: str
    hall_allocations: dict  # {hall_id: [Seat]}
    total_arranged: int
    total_students: int
    constraints_satisfied: bool
    conflicts: List[str] = []


class ExamRequest(BaseModel):
    """Request to arrange seating for an exam"""
    exam_id: Optional[str] = None
    exam_name: Optional[str] = 'Exam'
    students: Optional[List[Student]] = []
    halls: Optional[List[ExamHall]] = []
    exam_date: Optional[str] = None
