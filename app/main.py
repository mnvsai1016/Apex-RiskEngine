"""
FastAPI Application Entry Point:
High-Performance Student Risk Management & Automated Intervention Suite.
"""
import os
import io
import math
from typing import List, Optional
import pandas as pd
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.models import (
    StudentRecord, StudentRiskProfile, AppointmentBookingRequest
)
from app.risk_engine import build_student_risk_profiles, analyze_student_risk, ATTENDANCE_THRESHOLD
from app.timetable_engine import timetable_store
from app.notification_engine import notification_store
from app.call_engine import call_engine
from app.report_engine import generate_weekly_summary_report
from app.sample_data import DEFAULT_STUDENTS, export_sample_files

app = FastAPI(
    title="Apex Student Risk Management Automation",
    description="AI-Powered Student Attendance & Performance Early Warning, Recovery & Telephony Intervention System",
    version="1.0.0"
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
SAMPLE_FILES_DIR = os.path.join(STATIC_DIR, "sample_files")

# Ensure sample files exist on startup
export_sample_files(SAMPLE_FILES_DIR)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# In-memory store for active students
current_students: List[StudentRecord] = [s.model_copy() for s in DEFAULT_STUDENTS]

def normalize_column_name(col: str) -> str:
    return col.strip().lower().replace(" ", "_").replace(".", "").replace("-", "_")

def parse_uploaded_dataframe(df: pd.DataFrame) -> List[StudentRecord]:
    """
    Intelligently maps flexible column names to StudentRecord schema.
    """
    col_map = {normalize_column_name(c): c for c in df.columns}
    parsed: List[StudentRecord] = []

    def get_val(row, candidates, default):
        for cand in candidates:
            if cand in col_map:
                val = row[col_map[cand]]
                if pd.notna(val):
                    return val
        return default

    for idx, row in df.iterrows():
        roll = str(get_val(row, ["roll_number", "roll_no", "roll", "student_id", "id"], f"STU-{idx+1:03d}"))
        name = str(get_val(row, ["name", "student_name", "full_name"], f"Student {roll}"))
        email = str(get_val(row, ["email", "student_email"], f"{roll.lower()}@student.apex.edu"))
        phone = str(get_val(row, ["phone", "mobile", "contact", "phone_number"], "+1 (555) 000-0000"))
        dept = str(get_val(row, ["department", "dept", "branch"], "Computer Science"))
        sem = int(get_val(row, ["semester", "sem"], 4))
        advisor = str(get_val(row, ["advisor_name", "advisor", "faculty_advisor"], "Dr. Aris Thorne"))
        advisor_email = str(get_val(row, ["advisor_email", "advisor_mail"], "aris.thorne@apex.edu"))
        subject = str(get_val(row, ["subject", "course", "subject_name"], "Core Subject"))
        
        attended = int(get_val(row, ["classes_attended", "attended", "present_classes", "present"], 30))
        total = int(get_val(row, ["total_classes", "total", "held_classes", "max_classes"], 40))
        
        t1 = float(get_val(row, ["test1_marks", "test_1", "test1", "midterm_1"], 75.0))
        t2 = float(get_val(row, ["test2_marks", "test_2", "test2", "midterm_2"], 70.0))
        assign = float(get_val(row, ["assignment_marks", "assignment", "assignments", "internal"], 75.0))

        stu = StudentRecord(
            id=f"STU-{idx+1:03d}",
            name=name,
            roll_number=roll,
            email=email,
            phone=phone,
            department=dept,
            semester=sem,
            advisor_name=advisor,
            advisor_email=advisor_email,
            subject=subject,
            classes_attended=attended,
            total_classes=total,
            test1_marks=t1,
            test2_marks=t2,
            assignment_marks=assign
        )
        parsed.append(stu)
    return parsed

# -------------------------------------------------------------
# Web & Dashboard Routes
# -------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    profiles = build_student_risk_profiles(current_students)
    weekly_report = generate_weekly_summary_report(profiles)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "profiles": profiles,
            "timetables": timetable_store.get_all_timetables(),
            "email_logs": notification_store.get_logs(),
            "call_logs": call_engine.get_logs(),
            "report": weekly_report,
            "threshold": ATTENDANCE_THRESHOLD
        }
    )

# -------------------------------------------------------------
# REST API Endpoints
# -------------------------------------------------------------
@app.get("/api/students")
async def get_students():
    profiles = build_student_risk_profiles(current_students)
    return [p.model_dump() for p in profiles]

@app.post("/api/upload")
async def upload_files(
    attendance_file: Optional[UploadFile] = File(None),
    test_results_file: Optional[UploadFile] = File(None),
    combined_file: Optional[UploadFile] = File(None)
):
    global current_students
    uploaded_df = None

    target_file = combined_file or attendance_file or test_results_file
    if not target_file:
        raise HTTPException(status_code=400, detail="Please upload a CSV or Excel file.")

    content = await target_file.read()
    filename = target_file.filename.lower()

    try:
        if filename.endswith(".csv"):
            uploaded_df = pd.read_csv(io.BytesIO(content))
        elif filename.endswith((".xlsx", ".xls")):
            uploaded_df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Invalid format. Only .csv or .xlsx are accepted.")

        if attendance_file and test_results_file and target_file == attendance_file:
            # Handle dual file merge if both provided
            test_content = await test_results_file.read()
            t_df = pd.read_csv(io.BytesIO(test_content)) if test_results_file.filename.endswith(".csv") else pd.read_excel(io.BytesIO(test_content))
            # Merge on roll_number
            merged = pd.merge(uploaded_df, t_df, on="roll_number", how="left")
            uploaded_df = merged

        new_students = parse_uploaded_dataframe(uploaded_df)
        if not new_students:
            raise HTTPException(status_code=400, detail="No valid student records could be parsed.")

        current_students = new_students
        profiles = build_student_risk_profiles(current_students)

        return {
            "success": True,
            "message": f"Successfully ingested {len(new_students)} student records.",
            "total_students": len(new_students),
            "at_risk_count": sum(1 for p in profiles if p.metrics.risk_level != "SAFE")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse file: {str(e)}")

@app.post("/api/reset-demo")
async def reset_demo_data():
    global current_students
    current_students = [s.model_copy() for s in DEFAULT_STUDENTS]
    notification_store.clear_logs()
    call_engine.clear_logs()
    return {"success": True, "message": "Demo data reset successfully with 10 sample students."}

@app.get("/api/timetables")
async def get_timetables():
    return [t.model_dump() for t in timetable_store.get_all_timetables()]

@app.post("/api/book-appointment")
async def book_appointment(req: AppointmentBookingRequest):
    result = timetable_store.book_appointment(req)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result

@app.post("/api/notifications/student/{student_id}")
async def send_student_warning(student_id: str):
    profiles = build_student_risk_profiles(current_students)
    target = next((p for p in profiles if p.student.id == student_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Student not found.")
    
    log = notification_store.send_student_warning_email(target, simulated=True)
    return {"success": True, "log": log.model_dump()}

@app.post("/api/notifications/batch")
async def send_batch_notifications():
    profiles = build_student_risk_profiles(current_students)
    result = notification_store.send_batch_warnings(profiles)
    return {"success": True, **result}

@app.get("/api/notifications/logs")
async def get_notification_logs():
    return [l.model_dump() for l in notification_store.get_logs()]

@app.post("/api/calls/initiate/{student_id}")
async def initiate_student_call(student_id: str):
    profiles = build_student_risk_profiles(current_students)
    target = next((p for p in profiles if p.student.id == student_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Student not found.")
    
    log = call_engine.initiate_call(target)
    return {
        "success": True,
        "call": log.model_dump(),
        "speech_text": log.script
    }

@app.post("/api/calls/batch")
async def initiate_batch_calls():
    profiles = build_student_risk_profiles(current_students)
    result = call_engine.initiate_batch_calls(profiles)
    return {"success": True, **result}

@app.get("/api/calls/logs")
async def get_call_logs():
    return [l.model_dump() for l in call_engine.get_logs()]

@app.get("/api/report/weekly")
async def get_weekly_report():
    profiles = build_student_risk_profiles(current_students)
    report = generate_weekly_summary_report(profiles)
    return report.model_dump()

@app.get("/api/export/report-html", response_class=HTMLResponse)
async def export_report_html():
    profiles = build_student_risk_profiles(current_students)
    report = generate_weekly_summary_report(profiles)
    
    # Render an executive print-ready HTML page
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Institutional Academic Risk Summary - {report.report_week}</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 40px; color: #1e293b; background: #fff; }}
            h1 {{ color: #0f172a; margin-bottom: 4px; }}
            .subtitle {{ color: #64748b; font-size: 14px; margin-bottom: 24px; }}
            .card-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 30px; }}
            .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; }}
            .card .val {{ font-size: 28px; font-weight: 800; color: #0f172a; }}
            .card .lbl {{ font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 28px; font-size: 13px; }}
            th, td {{ border: 1px solid #cbd5e1; padding: 10px 12px; text-align: left; }}
            th {{ background: #f1f5f9; font-weight: 700; color: #334155; }}
            .danger {{ color: #dc2626; font-weight: 700; }}
            .badge-crit {{ background: #fee2e2; color: #991b1b; padding: 2px 8px; border-radius: 4px; font-weight: 700; }}
            .badge-mod {{ background: #fef3c7; color: #92400e; padding: 2px 8px; border-radius: 4px; font-weight: 700; }}
            .actions {{ background: #eff6ff; border-left: 4px solid #2563eb; padding: 16px; border-radius: 6px; }}
            .actions li {{ margin-bottom: 6px; }}
            @media print {{ body {{ padding: 0; }} }}
        </style>
    </head>
    <body>
        <h1>Apex Institute of Technology - Executive Risk Report</h1>
        <div class="subtitle">Generated on {report.generated_at} | Reporting Term: {report.report_week}</div>
        
        <div class="card-grid">
            <div class="card">
                <div class="lbl">Total Enrolled</div>
                <div class="val">{report.total_students}</div>
            </div>
            <div class="card">
                <div class="lbl">At-Risk Total</div>
                <div class="val" style="color: #ea580c;">{report.at_risk_students_count}</div>
            </div>
            <div class="card">
                <div class="lbl">Attendance Deficit (&le;85%)</div>
                <div class="val" style="color: #dc2626;">{report.attendance_at_risk_count}</div>
            </div>
            <div class="card">
                <div class="lbl">Critical Emergency (&lt;75%)</div>
                <div class="val" style="color: #b91c1c;">{report.critical_risk_count}</div>
            </div>
        </div>

        <h2>Department-Wide Risk Breakdown</h2>
        <table>
            <thead>
                <tr>
                    <th>Department</th>
                    <th>Students</th>
                    <th>At-Risk Count</th>
                    <th>Risk Rate</th>
                    <th>Average Attendance</th>
                    <th>Average Marks</th>
                </tr>
            </thead>
            <tbody>
                {"".join([f"<tr><td>{dept}</td><td>{d['total']}</td><td>{d['at_risk']}</td><td class='danger'>{d['risk_percentage']}%</td><td>{d['avg_attendance']}%</td><td>{d['avg_marks']}%</td></tr>" for dept, d in report.department_metrics.items()])}
            </tbody>
        </table>

        <h2>Top Urgent Students Needing Recovery Intervention</h2>
        <table>
            <thead>
                <tr>
                    <th>Roll Number</th>
                    <th>Student Name</th>
                    <th>Department</th>
                    <th>Subject</th>
                    <th>Attendance</th>
                    <th>Recovery Req.</th>
                    <th>Marks Avg</th>
                    <th>Risk Tier</th>
                </tr>
            </thead>
            <tbody>
                {"".join([f"<tr><td>{s['roll_number']}</td><td><strong>{s['name']}</strong></td><td>{s['department']}</td><td>{s['subject']}</td><td class='danger'>{s['attendance']}%</td><td style='font-weight:700; color:#b91c1c;'>{s['consecutive_needed']} Consecutive Classes</td><td>{s['marks_avg']}%</td><td><span class='badge-crit'>{s['risk_level']}</span></td></tr>" for s in report.top_urgent_students])}
            </tbody>
        </table>

        <div class="actions">
            <h3>Institutional Recommended Action Plan</h3>
            <ul>
                {"".join([f"<li>{act}</li>" for act in report.suggested_actions])}
            </ul>
        </div>
        <br>
        <button onclick="window.print()" style="padding: 10px 20px; font-weight: 700; background: #2563eb; color: white; border: none; border-radius: 6px; cursor: pointer;">Print / Save as PDF</button>
    </body>
    </html>
    """
    return html

@app.get("/api/download/{file_name}")
async def download_sample(file_name: str):
    file_path = os.path.join(SAMPLE_FILES_DIR, file_name)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=file_name)
    raise HTTPException(status_code=404, detail="Sample file not found.")
