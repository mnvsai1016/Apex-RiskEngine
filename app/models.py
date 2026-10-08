"""
Data models for Student Risk Management System.
"""
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

class StudentRecord(BaseModel):
    id: str
    name: str
    roll_number: str
    email: str
    phone: str
    department: str
    semester: int
    advisor_name: str
    advisor_email: str
    subject: str
    classes_attended: int
    total_classes: int
    test1_marks: float  # out of 100
    test2_marks: float  # out of 100
    assignment_marks: float  # out of 100

class RiskMetrics(BaseModel):
    attendance_pct: float
    test_avg_pct: float
    marks_trend: str  # "DECLINING", "IMPROVING", "STABLE"
    marks_change: float
    is_attendance_at_risk: bool  # <= 85%
    is_performance_at_risk: bool  # <= 85% or marks < 50%
    consecutive_classes_needed: int
    risk_level: str  # "CRITICAL", "HIGH", "MODERATE", "SAFE"
    risk_score: float  # 0 to 100 index
    intervention_required: bool
    reasons: List[str]

class StudentRiskProfile(BaseModel):
    student: StudentRecord
    metrics: RiskMetrics

class TimeSlot(BaseModel):
    slot_id: str
    day: str
    start_time: str
    end_time: str
    status: str  # "FREE", "BUSY", "BOOKED"
    booked_by_student_id: Optional[str] = None
    booked_by_student_name: Optional[str] = None

class TeacherTimetable(BaseModel):
    teacher_id: str
    teacher_name: str
    department: str
    subject: str
    email: str
    office_room: str
    slots: List[TimeSlot]

class CreateSlotRequest(BaseModel):
    day: str
    start_time: str
    end_time: str
    status: str = "FREE"

class CreateTeacherRequest(BaseModel):
    teacher_name: str
    department: str
    subject: str
    email: str
    office_room: str
    slots: Optional[List[CreateSlotRequest]] = None

class AppointmentBookingRequest(BaseModel):
    teacher_id: str
    slot_id: str
    student_id: str
    student_name: str
    reason: str

class EmailLog(BaseModel):
    id: str
    recipient_email: str
    recipient_name: str
    recipient_role: str  # "STUDENT", "ADVISOR", "TEACHER"
    subject: str
    body_html: str
    timestamp: str
    status: str  # "SENT", "SIMULATED", "FAILED"
    simulated: bool = True

class CallLog(BaseModel):
    call_sid: str
    student_id: str
    student_name: str
    phone_number: str
    timestamp: str
    status: str  # "COMPLETED", "INITIATED", "RINGING", "IN_PROGRESS", "FAILED"
    duration_seconds: int
    script: str
    transcript: str
    provider: str  # "BROWSER_SPEECH", "TWILIO_SIMULATED", "TWILIO_LIVE"
    consecutive_classes_needed: int
    current_attendance: float

class WeeklyReportSummary(BaseModel):
    generated_at: str
    report_week: str
    total_students: int
    at_risk_students_count: int
    attendance_at_risk_count: int
    performance_at_risk_count: int
    critical_risk_count: int
    department_metrics: Dict[str, Dict[str, Any]]
    subject_metrics: Dict[str, Dict[str, Any]]
    top_urgent_students: List[Dict[str, Any]]
    suggested_actions: List[str]
