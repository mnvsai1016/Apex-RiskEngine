"""
Sample Dataset and Exporter for Hackathon Judges.
Pre-populates realistic student records across attendance & test marks,
and generates downloadable CSV files for instant validation.
"""
import os
import pandas as pd
from typing import List
from app.models import StudentRecord

DEFAULT_STUDENTS: List[StudentRecord] = [
    StudentRecord(
        id="STU-001",
        name="Aarav Sharma",
        roll_number="2024-CS-014",
        email="aarav.sharma@student.apex.edu",
        phone="+1 (555) 234-5678",
        department="Computer Science",
        semester=4,
        advisor_name="Dr. Aris Thorne",
        advisor_email="aris.thorne@apex.edu",
        subject="Data Structures & Algorithms",
        classes_attended=24,
        total_classes=36,  # 66.67% -> Critical! Recovery: ceil((0.85*36 - 24)/0.15) = ceil(6.6/0.15) = 44 consecutive classes
        test1_marks=74.0,
        test2_marks=52.0,  # Declining by -22%
        assignment_marks=60.0
    ),
    StudentRecord(
        id="STU-002",
        name="Rohan Verma",
        roll_number="2024-CS-029",
        email="rohan.verma@student.apex.edu",
        phone="+1 (555) 345-6789",
        department="Computer Science",
        semester=4,
        advisor_name="Prof. Sarah Jenkins",
        advisor_email="sarah.jenkins@apex.edu",
        subject="Operating Systems",
        classes_attended=28,
        total_classes=35,  # 80.00% -> Moderate! Recovery: ceil((0.85*35 - 28)/0.15) = ceil(1.75/0.15) = 12 consecutive classes
        test1_marks=82.0,
        test2_marks=78.0,
        assignment_marks=80.0
    ),
    StudentRecord(
        id="STU-003",
        name="Ananya Iyer",
        roll_number="2024-EC-008",
        email="ananya.iyer@student.apex.edu",
        phone="+1 (555) 456-7890",
        department="Electronics & Communication",
        semester=4,
        advisor_name="Dr. Vikram Patel",
        advisor_email="vikram.patel@apex.edu",
        subject="Digital Signal Processing",
        classes_attended=34,
        total_classes=40,  # 85.00% -> Borderline on the 85% threshold! Recovery: 0
        test1_marks=91.0,
        test2_marks=89.0,
        assignment_marks=92.0
    ),
    StudentRecord(
        id="STU-004",
        name="Vikramaditya Rao",
        roll_number="2024-IT-019",
        email="vikram.rao@student.apex.edu",
        phone="+1 (555) 567-8901",
        department="Information Technology",
        semester=4,
        advisor_name="Prof. Meera Nair",
        advisor_email="meera.nair@apex.edu",
        subject="Database Management Systems",
        classes_attended=22,
        total_classes=32,  # 68.75% -> Critical! Recovery: ceil((0.85*32 - 22)/0.15) = ceil(5.2/0.15) = 35 consecutive classes
        test1_marks=65.0,
        test2_marks=44.0,  # Declining by -21% & under 50%
        assignment_marks=50.0
    ),
    StudentRecord(
        id="STU-005",
        name="Priya Sengupta",
        roll_number="2024-CS-041",
        email="priya.sengupta@student.apex.edu",
        phone="+1 (555) 678-9012",
        department="Computer Science",
        semester=4,
        advisor_name="Dr. Aris Thorne",
        advisor_email="aris.thorne@apex.edu",
        subject="Data Structures & Algorithms",
        classes_attended=38,
        total_classes=40,  # 95.00% -> Safe!
        test1_marks=94.0,
        test2_marks=96.0,
        assignment_marks=98.0
    ),
    StudentRecord(
        id="STU-006",
        name="Karan Malhotra",
        roll_number="2024-EC-022",
        email="karan.malhotra@student.apex.edu",
        phone="+1 (555) 789-0123",
        department="Electronics & Communication",
        semester=4,
        advisor_name="Dr. Vikram Patel",
        advisor_email="vikram.patel@apex.edu",
        subject="Digital Signal Processing",
        classes_attended=25,
        total_classes=34,  # 73.53% -> Critical! Recovery: ceil((0.85*34 - 25)/0.15) = ceil(3.9/0.15) = 26 consecutive classes
        test1_marks=55.0,
        test2_marks=42.0,  # Declining marks (<50%)
        assignment_marks=58.0
    ),
    StudentRecord(
        id="STU-007",
        name="Sneha Kulkarni",
        roll_number="2024-AI-005",
        email="sneha.kulkarni@student.apex.edu",
        phone="+1 (555) 890-1234",
        department="Artificial Intelligence & ML",
        semester=4,
        advisor_name="Dr. Rajesh Kumar",
        advisor_email="rajesh.kumar@apex.edu",
        subject="Engineering Mathematics III",
        classes_attended=29,
        total_classes=35,  # 82.86% -> Below 85%! Recovery: ceil((0.85*35 - 29)/0.15) = ceil(0.75/0.15) = 5 consecutive classes
        test1_marks=70.0,
        test2_marks=68.0,
        assignment_marks=75.0
    ),
    StudentRecord(
        id="STU-008",
        name="Devansh Chawla",
        roll_number="2024-AI-018",
        email="devansh.chawla@student.apex.edu",
        phone="+1 (555) 901-2345",
        department="Artificial Intelligence & ML",
        semester=4,
        advisor_name="Dr. Rajesh Kumar",
        advisor_email="rajesh.kumar@apex.edu",
        subject="Engineering Mathematics III",
        classes_attended=19,
        total_classes=30,  # 63.33% -> Critical! Recovery: ceil((0.85*30 - 19)/0.15) = ceil(6.5/0.15) = 44 consecutive classes
        test1_marks=48.0,
        test2_marks=35.0,  # Severe decline & fail
        assignment_marks=40.0
    ),
    StudentRecord(
        id="STU-009",
        name="Divya Reddy",
        roll_number="2024-IT-031",
        email="divya.reddy@student.apex.edu",
        phone="+1 (555) 012-3456",
        department="Information Technology",
        semester=4,
        advisor_name="Prof. Meera Nair",
        advisor_email="meera.nair@apex.edu",
        subject="Database Management Systems",
        classes_attended=30,
        total_classes=36,  # 83.33% -> Moderate below 85%! Recovery: ceil((0.85*36 - 30)/0.15) = ceil(0.6/0.15) = 4 consecutive classes
        test1_marks=88.0,
        test2_marks=86.0,
        assignment_marks=90.0
    ),
    StudentRecord(
        id="STU-010",
        name="Manish Gupta",
        roll_number="2024-CS-055",
        email="manish.gupta@student.apex.edu",
        phone="+1 (555) 123-9876",
        department="Computer Science",
        semester=4,
        advisor_name="Prof. Sarah Jenkins",
        advisor_email="sarah.jenkins@apex.edu",
        subject="Operating Systems",
        classes_attended=36,
        total_classes=38,  # 94.74% -> Safe!
        test1_marks=89.0,
        test2_marks=91.0,
        assignment_marks=92.0
    )
]

def export_sample_files(target_dir: str):
    """
    Exports clean sample CSV files so hackathon judges can download and inspect them,
    or re-upload them to test the ingestion pipeline.
    """
    os.makedirs(target_dir, exist_ok=True)
    
    # 1. Combined Master File
    df_combined = pd.DataFrame([s.model_dump() for s in DEFAULT_STUDENTS])
    combined_path = os.path.join(target_dir, "combined_student_data.csv")
    df_combined.to_csv(combined_path, index=False)

    # 2. Pure Attendance Sheet
    attendance_cols = ["roll_number", "name", "department", "subject", "classes_attended", "total_classes", "advisor_name", "advisor_email", "phone", "email"]
    df_attendance = df_combined[attendance_cols]
    attendance_path = os.path.join(target_dir, "attendance_sample.csv")
    df_attendance.to_csv(attendance_path, index=False)

    # 3. Pure Test Results Sheet
    test_cols = ["roll_number", "name", "subject", "test1_marks", "test2_marks", "assignment_marks"]
    df_tests = df_combined[test_cols]
    tests_path = os.path.join(target_dir, "test_results_sample.csv")
    df_tests.to_csv(tests_path, index=False)

    return {
        "combined": combined_path,
        "attendance": attendance_path,
        "test_results": tests_path
    }
