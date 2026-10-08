"""
Notification Engine: Generates personalized warning emails to at-risk students
and escalation alerts to faculty advisors and subject teachers.
Supports real SMTP dispatch when configured and in-memory log store.
"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid
from app.models import StudentRiskProfile, EmailLog

def dispatch_email_transport(
    recipient_email: str,
    recipient_name: str,
    recipient_role: str,
    subject: str,
    html_body: str
) -> EmailLog:
    """
    Attempts real SMTP delivery if SMTP credentials are set in environment,
    otherwise marks as DISPATCHED / SIMULATED and records to persistent log.
    """
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM", smtp_user or "advisory-alerts@apex.edu")

    status = "SIMULATED"
    simulated = True

    if smtp_host and smtp_user and smtp_pass:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"Apex RiskEngine <{smtp_from}>"
            msg["To"] = recipient_email
            part = MIMEText(html_body, "html")
            msg.attach(part)

            server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_from, [recipient_email], msg.as_string())
            server.quit()
            status = "DELIVERED (REAL SMTP)"
            simulated = False
        except Exception as e:
            status = f"SIMULATED (SMTP error: {str(e)[:30]})"
            simulated = True
    else:
        status = "SENT (SIMULATED)"
        simulated = True

    return EmailLog(
        id=f"EML-{uuid.uuid4().hex[:8].upper()}",
        recipient_email=recipient_email,
        recipient_name=recipient_name,
        recipient_role=recipient_role,
        subject=subject,
        body_html=html_body,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        status=status,
        simulated=simulated
    )

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

        log = dispatch_email_transport(
            recipient_email=s.email,
            recipient_name=s.name,
            recipient_role="STUDENT",
            subject=f"URGENT: Academic Risk & Attendance Recovery Warning ({s.subject})",
            html_body=html_body
        )
        self.email_logs.insert(0, log)
        return log

    def send_faculty_advisor_alert(
        self,
        advisor_name: str,
        advisor_email: str,
        advisee_profiles: List[StudentRiskProfile],
        custom_subject: Optional[str] = None
    ) -> EmailLog:
        rows_html = ""
        for p in advisee_profiles:
            rows_html += f"""
            <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 8px 10px; font-weight: 600;">{p.student.name} ({p.student.roll_number})</td>
                <td style="padding: 8px 10px;">{p.student.subject}</td>
                <td style="padding: 8px 10px; font-weight: 700; color: #dc2626;">{p.metrics.attendance_pct}%</td>
                <td style="padding: 8px 10px; font-weight: 700; color: #b91c1c;">{p.metrics.consecutive_classes_needed} classes</td>
                <td style="padding: 8px 10px;">{p.metrics.test_avg_pct}% ({p.metrics.marks_trend})</td>
                <td style="padding: 8px 10px;"><span style="padding: 2px 8px; border-radius: 9999px; background: #fee2e2; color: #991b1b; font-size: 11px; font-weight: 700;">{p.metrics.risk_level}</span></td>
            </tr>
            """

        subject_line = custom_subject or f"FACULTY ADVISOR ALERT: {len(advisee_profiles)} Students Below 85% Threshold"

        html_body = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 650px; margin: auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff;">
            <div style="background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%); padding: 18px 24px; border-radius: 8px; color: white; margin-bottom: 20px;">
                <h2 style="margin: 0; font-size: 20px;">Faculty Advisor Escalation: At-Risk Advisees</h2>
                <p style="margin: 4px 0 0; font-size: 13px; opacity: 0.9;">Apex RiskEngine Automated Council Sync</p>
            </div>
            
            <p>Dear Professor <strong>{advisor_name}</strong>,</p>
            <p>This automated escalation report notifies you that <strong>{len(advisee_profiles)} student(s)</strong> under your advisory supervision have fallen at or below the mandatory <strong>85% attendance and performance threshold</strong>.</p>
            
            <table style="width: 100%; border-collapse: collapse; margin: 18px 0; font-size: 13px;">
                <thead>
                    <tr style="background: #f1f5f9; text-align: left; color: #475569;">
                        <th style="padding: 8px 10px;">Student</th>
                        <th style="padding: 8px 10px;">Subject</th>
                        <th style="padding: 8px 10px;">Attd. %</th>
                        <th style="padding: 8px 10px;">Recovery Streak</th>
                        <th style="padding: 8px 10px;">Marks Avg</th>
                        <th style="padding: 8px 10px;">Risk Level</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>

            <div style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 12px 16px; margin: 18px 0; border-radius: 4px;">
                <strong style="color: #1e40af;">Faculty Action Directives:</strong>
                <ul style="margin: 6px 0 0 16px; padding: 0; color: #1e3a8a; font-size: 13px;">
                    <li>Review available office hour counseling slots in your Faculty Portal.</li>
                    <li>Conduct 1-on-1 recovery review with critical students before the midterm cutoff.</li>
                    <li>Verify attendance catchup feasibility using the recovery streak metrics above.</li>
                </ul>
            </div>

            <p style="font-size: 12px; color: #64748b; margin-top: 24px; border-top: 1px solid #e2e8f0; padding-top: 12px;">
                Delivered to: <code>{advisor_email}</code> via Apex Automated Early Warning System.
            </p>
        </div>
        """

        log = dispatch_email_transport(
            recipient_email=advisor_email,
            recipient_name=advisor_name,
            recipient_role="ADVISOR",
            subject=subject_line,
            html_body=html_body
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
            self.send_student_warning_email(p)
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
            self.send_faculty_advisor_alert(adv_name, adv_email, adv_profiles)
            advisor_emails_sent += 1

        return {
            "total_sent": student_emails_sent + advisor_emails_sent,
            "student_warnings": student_emails_sent,
            "advisor_alerts": advisor_emails_sent,
            "students_contacted": [p.student.name for p in at_risk]
        }

notification_store = NotificationStore()
