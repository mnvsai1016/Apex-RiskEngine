# 🧑‍⚖️ Hackathon Judge Evaluation & Testing Guide

Welcome, Judges! This guide allows you to test and verify every core feature in **under 2 minutes**.

---

## ⚡ 60-Second Quick Test Checklist

| Step | Feature Under Test | Where to Test | Expected Outcome |
|---|---|---|---|
| 1️⃣ | **Run or Open Application** | Browser at `http://localhost:8000` | Full glassmorphism dashboard renders with loaded metrics. |
| 2️⃣ | **Upload Ingestion** | Click *"Upload Attendance & Marks"* tab | Download sample CSV, re-upload it, and watch the roster update. |
| 3️⃣ | **Verify 85% & Recovery Formula** | Check *"Risk Dashboard"* for Aarav Sharma (66.7%) | Shows exactly `44 Consecutive Classes Needed` ($\lceil (0.85 \times 36 - 24)/0.15 \rceil = 44$). |
| 4️⃣ | **Declining Marks Flag** | Check students with test score drops | Flags "Declining (Test 1 $\to$ Test 2)" with badge. |
| 5️⃣ | **Automated Voice Call** | Click **Phone icon** on any student or *"Auto-Call (<85%)"* | Virtual phone rings, animated waveform activates, and browser speaks voice warning aloud! |
| 6️⃣ | **Personalized Email Warning** | Click **Paper Plane icon** on student or *"Warn All At-Risk"* | Dispatched email preview shows custom attendance %, recovery classes, and advisor details. |
| 7️⃣ | **Teacher Timetable Booking** | Click *"Teacher Timetable & Booking"* tab | Click *"Book Session"* on a free green slot; slot locks with confirmation ID. |
| 8️⃣ | **Weekly Dean's Summary** | Click *"Weekly Dean's Report"* tab | Executive report view with department breakdowns & *"Print / PDF View"*. |

---

## 🔬 Mathematical Verification of the Recovery Formula

The problem statement asks: *Calculate how many consecutive classes each at-risk student must attend to recover.*

* Target attendance percentage: $P = 85.0\% = 0.85$
* Current classes attended: $A$
* Current total classes held: $T$
* Target condition: $\frac{A + x}{T + x} \ge 0.85$
* Solving for $x$:
  $$A + x \ge 0.85T + 0.85x$$
  $$(1 - 0.85)x \ge 0.85T - A$$
  $$0.15x \ge 0.85T - A$$
  $$x = \left\lceil \frac{0.85T - A}{0.15} \right\rceil$$

### Test Example (Aarav Sharma):
* $A = 24$, $T = 36$
* Current attendance: $24 / 36 = 66.67\%$
* Recovery requirement:
  $$x = \left\lceil \frac{0.85 \times 36 - 24}{0.15} \right\rceil = \left\lceil \frac{30.6 - 24}{0.15} \right\rceil = \left\lceil \frac{6.6}{0.15} \right\rceil = \lceil 44.0 \rceil = 44$$
* **Verification Check:**
  $$\frac{24 + 44}{36 + 44} = \frac{68}{80} = 85.00\% \quad \text{(Exact Match!)}$$
