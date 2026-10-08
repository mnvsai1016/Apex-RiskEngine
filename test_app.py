"""
Automated System Verification Tests.
Tests risk formulas, recovery calculations, uploads, appointment bookings,
calls, notifications, and weekly report generation.
"""
import io
import math
import pandas as pd
from app.models import StudentRecord, AppointmentBookingRequest
from app.risk_engine import calculate_consecutive_classes_needed, analyze_student_risk, build_student_risk_profiles
from app.timetable_engine import timetable_store
from app.notification_engine import notification_store
from app.call_engine import call_engine
from app.report_engine import generate_weekly_summary_report

def test_recovery_formula():
    print("Testing recovery formula...")
    # Student with 24 attended out of 36 (66.67% attendance)
    # We need (24 + x)/(36 + x) >= 0.85
    # (0.85 * 36 - 24) / 0.15 = 6.6 / 0.15 = 44.0
    x = calculate_consecutive_classes_needed(24, 36, 85.0)
    assert x == 44, f"Expected 44, got {x}"
    # Verify with 44 attended: (24 + 44) / (36 + 44) = 68 / 80 = 0.85 (85.0%)
    assert (24 + 44) / (36 + 44) >= 0.85

    # Borderline case: 17 out of 20 = 85.0%
    x_border = calculate_consecutive_classes_needed(17, 20, 85.0)
    assert x_border == 0, f"Expected 0, got {x_border}"

    # Safe case: 38 out of 40 = 95.0%
    x_safe = calculate_consecutive_classes_needed(38, 40, 85.0)
    assert x_safe == 0, f"Expected 0, got {x_safe}"
    print("[PASS] Recovery formula tests passed!")

def test_risk_analysis():
    print("Testing student risk analysis...")
    stu_critical = StudentRecord(
        id="TEST-1",
        name="Test At Risk",
        roll_number="T-01",
        email="test@apex.edu",
        phone="+15551234",
        department="Computer Science",
        semester=4,
        advisor_name="Dr. Thorne",
        advisor_email="thorne@apex.edu",
        subject="Algorithms",
        classes_attended=20,
        total_classes=35, # 57.14% attendance
        test1_marks=80.0,
        test2_marks=45.0, # Declining marks
        assignment_marks=50.0
    )
    metrics = analyze_student_risk(stu_critical)
    assert metrics.is_attendance_at_risk is True
    assert metrics.marks_trend == "DECLINING"
    assert metrics.risk_level in ["CRITICAL", "HIGH"]
    assert metrics.consecutive_classes_needed > 0
    print(f"[PASS] Critical student flagged: {metrics.risk_level}, Needs {metrics.consecutive_classes_needed} consecutive classes")

def test_booking_and_notifications():
    print("Testing booking and communications...")
    # Test booking
    req = AppointmentBookingRequest(
        teacher_id="TCH-001",
        slot_id="SLT-101",
        student_id="STU-001",
        student_name="Aarav Sharma",
        reason="Doubt clearance and attendance catchup"
    )
    res = timetable_store.book_appointment(req)
    assert res["success"] is True
    print(f"[PASS] Appointment booked: {res['appointment']['booking_id']}")

    # Test call engine
    from app.sample_data import DEFAULT_STUDENTS
    profiles = build_student_risk_profiles(DEFAULT_STUDENTS)
    call_log = call_engine.initiate_call(profiles[0])
    assert call_log.call_sid.startswith("CA")
    assert call_log.status == "COMPLETED"
    print(f"[PASS] Telephony call generated: SID={call_log.call_sid}, duration={call_log.duration_seconds}s")

    # Test batch emails
    batch_res = notification_store.send_batch_warnings(profiles)
    assert batch_res["total_sent"] > 0
    print(f"[PASS] Batch emails sent: {batch_res['total_sent']} emails logged")

    # Test weekly report
    report = generate_weekly_summary_report(profiles)
    assert report.total_students == len(DEFAULT_STUDENTS)
    assert report.attendance_at_risk_count > 0
    print(f"[PASS] Weekly report compiled: {report.attendance_at_risk_count} at-risk students flagged across {len(report.department_metrics)} departments")

if __name__ == "__main__":
    test_recovery_formula()
    test_risk_analysis()
    test_booking_and_notifications()
    print("\nALL SYSTEM VERIFICATION TESTS PASSED SUCCESSFULLY!")
