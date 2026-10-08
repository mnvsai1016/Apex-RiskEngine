"""
Notification Engine: Generates personalized warning emails to at-risk students
and escalation alerts to faculty advisors and subject teachers.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid
from app.models import StudentRiskProfile, EmailLog

class NotificationStore:
    def __init__(self):
        self.email_logs: List[EmailLog] = []

    def get_logs(self) -> List[EmailLog]:
        return self.email_logs

    def clear_logs(self):
        self.email_logs.clear()

    def send_student_warning_email(self, profile: StudentRiskProfile, simulated: bool = True) -> EmailLog:
        s = profile.student
        m = profile.metrics
        
        recovery_guidance = (
            f"You are required to attend the next <strong>{m.consecutive_classes_needed} consecutive classes</strong> "
            f"without any absence to bring your attendance back to the mandatory 85% threshold."
            if m.consecutive_classes_needed > 0 else
            "Your attendance is currently on borderline. Maintain full attendance in upcoming lectures."
        )

        marks_summary = (
            f"Test 1: {s.test1_marks}%, Test 2: {s.test2_marks}%, Assignments: {s.assignment_marks}% "
            f"(Average: {m.test_avg_pct}% | Trajectory: {m.marks_trend})"
        )

        html_body = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff;">
            <div style="background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%); padding: 18px 24px; border-radius: 8px; color: white; margin-bottom: 20px;">
                <h2 style="margin: 0; font-size: 20px;">Academic Warning: Attendance & Performance Alert</h2>
                <p style="margin: 4px 0 0; font-size: 13px; opacity: 0.9;">Apex Institute Academic Advisory Council</p>
            </div>
            
            <p>Dear <strong>{s.name}</strong> (Roll No: <code>{s.roll_number}</code>),</p>
            
            <p>This automated notice informs you that your academic standing in <strong>{s.subject}</strong> ({s.department}) has fallen below our institution's minimum required threshold of <strong>85%</strong>.</p>
            
            <table style="width: 100%; border-collapse: collapse; margin: 18px 0; font-size: 14px;">
                <tr style="background: #f8fafc; border-bottom: 1px solid #e2e8f0;">
                    <td style="padding: 10px; font-weight: 600; color: #475569;">Current Attendance</td>
                    <td style="padding: 10px; font-weight: 700; color: #dc2626;">{m.attendance_pct}% ({s.classes_attended}/{s.total_classes} classes)</td>
                </tr>
                <tr style="background: #ffffff; border-bottom: 1px solid #e2e8f0;">
                    <td style="padding: 10px; font-weight: 600; color: #475569;">Mandatory Target</td>
                    <td style="padding: 10px; font-weight: 600; color: #16a34a;">85.00%</td>
                </tr>
                <tr style="background: #fef2f2; border-bottom: 1px solid #fecaca;">
                    <td style="padding: 10px; font-weight: 600; color: #991b1b;">Recovery Requirement</td>
                    <td style="padding: 10px; font-weight: 700; color: #b91c1c;">{m.consecutive_classes_needed} Consecutive Classes Needed</td>
                </tr>
                <tr style="background: #f8fafc; border-bottom: 1px solid #e2e8f0;">
                    <td style="padding: 10px; font-weight: 600; color: #475569;">Academic Performance</td>
                    <td style="padding: 10px; color: #334155;">{marks_summary}</td>
                </tr>
                <tr style="background: #ffffff; border-bottom: 1px solid #e2e8f0;">
                    <td style="padding: 10px; font-weight: 600; color: #475569;">Risk Severity</td>
                    <td style="padding: 10px; font-weight: 700; color: #ea580c;">LEVEL: {m.risk_level} (Index: {m.risk_score}/100)</td>
                </tr>
            </table>

            <div style="background: #fffbeb; border-left: 4px solid #f59e0b; padding: 12px 16px; margin: 18px 0; border-radius: 4px;">
                <strong style="color: #92400e;">Action Required:</strong>
                <p style="margin: 4px 0 0; color: #78350f; font-size: 13.5px;">
                    {recovery_guidance} Please schedule an in-person academic counseling appointment with your course instructor or your Faculty Advisor (<strong>{s.advisor_name}</strong> - <code>{s.advisor_email}</code>).
                </p>
            </div>

            <p style="font-size: 13px; color: #64748b; margin-top: 24px; border-top: 1px solid #e2e8f0; padding-top: 12px;">
                * This is a system-generated alert from the Student Risk Management Automation Suite. Failure to recover attendance may result in semester debarment.
            </p>
        </div>
        """

        log = EmailLog(
            id=f"EML-{uuid.uuid4().hex[:8].upper()}",
            recipient_email=s.email,
            recipient_name=s.name,
            recipient_role="STUDENT",
            subject=f"URGENT: Academic Risk & Attendance Recovery Warning ({s.subject})",
            body_html=html_body,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            status="SIMULATED" if simulated else "SENT",
            simulated=simulated
        )
        self.email_logs.insert(0, log)
        return log

    def send_faculty_advisor_alert(self, advisor_name: str, advisor_email: str, advisee_profiles: List[StudentRiskProfile], simulated: bool = True) -> EmailLog:
        rows_html = ""
        for p in advisee_profiles:
            rows_html += f"""
            <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 8px 10px;">{p.student.name} ({p.student.roll_number})</td>
                <td style="padding: 8px 10px;">{p.student.subject}</td>
                <td style="padding: 8px 10px; font-weight: 700; color: #dc2626;">{p.metrics.attendance_pct}%</td>
                <td style="padding: 8px 10px; font-weight: 700; color: #b91c1c;">{p.metrics.consecutive_classes_needed} classes</td>
                <td style="padding: 8px 10px;">{p.metrics.test_avg_pct}% ({p.metrics.marks_trend})</td>
                <td style="padding: 8px 10px;"><span style="padding: 2px 8px; border-radius: 9999px; background: #fee2e2; color: #991b1b; font-size: 11px; font-weight: 700;">{p.metrics.risk_level}</span></td>
            </tr>
            """

        html_body = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 650px; margin: auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff;">
            <div style="background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%); padding: 18px 24px; border-radius: 8px; color: white; margin-bottom: 20px;">
                <h2 style="margin: 0; font-size: 20px;">Faculty Advisor Escalation: At-Risk Advisees</h2>
                <p style="margin: 4px 0 0; font-size: 13px; opacity: 0.9;">Weekly Automated Dean's Risk Sync</p>
            </div>
            
            <p>Dear <strong>{advisor_name}</strong>,</p>
            <p>The automated risk monitoring engine detected that <strong>{len(advisee_profiles)} students</strong> under your mentorship have dropped below the 85% attendance or performance threshold.</p>
            
            <table style="width: 100%; border-collapse: collapse; margin: 18px 0; font-size: 13px;">
                <thead>
                    <tr style="background: #f1f5f9; text-align: left; color: #475569;">
                        <th style="padding: 8px 10px;">Student</th>
                        <th style="padding: 8px 10px;">Subject</th>
                        <th style="padding: 8px 10px;">Attd. %</th>
                        <th style="padding: 8px 10px;">Recovery Req.</th>
                        <th style="padding: 8px 10px;">Marks Avg</th>
                        <th style="padding: 8px 10px;">Risk Level</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>

            <p style="font-size: 13.5px; color: #334155;">
                Recommended Action: Please schedule counseling slots via the Faculty Timetable Portal and notify course instructors for remedial support.
            </p>
        </div>
        """

        log = EmailLog(
            id=f"EML-{uuid.uuid4().hex[:8].upper()}",
            recipient_email=advisor_email,
            recipient_name=advisor_name,
            recipient_role="ADVISOR",
            subject=f"URGENT ADVISOR ALERT: {len(advisee_profiles)} Students Below 85% Threshold",
            body_html=html_body,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            status="SIMULATED" if simulated else "SENT",
            simulated=simulated
        )
        self.email_logs.insert(0, log)
        return log

    def send_batch_warnings(self, profiles: List[StudentRiskProfile]) -> Dict[str, Any]:
        """
        Sends individual personalized warnings to all students with risk_level != 'SAFE',
        and groups advisors to send consolidated escalation digests.
        """
        at_risk = [p for p in profiles if p.metrics.risk_level != "SAFE"]
        student_emails_sent = 0
        advisor_emails_sent = 0

        # 1. Send warning to each at-risk student
        for p in at_risk:
            self.send_student_warning_email(p, simulated=True)
            student_emails_sent += 1

        # 2. Group by advisor and send advisor digests
        advisor_groups: Dict[str, List[StudentRiskProfile]] = {}
        advisor_email_map: Dict[str, str] = {}
        for p in at_risk:
            adv_name = p.student.advisor_name
            advisor_groups.setdefault(adv_name, []).append(p)
            advisor_email_map[adv_name] = p.student.advisor_email

        for adv_name, adv_profiles in advisor_groups.items():
            adv_email = advisor_email_map.get(adv_name, "advisor@apex.edu")
            self.send_faculty_advisor_alert(adv_name, adv_email, adv_profiles, simulated=True)
            advisor_emails_sent += 1

        return {
            "total_sent": student_emails_sent + advisor_emails_sent,
            "student_warnings": student_emails_sent,
            "advisor_alerts": advisor_emails_sent,
            "students_contacted": [p.student.name for p in at_risk]
        }

notification_store = NotificationStore()
