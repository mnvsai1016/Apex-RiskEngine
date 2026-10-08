"""
Comprehensive integration verification suite using FastAPI/Starlette TestClient.
Executes synchronously in-memory, testing all routes, file uploads, recovery calculations,
telephony dispatches, email logs, appointment reservations, and report exports.
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def run_all_tests():
    print("Starting Comprehensive System Integration Verification...")

    # 1. Root Dashboard HTML
    r_root = client.get("/")
    assert r_root.status_code == 200
    assert "Apex RiskEngine" in r_root.text
    print(f"[PASS] GET / (Dashboard HTML loaded, {len(r_root.text)} bytes)")

    # 2. Students API
    r_stu = client.get("/api/students")
    assert r_stu.status_code == 200
    students = r_stu.json()
    assert len(students) >= 10
    print(f"[PASS] GET /api/students: {len(students)} student risk profiles loaded")

    # 3. File Upload Simulation (Combined File)
    with open("static/sample_files/combined_student_data.csv", "rb") as f:
        r_up = client.post("/api/upload", files={"combined_file": ("combined.csv", f, "text/csv")})
    assert r_up.status_code == 200
    assert r_up.json()["success"] is True
    print(f"[PASS] POST /api/upload: {r_up.json()['message']}")

    # 4. Batch Email Warnings
    r_email = client.post("/api/notifications/batch")
    assert r_email.status_code == 200
    assert r_email.json()["success"] is True
    total_sent = r_email.json()["total_sent"]
    print(f"[PASS] POST /api/notifications/batch: Dispatched {total_sent} notifications")

    # 5. Email Logs Retrieval
    r_elogs = client.get("/api/notifications/logs")
    assert r_elogs.status_code == 200
    logs = r_elogs.json()
    assert len(logs) > 0
    print(f"[PASS] GET /api/notifications/logs: {len(logs)} logs retrieved")

    # 6. Single Student Warning Email
    r_single_email = client.post("/api/notifications/student/STU-001")
    assert r_single_email.status_code == 200
    print(f"[PASS] POST /api/notifications/student/STU-001: Sent (Log ID {r_single_email.json()['log']['id']})")

    # 7. Single Automated Call Initiation
    r_call = client.post("/api/calls/initiate/STU-001")
    assert r_call.status_code == 200
    call_data = r_call.json()
    assert call_data["success"] is True
    assert call_data["call"]["call_sid"].startswith("CA")
    print(f"[PASS] POST /api/calls/initiate/STU-001: Call placed (SID: {call_data['call']['call_sid']})")

    # 8. Batch Calls Trigger
    r_bcall = client.post("/api/calls/batch")
    assert r_bcall.status_code == 200
    b_data = r_bcall.json()
    print(f"[PASS] POST /api/calls/batch: Triggered {b_data['total_calls_triggered']} automated calls")

    # 9. Call Logs Retrieval
    r_clogs = client.get("/api/calls/logs")
    assert r_clogs.status_code == 200
    assert len(r_clogs.json()) > 0
    print(f"[PASS] GET /api/calls/logs: {len(r_clogs.json())} telephony logs recorded")

    # 10. Timetables & Booking
    r_tt = client.get("/api/timetables")
    assert r_tt.status_code == 200
    timetables = r_tt.json()
    assert len(timetables) >= 5
    
    first_teacher = timetables[0]
    free_slot = [s for s in first_teacher["slots"] if s["status"] == "FREE"][0]
    
    r_book = client.post("/api/book-appointment", json={
        "teacher_id": first_teacher["teacher_id"],
        "slot_id": free_slot["slot_id"],
        "student_id": "STU-001",
        "student_name": "Aarav Sharma",
        "reason": "Attendance counseling and doubt clearance"
    })
    assert r_book.status_code == 200
    booking_res = r_book.json()
    assert booking_res["success"] is True
    print(f"[PASS] POST /api/book-appointment: Booked {booking_res['appointment']['booking_id']} with {first_teacher['teacher_name']}")

    # 11. Weekly Dean's Summary Report API
    r_rep = client.get("/api/report/weekly")
    assert r_rep.status_code == 200
    rep_data = r_rep.json()
    assert "department_metrics" in rep_data
    assert "subject_metrics" in rep_data
    print(f"[PASS] GET /api/report/weekly: {rep_data['at_risk_students_count']} at-risk students analyzed")

    # 12. Printable HTML Report
    r_rep_html = client.get("/api/export/report-html")
    assert r_rep_html.status_code == 200
    assert "Apex Institute of Technology - Executive Risk Report" in r_rep_html.text
    print(f"[PASS] GET /api/export/report-html: Printable executive view verified ({len(r_rep_html.text)} bytes)")

    # 13. Sample File Downloads
    for fname in ["attendance_sample.csv", "test_results_sample.csv", "combined_student_data.csv"]:
        r_dl = client.get(f"/api/download/{fname}")
        assert r_dl.status_code == 200
        print(f"[PASS] GET /api/download/{fname}: Verified download ({len(r_dl.content)} bytes)")

    # 14. Reset Demo Data
    r_reset = client.post("/api/reset-demo")
    assert r_reset.status_code == 200
    print(f"[PASS] POST /api/reset-demo: Demo state reset successfully")

    print("\n" + "="*70)
    print("SUCCESS: ALL 14 TEST CASES & ENDPOINTS PASSED WITH 100% ACCURACY!")
    print("="*70)

if __name__ == "__main__":
    run_all_tests()
