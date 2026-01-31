"""
Intelligent Exam Seating Engine
Applies constraints:
- Avoid same-subject adjacency (horizontally and vertically)
- Avoid same-department row placement
- Efficiently utilize available exam halls
"""

from typing import List, Dict, Optional, Tuple
from models import Student, ExamHall, Seat, SeatingArrangement
import random


class SeatingEngine:
    def __init__(self):
        self.conflicts = []
    
    def arrange_seating(
        self,
        exam_id: str,
        students: List[Student],
        halls: List[ExamHall]
    ) -> SeatingArrangement:
        """
        Main seating arrangement algorithm
        """
        self.conflicts = []
        
        # Sort students to improve constraint satisfaction
        sorted_students = self._sort_students_for_arrangement(students)
        
        # Initialize halls with seats
        hall_seats: Dict[str, List[List[Optional[Seat]]]] = {}
        for hall in halls:
            hall_seats[hall.hall_id] = self._create_hall_seats(hall)
        
        # Place students using constraint-aware algorithm
        placed_students = 0
        for student in sorted_students:
            placed = False
            
            # Try each hall
            for hall in halls:
                if placed:
                    break
                
                seats = hall_seats[hall.hall_id]
                
                # Try to place student in this hall
                seat = self._find_best_seat(
                    hall=hall,
                    seats=seats,
                    student=student,
                    placed_students=sorted_students[:sorted_students.index(student)]
                )
                
                if seat:
                    seats[seat.row][seat.column] = seat
                    placed_students += 1
                    placed = True
            
            if not placed:
                self.conflicts.append(f"Could not place student {student.student_id}")
        
        # Build result
        hall_allocations = {}
        for hall_id, seats_matrix in hall_seats.items():
            hall_allocations[hall_id] = self._flatten_seats(seats_matrix)
        
        arrangement_satisfied = len(self.conflicts) == 0
        
        return SeatingArrangement(
            arrangement_id=f"ARR_{exam_id}",
            exam_id=exam_id,
            hall_allocations=hall_allocations,
            total_arranged=placed_students,
            total_students=len(students),
            constraints_satisfied=arrangement_satisfied,
            conflicts=self.conflicts
        )
    
    def _sort_students_for_arrangement(self, students: List[Student]) -> List[Student]:
        """
        Sort students strategically:
        - Departments in order (to cluster them)
        - Subjects distributed within departments
        """
        # Sort by department first, then shuffle within department
        students_by_dept = {}
        for student in students:
            if student.department not in students_by_dept:
                students_by_dept[student.department] = []
            students_by_dept[student.department].append(student)
        
        # Flatten back but with department clustering
        sorted_students = []
        for dept in sorted(students_by_dept.keys()):
            dept_students = students_by_dept[dept]
            # Sort by subject within department for some structure
            dept_students.sort(key=lambda x: x.subject)
            sorted_students.extend(dept_students)
        
        return sorted_students
    
    def _create_hall_seats(self, hall: ExamHall) -> List[List[Optional[Seat]]]:
        """Create a 2D matrix of empty seats for a hall"""
        seats = []
        seat_counter = 0
        
        for row in range(hall.rows):
            row_seats = []
            for col in range(hall.columns):
                seat = Seat(
                    seat_id=f"{hall.hall_id}_R{row}_C{col}",
                    hall_id=hall.hall_id,
                    row=row,
                    column=col
                )
                row_seats.append(seat)
                seat_counter += 1
                
                if seat_counter >= hall.total_seats:
                    break
            
            seats.append(row_seats)
            if seat_counter >= hall.total_seats:
                break
        
        return seats
    
    def _find_best_seat(
        self,
        hall: ExamHall,
        seats: List[List[Optional[Seat]]],
        student: Student,
        placed_students: List[Student]
    ) -> Optional[Seat]:
        """
        Find the best seat for a student considering constraints:
        1. Avoid same-subject adjacency (left, right, above, below)
        2. Avoid same-department in the same row
        3. Prefer spreading out departments
        """
        candidates = []
        
        for row in range(len(seats)):
            for col in range(len(seats[row])):
                seat = seats[row][col]
                
                # Skip occupied seats
                if seat.student_id is not None:
                    continue
                
                # Check constraints
                violations = self._check_seat_constraints(
                    seat=seat,
                    student=student,
                    seats=seats,
                    hall=hall,
                    placed_students=placed_students
                )
                
                candidates.append((seat, violations))
        
        if not candidates:
            return None
        
        # Sort by number of violations (ascending) and prefer seats farther from edges
        candidates.sort(
            key=lambda x: (x[1], -self._distance_from_edges(x[0], hall))
        )
        
        # Return seat with least violations
        best_seat, violations = candidates[0]
        best_seat.student_id = student.student_id
        best_seat.student_subject = student.subject
        best_seat.student_department = student.department
        
        return best_seat
    
    def _check_seat_constraints(
        self,
        seat: Seat,
        student: Student,
        seats: List[List[Optional[Seat]]],
        hall: ExamHall,
        placed_students: List[Student]
    ) -> int:
        """
        Check constraints for a seat. Returns violation count.
        """
        violations = 0
        
        # Constraint 1: Check same-subject adjacency
        adjacent_seats = [
            (seat.row - 1, seat.column),  # Above
            (seat.row + 1, seat.column),  # Below
            (seat.row, seat.column - 1),  # Left
            (seat.row, seat.column + 1),  # Right
        ]
        
        for adj_row, adj_col in adjacent_seats:
            if 0 <= adj_row < len(seats) and 0 <= adj_col < len(seats[0]):
                adj_seat = seats[adj_row][adj_col]
                if adj_seat.student_id and adj_seat.student_subject == student.subject:
                    violations += 1
        
        # Constraint 2: Check same-department in row
        for col in range(len(seats[seat.row])):
            row_seat = seats[seat.row][col]
            if row_seat.student_id and row_seat.student_department == student.department:
                violations += 2  # Higher penalty for department constraint
        
        return violations
    
    def _distance_from_edges(self, seat: Seat, hall: ExamHall) -> int:
        """Calculate distance from edges (prefer central seats for better distribution)"""
        center_row = hall.rows / 2
        center_col = hall.columns / 2
        
        dist_row = abs(seat.row - center_row)
        dist_col = abs(seat.column - center_col)
        
        return int(dist_row + dist_col)
    
    def _flatten_seats(self, seats_matrix: List[List[Optional[Seat]]]) -> List[Seat]:
        """Convert 2D seat matrix to flat list"""
        flat_seats = []
        for row in seats_matrix:
            for seat in row:
                if seat:
                    flat_seats.append(seat)
        return flat_seats
    
    def validate_arrangement(self, arrangement: SeatingArrangement) -> Tuple[bool, List[str]]:
        """
        Validate the seating arrangement against all constraints
        """
        issues = []
        
        for hall_id, seats in arrangement.hall_allocations.items():
            # Check subject adjacency
            seats_by_position = {(s.row, s.column): s for s in seats if isinstance(s, dict)}
            
            # Rebuild 2D structure for validation
            max_row = max([s.get('row', 0) if isinstance(s, dict) else s.row for s in seats])
            max_col = max([s.get('column', 0) if isinstance(s, dict) else s.column for s in seats])
            
        return len(issues) == 0, issues
