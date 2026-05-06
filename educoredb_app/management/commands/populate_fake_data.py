import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction

from educoredb_app.models import (
    AdminHOD,
    Attendance,
    AttendanceReport,
    Courses,
    CustomUser,
    FeedBackStaffs,
    FeedBackStudent,
    LeaveReportStaff,
    LeaveReportStudent,
    NotificationStaffs,
    NotificationStudent,
    OnlineClassRoom,
    SessionYearModel,
    Staffs,
    Students,
    Subjects,
    StudentResult,
)


def create_or_get_session():
    session, created = SessionYearModel.objects.get_or_create(
        session_start_year=date(2023, 9, 1),
        session_end_year=date(2024, 5, 31),
    )
    return session


def create_courses():
    course_names = ["Computer Science", "Mathematics", "Physics"]
    courses = []
    for name in course_names:
        course, _ = Courses.objects.get_or_create(course_name=name)
        courses.append(course)
    return courses


def create_user(username, email, password, first_name, last_name, user_type):
    user, created = CustomUser.objects.get_or_create(
        username=username,
        defaults={
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "user_type": str(user_type),
            "is_active": True,
        },
    )
    if created:
        user.set_password(password)
        user.save()
    return user


def create_staff_users():
    staff_data = [
        ("alice", "alice@educore.com", "staff123", "Alice", "Roy"),
        ("bob", "bob@educore.com", "staff123", "Bob", "Khan"),
    ]
    staff_users = []
    for username, email, password, first_name, last_name in staff_data:
        user = create_user(username, email, password, first_name, last_name, 2)
        Staffs.objects.get_or_create(admin=user, defaults={"address": ""})
        staff_users.append(user)
    return staff_users


def create_students(courses, session_year):
    student_data = [
        ("sophie", "sophie@student.com", "student123", "Sophie", "Sharma", courses[0]),
        ("ravi", "ravi@student.com", "student123", "Ravi", "Patel", courses[0]),
        ("neha", "neha@student.com", "student123", "Neha", "Singh", courses[1]),
        ("arjun", "arjun@student.com", "student123", "Arjun", "Malhotra", courses[1]),
        ("tanya", "tanya@student.com", "student123", "Tanya", "Mehta", courses[2]),
        ("kiran", "kiran@student.com", "student123", "Kiran", "Verma", courses[2]),
    ]
    students = []
    for username, email, password, first_name, last_name, course in student_data:
        user = create_user(username, email, password, first_name, last_name, 3)
        student, _ = Students.objects.get_or_create(
            admin=user,
            defaults={
                "course_id": course,
                "session_year_id": session_year,
                "gender": random.choice(["Male", "Female"]),
                "address": f"{random.choice(['Delhi', 'Mumbai', 'Kolkata', 'Chennai'])}, India",
                "profile_pic": "",
            },
        )
        if not _:
            student.course_id = course
            student.session_year_id = session_year
            student.gender = random.choice(["Male", "Female"])
            student.address = f"{random.choice(['Delhi', 'Mumbai', 'Kolkata', 'Chennai'])}, India"
            student.profile_pic = ""
            student.save()
        students.append(student)
    return students


def create_hod_user():
    user = create_user("admin", "admin@educore.com", "admin123", "Admin", "User", 1)
    AdminHOD.objects.get_or_create(admin=user)
    return user


def create_subjects(courses, staff_users):
    subject_map = [
        ("Programming Fundamentals", courses[0], staff_users[0]),
        ("Data Structures", courses[0], staff_users[0]),
        ("Calculus", courses[1], staff_users[1]),
        ("Linear Algebra", courses[1], staff_users[1]),
        ("Mechanics", courses[2], staff_users[1]),
    ]
    subjects = []
    for name, course, staff in subject_map:
        subject, _ = Subjects.objects.get_or_create(
            subject_name=name,
            course_id=course,
            staff_id=staff,
        )
        subjects.append(subject)
    return subjects


def create_attendance_and_reports(subjects, students, session_year):
    today = date.today()
    for subject in subjects:
        course_students = [s for s in students if s.course_id.id == subject.course_id.id]
        for offset in range(5):
            attendance_date = today - timedelta(days=offset * 2)
            attendance, _ = Attendance.objects.get_or_create(
                subject_id=subject,
                attendance_date=attendance_date,
                session_year_id=session_year,
            )
            for student in course_students:
                status = random.choice([True, True, False])
                AttendanceReport.objects.get_or_create(
                    student_id=student,
                    attendance_id=attendance,
                    defaults={"status": status},
                )


def create_student_results(subjects, students):
    for student in students:
        for subject in subjects:
            if subject.course_id == student.course_id:
                StudentResult.objects.get_or_create(
                    student_id=student,
                    subject_id=subject,
                    defaults={
                        "subject_exam_marks": random.uniform(50, 95),
                        "subject_assignment_marks": random.uniform(35, 50),
                    },
                )


def create_classrooms(subjects, session_year):
    for subject in subjects:
        OnlineClassRoom.objects.get_or_create(
            room_name=f"{subject.subject_name[:4].upper()}-{session_year.id}",
            room_pwd="class123",
            subject=subject,
            session_years=session_year,
            started_by=subject.staff_id.staffs,
            is_active=True,
        )


def create_feedback_and_notifications(students, staff_users):
    for student in students[:3]:
        FeedBackStudent.objects.get_or_create(
            student_id=student,
            defaults={"feedback": "The classes are helpful.", "feedback_reply": "Thank you for the review."},
        )
        LeaveReportStudent.objects.get_or_create(
            student_id=student,
            defaults={"leave_date": "2024-04-20", "leave_message": "Family work", "leave_status": 1},
        )
        NotificationStudent.objects.get_or_create(
            student_id=student,
            defaults={"message": "New assignment uploaded."},
        )

    for staff_user in staff_users:
        staff = Staffs.objects.get(admin=staff_user)
        FeedBackStaffs.objects.get_or_create(
            staff_id=staff,
            defaults={"feedback": "Please check the attendance portal.", "feedback_reply": "Will do, thanks."},
        )
        LeaveReportStaff.objects.get_or_create(
            staff_id=staff,
            defaults={"leave_date": "2024-03-15", "leave_message": "Medical leave", "leave_status": 1},
        )
        NotificationStaffs.objects.get_or_create(
            staff_id=staff,
            defaults={"message": "Staff meeting scheduled for Friday."},
        )


class Command(BaseCommand):
    help = "Populate demo data into the EDUCoreDB database."

    def handle(self, *args, **options):
        with transaction.atomic():
            if CustomUser.objects.filter(username="admin").exists():
                self.stdout.write(self.style.WARNING("Demo data already exists. No changes made."))
                return

            self.stdout.write("Creating demo data...")
            session_year = create_or_get_session()
            courses = create_courses()
            create_hod_user()
            staff_users = create_staff_users()
            students = create_students(courses, session_year)
            subjects = create_subjects(courses, staff_users)
            create_attendance_and_reports(subjects, students, session_year)
            create_student_results(subjects, students)
            create_classrooms(subjects, session_year)
            create_feedback_and_notifications(students, staff_users)

            self.stdout.write(self.style.SUCCESS("Demo data has been added successfully."))
