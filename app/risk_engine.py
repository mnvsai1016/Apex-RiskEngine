"""
Risk Engine: Calculates student risk levels, consecutive recovery classes,
performance trends, and composite severity indices.
"""
import math
from typing import List, Dict, Any, Tuple
from app.models import StudentRecord, RiskMetrics, StudentRiskProfile

ATTENDANCE_THRESHOLD = 85.0
PERFORMANCE_THRESHOLD = 85.0

def calculate_consecutive_classes_needed(classes_attended: int, total_classes: int, target_pct: float = ATTENDANCE_THRESHOLD) -> int:
    """
    Calculates consecutive classes a student must attend without missing any
    to recover to target_pct (85%).
    
    Formula derivation:
    (classes_attended + x) / (total_classes + x) >= target_pct / 100
    classes_attended + x >= (target_pct / 100) * (total_classes + x)
    x * (1 - target_pct / 100) >= (target_pct / 100) * total_classes - classes_attended
    x = ceil(((target_pct / 100) * total_classes - classes_attended) / (1 - target_pct / 100))
    """
    if total_classes <= 0:
        return 0
    
    target_ratio = target_pct / 100.0
    current_ratio = classes_attended / total_classes
    
    if current_ratio >= target_ratio:
        return 0
    
    numerator = (target_ratio * total_classes) - classes_attended
    denominator = 1.0 - target_ratio  # 0.15 for 85%
    
    classes_needed = math.ceil(numerator / denominator)
    return max(0, classes_needed)

def analyze_student_risk(student: StudentRecord) -> RiskMetrics:
    """
    Evaluates individual student's attendance, marks trajectory,
    recovery requirements, and assigns an overall risk score and tier.
    """
    # 1. Attendance percentage
    if student.total_classes > 0:
        attendance_pct = round((student.classes_attended / student.total_classes) * 100.0, 2)
    else:
        attendance_pct = 100.0
        
    consecutive_needed = calculate_consecutive_classes_needed(
        student.classes_attended, student.total_classes, ATTENDANCE_THRESHOLD
    )
    is_attendance_at_risk = attendance_pct <= ATTENDANCE_THRESHOLD

    # 2. Performance & Trend calculation
    test_avg = round((student.test1_marks + student.test2_marks + student.assignment_marks) / 3.0, 2)
    marks_change = round(student.test2_marks - student.test1_marks, 2)
    
    if marks_change < -2.0:
        marks_trend = "DECLINING"
    elif marks_change > 2.0:
        marks_trend = "IMPROVING"
    else:
        marks_trend = "STABLE"

    is_performance_at_risk = (test_avg <= PERFORMANCE_THRESHOLD) or (marks_trend == "DECLINING") or (student.test2_marks < 50.0)

    # 3. Compile specific reason diagnostics
    reasons = []
    if is_attendance_at_risk:
        reasons.append(f"Attendance is {attendance_pct}% (At/below {ATTENDANCE_THRESHOLD}% threshold)")
        if consecutive_needed > 0:
            reasons.append(f"Requires attending next {consecutive_needed} consecutive classes to recover to 85%")
    else:
        reasons.append(f"Attendance is healthy at {attendance_pct}%")

    if marks_trend == "DECLINING":
        reasons.append(f"Declining test performance: Test 1 ({student.test1_marks}) → Test 2 ({student.test2_marks}) [Δ: {marks_change}%]")
    
    if test_avg < 50.0:
        reasons.append(f"Critical academic failure risk: Average score {test_avg}% (< 50%)")
    elif test_avg <= PERFORMANCE_THRESHOLD:
        reasons.append(f"Performance score {test_avg}% is below benchmark ({PERFORMANCE_THRESHOLD}%)")

    # 4. Composite Risk Score (0 = Safe, 100 = Maximum Danger)
    # Weight: 60% Attendance Deficit, 30% Mark Deficit, 10% Trend Deficit
    attendance_deficit = max(0.0, ATTENDANCE_THRESHOLD - attendance_pct)
    attendance_component = min(60.0, (attendance_deficit / ATTENDANCE_THRESHOLD) * 120.0)
    
    performance_deficit = max(0.0, PERFORMANCE_THRESHOLD - test_avg)
    performance_component = min(30.0, (performance_deficit / PERFORMANCE_THRESHOLD) * 45.0)
    
    trend_component = 10.0 if marks_trend == "DECLINING" else (0.0 if marks_trend == "STABLE" else -5.0)
    
    risk_score = round(max(0.0, min(100.0, attendance_component + performance_component + trend_component)), 1)

    # 5. Severity Categorization
    if attendance_pct < 75.0 or (attendance_pct <= 85.0 and test_avg < 50.0) or risk_score >= 70.0:
        risk_level = "CRITICAL"
        intervention_required = True
    elif attendance_pct <= 80.0 or test_avg < 60.0 or risk_score >= 45.0:
        risk_level = "HIGH"
        intervention_required = True
    elif is_attendance_at_risk or is_performance_at_risk:
        risk_level = "MODERATE"
        intervention_required = True
    else:
        risk_level = "SAFE"
        intervention_required = False

    return RiskMetrics(
        attendance_pct=attendance_pct,
        test_avg_pct=test_avg,
        marks_trend=marks_trend,
        marks_change=marks_change,
        is_attendance_at_risk=is_attendance_at_risk,
        is_performance_at_risk=is_performance_at_risk,
        consecutive_classes_needed=consecutive_needed,
        risk_level=risk_level,
        risk_score=risk_score,
        intervention_required=intervention_required,
        reasons=reasons
    )

def build_student_risk_profiles(students: List[StudentRecord]) -> List[StudentRiskProfile]:
    """
    Transforms a list of student records into analyzed risk profiles,
    sorted by risk severity in descending order (highest risk first).
    """
    profiles = []
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MODERATE": 2, "SAFE": 3}
    
    for s in students:
        metrics = analyze_student_risk(s)
        profiles.append(StudentRiskProfile(student=s, metrics=metrics))
        
    profiles.sort(key=lambda p: (severity_order.get(p.metrics.risk_level, 4), -p.metrics.risk_score))
    return profiles
