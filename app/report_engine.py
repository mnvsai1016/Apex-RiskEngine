"""
Weekly Summary Report Engine:
Generates comprehensive department-wide and subject-wide risk summaries,
trend analysis, and institutional intervention action plans.
"""
from datetime import datetime
from typing import List, Dict, Any
from app.models import StudentRiskProfile, WeeklyReportSummary

def generate_weekly_summary_report(profiles: List[StudentRiskProfile], week_label: str = "Week 10 - Academic Term 2026") -> WeeklyReportSummary:
    total_students = len(profiles)
    at_risk_profiles = [p for p in profiles if p.metrics.risk_level != "SAFE"]
    attendance_at_risk = [p for p in profiles if p.metrics.is_attendance_at_risk]
    performance_at_risk = [p for p in profiles if p.metrics.is_performance_at_risk]
    critical_risk = [p for p in profiles if p.metrics.risk_level == "CRITICAL"]

    # 1. Department Breakdown
    dept_metrics: Dict[str, Dict[str, Any]] = {}
    for p in profiles:
        dept = p.student.department
        if dept not in dept_metrics:
            dept_metrics[dept] = {
                "total": 0,
                "at_risk": 0,
                "critical": 0,
                "attendance_sum": 0.0,
                "marks_sum": 0.0
            }
        dept_metrics[dept]["total"] += 1
        dept_metrics[dept]["attendance_sum"] += p.metrics.attendance_pct
        dept_metrics[dept]["marks_sum"] += p.metrics.test_avg_pct
        if p.metrics.risk_level != "SAFE":
            dept_metrics[dept]["at_risk"] += 1
        if p.metrics.risk_level == "CRITICAL":
            dept_metrics[dept]["critical"] += 1

    # Normalize averages
    for dept, data in dept_metrics.items():
        total = data["total"]
        data["avg_attendance"] = round(data["attendance_sum"] / total, 1) if total else 0.0
        data["avg_marks"] = round(data["marks_sum"] / total, 1) if total else 0.0
        data["risk_percentage"] = round((data["at_risk"] / total) * 100.0, 1) if total else 0.0

    # 2. Subject Breakdown
    subj_metrics: Dict[str, Dict[str, Any]] = {}
    for p in profiles:
        subj = p.student.subject
        if subj not in subj_metrics:
            subj_metrics[subj] = {
                "total": 0,
                "at_risk": 0,
                "attendance_sum": 0.0,
                "marks_sum": 0.0,
                "declining_marks_count": 0
            }
        subj_metrics[subj]["total"] += 1
        subj_metrics[subj]["attendance_sum"] += p.metrics.attendance_pct
        subj_metrics[subj]["marks_sum"] += p.metrics.test_avg_pct
        if p.metrics.risk_level != "SAFE":
            subj_metrics[subj]["at_risk"] += 1
        if p.metrics.marks_trend == "DECLINING":
            subj_metrics[subj]["declining_marks_count"] += 1

    for subj, data in subj_metrics.items():
        total = data["total"]
        data["avg_attendance"] = round(data["attendance_sum"] / total, 1) if total else 0.0
        data["avg_marks"] = round(data["marks_sum"] / total, 1) if total else 0.0
        data["risk_percentage"] = round((data["at_risk"] / total) * 100.0, 1) if total else 0.0

    # 3. Top urgent students needing immediate intervention
    sorted_urgent = sorted(
        [p for p in profiles if p.metrics.risk_level in ["CRITICAL", "HIGH"]],
        key=lambda x: (x.metrics.attendance_pct, -x.metrics.risk_score)
    )[:5]

    top_urgent_list = [
        {
            "id": p.student.id,
            "name": p.student.name,
            "roll_number": p.student.roll_number,
            "department": p.student.department,
            "subject": p.student.subject,
            "attendance": p.metrics.attendance_pct,
            "consecutive_needed": p.metrics.consecutive_classes_needed,
            "marks_avg": p.metrics.test_avg_pct,
            "risk_level": p.metrics.risk_level,
            "risk_score": p.metrics.risk_score
        }
        for p in sorted_urgent
    ]

    # 4. Institutional Action Items
    actions = [
        f"Conduct mandatory counselor reviews for {len(critical_risk)} students currently at CRITICAL status (< 75% attendance).",
        f"Enforce consecutive class attendance monitoring across {len(attendance_at_risk)} students with sub-85% records.",
        "Open additional teacher office-hour slots for Data Structures & Algorithms and Engineering Mathematics III.",
        "Dispatch automated weekly warnings to parents and department heads.",
        "Initiate automated phone outreach and warning emails for pending cases."
    ]

    return WeeklyReportSummary(
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        report_week=week_label,
        total_students=total_students,
        at_risk_students_count=len(at_risk_profiles),
        attendance_at_risk_count=len(attendance_at_risk),
        performance_at_risk_count=len(performance_at_risk),
        critical_risk_count=len(critical_risk),
        department_metrics=dept_metrics,
        subject_metrics=subj_metrics,
        top_urgent_students=top_urgent_list,
        suggested_actions=actions
    )
