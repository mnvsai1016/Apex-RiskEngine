# 🎥 Hackathon Demo Video Script (2–5 Minutes Walkthrough)

This script provides an exact timestamped recording blueprint for presenting the **Apex RiskEngine** to judges.

---

## ⏱️ Video Breakdown (Target: 3 Minutes 30 Seconds)

### **0:00 - 0:30 | Introduction & Problem Statement**
* **Visual:** Open browser at `http://localhost:8000/` or live deployed URL showing the Apex RiskEngine dashboard.
* **Narration:**
  > *"Hello judges! In higher education, student dropout and course debarment often happen because attendance deficits are caught too late. Today we are presenting **Apex RiskEngine** — an automated, AI-powered student risk management system designed to enforce the mandatory 85% attendance policy, predict failure risk, calculate exact mathematical recovery streaks, and automate multi-channel interventions including personalized warning emails, advisor escalations, teacher timetable sync, and automated voice calls."*

---

### **0:30 - 1:05 | File Upload & Flexible Data Ingestion (Deliverable #1)**
* **Visual:** Navigate to the **"Upload Attendance & Marks"** tab.
* **Actions:**
  1. Highlight the pre-built sample test files (`combined_student_data.csv`, `attendance_sample.csv`, `test_results_sample.csv`).
  2. Click the upload dropzone or select `combined_student_data.csv`.
  3. Click **"Process & Run Risk Engine"**.
* **Narration:**
  > *"Faculty and administrators can ingest real-world CSV or Excel sheets containing attendance and midterm test results. The engine features forgiving column normalization, mapping diverse formats automatically. Within milliseconds, the entire cohort is parsed, calculated, and re-ranked."*

---

### **1:05 - 1:45 | Dashboard, Risk Rankings & The Recovery Formula (Deliverable #2 & #3)**
* **Visual:** Switch to **"Risk Dashboard & Recovery Roster"**.
* **Actions:**
  1. Point out the top stat counters: Total Monitored, Students $\le$ 85%, Declining Marks, and Interventions Active.
  2. Showcase the **Department-wide risk breakdown** and **Subject-wide risk metrics**.
  3. Highlight student **Aarav Sharma** (Attendance: 66.7%).
  4. Explain the **Recovery Formula**:
     $$\text{Consecutive Classes Needed} = \left\lceil \frac{0.85 \times T - A}{0.15} \right\rceil$$
* **Narration:**
  > *"Unlike basic trackers, Apex RiskEngine calculates the non-negotiable upcoming streak of classes a student must attend to cross back over 85%. For example, Aarav Sharma has attended 24 of 36 classes (66.7%). To reach 85%, he must attend exactly 44 consecutive upcoming lectures without missing a single one. Students with declining test scores from Test 1 to Test 2 are also automatically flagged."*

---

### **1:45 - 2:20 | Automated Voice Call Interventions (Deliverable #4 - Key Highlight!)**
* **Visual:** On Aarav Sharma's row, click the **Phone icon ("Simulate Automated Call")**.
* **Actions:**
  1. The **Interactive Virtual IVR Phone Modal** opens.
  2. Point out: Dialing $\to$ Carrier Ringing $\to$ Connected $\to$ Waveform Pulse.
  3. The browser speaks the automated warning message via Web Speech API / audio synthesis!
  4. Show the live transcription box displaying the warning script.
  5. Click **"End Call"** or wait for completion.
  6. Switch to **"Automated Telephony Logs"** tab to show the logged Call SID, transcript, duration, and status.
* **Narration:**
  > *"When students fall below the 85% threshold, waiting for them to check emails is not enough. The system triggers automated outbound phone calls. Watch as the virtual phone dials, connects, and our synthetic voice engine transmits an immediate audio warning directly to the student, logging the complete telephony record and Call SID."*

---

### **2:20 - 2:45 | Personalized Warning Emails & Advisor Escalations (Deliverable #5)**
* **Visual:** Switch to **"Email Warning Dispatch"** tab.
* **Actions:**
  1. Click **"Dispatch Warnings to All At-Risk"**.
  2. Open any email log and click **"Preview Email"**.
  3. Show the personalized email with attendance %, consecutive classes needed, advisor details, and urgent action plan.
* **Narration:**
  > *"With one click, personalized warning emails are dispatched to all at-risk students, while department advisors receive consolidated escalation digests grouping their flagged advisees."*

---

### **2:45 - 3:10 | Teacher Timetable Sync & Student Appointment Booking (Deliverable #6)**
* **Visual:** Switch to **"Teacher Timetable & Booking"** tab.
* **Actions:**
  1. Show teacher office hours (Dr. Aris Thorne, Prof. Sarah Jenkins, etc.) with FREE and BUSY slots.
  2. Click **"Book Session"** on an available green slot.
  3. Enter student name, reason ("Attendance recovery plan review"), and confirm.
  4. The slot immediately locks to 'BOOKED' with an appointment ID and Google Calendar invite link!
* **Narration:**
  > *"At-risk students need immediate remedial help. Apex RiskEngine integrates directly with faculty schedules. Students can discover open office hours and book a 1-on-1 counseling slot instantly, converting risk warnings into active remediation."*

---

### **3:10 - 3:30 | Weekly Dean's Summary Report & Conclusion (Deliverable #7)**
* **Visual:** Switch to **"Weekly Dean's Report"** tab and click **"Open Printable / PDF View"**.
* **Narration:**
  > *"Finally, the system compiles automated weekly executive summaries for Deans and Department Chairs, detailing institutional hotspots, urgent student rosters, and remedial action directives. Apex RiskEngine closes the loop between data ingestion, predictive calculation, multi-channel outreach, and faculty counseling. Thank you!"*
