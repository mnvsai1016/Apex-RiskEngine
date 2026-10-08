"""
Teacher Timetable and Student Appointment Booking Engine.
Allows at-risk students to discover teacher office hours and reserve counseling slots.
"""
from typing import List, Optional, Dict, Any
from app.models import TeacherTimetable, TimeSlot, AppointmentBookingRequest

INITIAL_TEACHERS: List[TeacherTimetable] = [
    TeacherTimetable(
        teacher_id="TCH-001",
        teacher_name="Dr. Aris Thorne",
        department="Computer Science & Engineering",
        subject="Data Structures & Algorithms",
        email="aris.thorne@apex.edu",
        office_room="Block C, Room 302",
        slots=[
            TimeSlot(slot_id="SLT-101", day="Monday", start_time="10:00 AM", end_time="11:00 AM", status="FREE"),
            TimeSlot(slot_id="SLT-102", day="Monday", start_time="02:00 PM", end_time="03:00 PM", status="BUSY"),
            TimeSlot(slot_id="SLT-103", day="Tuesday", start_time="11:30 AM", end_time="12:30 PM", status="FREE"),
            TimeSlot(slot_id="SLT-104", day="Wednesday", start_time="03:00 PM", end_time="04:00 PM", status="FREE"),
            TimeSlot(slot_id="SLT-105", day="Thursday", start_time="09:30 AM", end_time="10:30 AM", status="BUSY"),
            TimeSlot(slot_id="SLT-106", day="Friday", start_time="02:30 PM", end_time="03:30 PM", status="FREE")
        ]
    ),
    TeacherTimetable(
        teacher_id="TCH-002",
        teacher_name="Prof. Sarah Jenkins",
        department="Computer Science & Engineering",
        subject="Operating Systems",
        email="sarah.jenkins@apex.edu",
        office_room="Block C, Room 214",
        slots=[
            TimeSlot(slot_id="SLT-201", day="Monday", start_time="09:00 AM", end_time="10:00 AM", status="FREE"),
            TimeSlot(slot_id="SLT-202", day="Tuesday", start_time="01:30 PM", end_time="02:30 PM", status="FREE"),
            TimeSlot(slot_id="SLT-203", day="Wednesday", start_time="10:00 AM", end_time="11:00 AM", status="BUSY"),
            TimeSlot(slot_id="SLT-204", day="Thursday", start_time="02:00 PM", end_time="03:00 PM", status="FREE"),
            TimeSlot(slot_id="SLT-205", day="Friday", start_time="11:00 AM", end_time="12:00 PM", status="FREE")
        ]
    ),
    TeacherTimetable(
        teacher_id="TCH-003",
        teacher_name="Dr. Vikram Patel",
        department="Electronics & Communication",
        subject="Digital Signal Processing",
        email="vikram.patel@apex.edu",
        office_room="Block B, Room 118",
        slots=[
            TimeSlot(slot_id="SLT-301", day="Monday", start_time="03:00 PM", end_time="04:00 PM", status="FREE"),
            TimeSlot(slot_id="SLT-302", day="Wednesday", start_time="11:00 AM", end_time="12:00 PM", status="FREE"),
            TimeSlot(slot_id="SLT-303", day="Thursday", start_time="04:00 PM", end_time="05:00 PM", status="FREE"),
            TimeSlot(slot_id="SLT-304", day="Friday", start_time="10:00 AM", end_time="11:00 AM", status="BUSY")
        ]
    ),
    TeacherTimetable(
        teacher_id="TCH-004",
        teacher_name="Prof. Meera Nair",
        department="Information Technology",
        subject="Database Management Systems",
        email="meera.nair@apex.edu",
        office_room="Block D, Room 405",
        slots=[
            TimeSlot(slot_id="SLT-401", day="Tuesday", start_time="10:00 AM", end_time="11:00 AM", status="FREE"),
            TimeSlot(slot_id="SLT-402", day="Wednesday", start_time="02:00 PM", end_time="03:00 PM", status="FREE"),
            TimeSlot(slot_id="SLT-403", day="Friday", start_time="03:30 PM", end_time="04:30 PM", status="FREE")
        ]
    ),
    TeacherTimetable(
        teacher_id="TCH-005",
        teacher_name="Dr. Rajesh Kumar",
        department="Mathematics & Basic Sciences",
        subject="Engineering Mathematics III",
        email="rajesh.kumar@apex.edu",
        office_room="Block A, Room 102",
        slots=[
            TimeSlot(slot_id="SLT-501", day="Monday", start_time="11:30 AM", end_time="12:30 PM", status="FREE"),
            TimeSlot(slot_id="SLT-502", day="Tuesday", start_time="03:00 PM", end_time="04:00 PM", status="FREE"),
            TimeSlot(slot_id="SLT-503", day="Thursday", start_time="11:00 AM", end_time="12:00 PM", status="FREE")
        ]
    )
]

class TimetableStore:
    def __init__(self):
        # Deep copy initial timetables
        self.timetables: List[TeacherTimetable] = [
            TeacherTimetable.model_validate(t.model_dump()) for t in INITIAL_TEACHERS
        ]
        self.appointments_history: List[Dict[str, Any]] = []

    def get_all_timetables(self) -> List[TeacherTimetable]:
        return self.timetables

    def get_teacher_by_id(self, teacher_id: str) -> Optional[TeacherTimetable]:
        for t in self.timetables:
            if t.teacher_id == teacher_id:
                return t
        return None

    def book_appointment(self, req: AppointmentBookingRequest) -> Dict[str, Any]:
        teacher = self.get_teacher_by_id(req.teacher_id)
        if not teacher:
            return {"success": False, "message": "Teacher not found"}
        
        target_slot = None
        for s in teacher.slots:
            if s.slot_id == req.slot_id:
                target_slot = s
                break
                
        if not target_slot:
            return {"success": False, "message": "Time slot not found"}
            
        if target_slot.status != "FREE":
            return {"success": False, "message": f"This slot is currently {target_slot.status}. Please pick a FREE slot."}
            
        target_slot.status = "BOOKED"
        target_slot.booked_by_student_id = req.student_id
        target_slot.booked_by_student_name = req.student_name

        booking_record = {
            "booking_id": f"APPT-{len(self.appointments_history)+1:04d}",
            "teacher_id": teacher.teacher_id,
            "teacher_name": teacher.teacher_name,
            "teacher_email": teacher.email,
            "subject": teacher.subject,
            "office_room": teacher.office_room,
            "slot_id": target_slot.slot_id,
            "day": target_slot.day,
            "time": f"{target_slot.start_time} - {target_slot.end_time}",
            "student_id": req.student_id,
            "student_name": req.student_name,
            "reason": req.reason,
            "calendar_url": f"https://calendar.google.com/calendar/render?action=TEMPLATE&text=Academic+Advising+{req.student_name}+with+{teacher.teacher_name}&location={teacher.office_room}"
        }
        self.appointments_history.append(booking_record)
        return {"success": True, "appointment": booking_record}

timetable_store = TimetableStore()
