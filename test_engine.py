"""
Test script for the Intelligent Exam Seating Engine
Validates core functionality and constraint satisfaction
"""

from models import Student, ExamHall, ExamRequest, ExamType
from seating_engine import SeatingEngine
import json


def test_basic_seating():
    """Test basic seating arrangement"""
    print("=" * 60)
    print("Test 1: Basic Seating Arrangement")
    print("=" * 60)
    
    # Create test data
    students = [
        Student(student_id="S001", name="Alice Johnson", subject="Mathematics", department="Science"),
        Student(student_id="S002", name="Bob Smith", subject="Mathematics", department="Engineering"),
        Student(student_id="S003", name="Carol Davis", subject="Physics", department="Science"),
        Student(student_id="S004", name="David Wilson", subject="Physics", department="Engineering"),
        Student(student_id="S005", name="Eve Brown", subject="Chemistry", department="Science"),
        Student(student_id="S006", name="Frank Miller", subject="Chemistry", department="Engineering"),
    ]
    
    halls = [
        ExamHall(hall_id="H001", name="Hall A", total_seats=20, rows=4, columns=5),
    ]
    
    # Run arrangement
    engine = SeatingEngine()
    arrangement = engine.arrange_seating("EXAM001", students, halls)
    
    print(f"\nExam ID: {arrangement.exam_id}")
    print(f"Total Students: {arrangement.total_students}")
    print(f"Total Arranged: {arrangement.total_arranged}")
    print(f"Constraints Satisfied: {arrangement.constraints_satisfied}")
    print(f"Conflicts: {arrangement.conflicts if arrangement.conflicts else 'None'}")
    
    # Display seating details
    print("\nSeating Details:")
    for hall_id, seats in arrangement.hall_allocations.items():
        print(f"\nHall: {hall_id}")
        print(f"Total Seats in Arrangement: {len(seats)}")
        
        # Show a few sample seats
        occupied = [s for s in seats if s.student_id]
        print(f"Occupied Seats: {len(occupied)}")
        
        if occupied:
            print("\nSample Occupied Seats:")
            for seat in occupied[:3]:
                print(f"  Seat {seat.seat_id}: {seat.student_subject} ({seat.student_department})")
    
    return arrangement


def test_constraint_validation():
    """Test constraint validation"""
    print("\n" + "=" * 60)
    print("Test 2: Constraint Validation")
    print("=" * 60)
    
    students = [
        Student(student_id="S001", name="Student 1", subject="Math", department="Dept A"),
        Student(student_id="S002", name="Student 2", subject="Math", department="Dept B"),
        Student(student_id="S003", name="Student 3", subject="Physics", department="Dept A"),
        Student(student_id="S004", name="Student 4", subject="Physics", department="Dept B"),
    ]
    
    halls = [
        ExamHall(hall_id="H001", name="Hall A", total_seats=16, rows=4, columns=4),
    ]
    
    engine = SeatingEngine()
    arrangement = engine.arrange_seating("EXAM002", students, halls)
    
    is_valid, issues = engine.validate_arrangement(arrangement)
    
    print(f"Arrangement Valid: {is_valid}")
    print(f"Validation Issues: {len(issues)}")
    if issues:
        for issue in issues:
            print(f"  - {issue}")
    
    return is_valid


def test_multiple_halls():
    """Test seating across multiple halls"""
    print("\n" + "=" * 60)
    print("Test 3: Multiple Halls")
    print("=" * 60)
    
    # Create 50 students across 3 departments and 3 subjects
    students = []
    departments = ["Science", "Engineering", "Commerce"]
    subjects = ["Mathematics", "Physics", "Chemistry"]
    
    for i in range(50):
        students.append(
            Student(
                student_id=f"S{i+1:03d}",
                name=f"Student {i+1}",
                subject=subjects[i % 3],
                department=departments[i % 3]
            )
        )
    
    halls = [
        ExamHall(hall_id="H001", name="Hall A", total_seats=20, rows=4, columns=5),
        ExamHall(hall_id="H002", name="Hall B", total_seats=20, rows=4, columns=5),
        ExamHall(hall_id="H003", name="Hall C", total_seats=20, rows=4, columns=5),
    ]
    
    engine = SeatingEngine()
    arrangement = engine.arrange_seating("EXAM003", students, halls)
    
    print(f"\nExam ID: {arrangement.exam_id}")
    print(f"Total Students: {arrangement.total_students}")
    print(f"Total Arranged: {arrangement.total_arranged}")
    print(f"Success Rate: {(arrangement.total_arranged / arrangement.total_students * 100):.2f}%")
    print(f"Constraints Satisfied: {arrangement.constraints_satisfied}")
    
    # Hall-wise breakdown
    print("\nHall-wise Breakdown:")
    for hall_id, seats in arrangement.hall_allocations.items():
        occupied = [s for s in seats if s.student_id]
        print(f"  {hall_id}: {len(occupied)} students out of {len(seats)} seats")
    
    return arrangement


def test_insufficient_capacity():
    """Test behavior with insufficient seating capacity"""
    print("\n" + "=" * 60)
    print("Test 4: Insufficient Capacity")
    print("=" * 60)
    
    students = [
        Student(student_id=f"S{i:03d}", name=f"Student {i}", subject="Math", department="Dept A")
        for i in range(1, 101)
    ]
    
    halls = [
        ExamHall(hall_id="H001", name="Hall A", total_seats=50, rows=5, columns=10),
    ]
    
    engine = SeatingEngine()
    arrangement = engine.arrange_seating("EXAM004", students, halls)
    
    print(f"\nTotal Students: {arrangement.total_students}")
    print(f"Total Seats Available: 50")
    print(f"Total Arranged: {arrangement.total_arranged}")
    print(f"Unplaced Students: {arrangement.total_students - arrangement.total_arranged}")
    print(f"Constraints Satisfied: {arrangement.constraints_satisfied}")
    
    if arrangement.conflicts:
        print(f"Conflicts: {len(arrangement.conflicts)}")
        print("First few conflicts:")
        for conflict in arrangement.conflicts[:3]:
            print(f"  - {conflict}")


if __name__ == "__main__":
    print("\n" + "🧪 EXAM SEATING ENGINE TEST SUITE 🧪".center(60))
    print("=" * 60)
    
    try:
        # Run all tests
        test_basic_seating()
        test_constraint_validation()
        test_multiple_halls()
        test_insufficient_capacity()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
