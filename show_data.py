#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'educoredb.settings')
django.setup()

from educoredb_app.models import CustomUser, Students, Staffs, Courses, Subjects, Attendance, AttendanceReport, StudentResult

print("=" * 70)
print("DATABASE SUMMARY - EDUCoreDB (MySQL/MariaDB)")
print("=" * 70)

print(f"\n📚 COURSES: {Courses.objects.count()}")
for course in Courses.objects.all():
    print(f"   ✓ {course.course_name}")

print(f"\n👨‍💼 STAFF MEMBERS: {Staffs.objects.count()}")
for staff in Staffs.objects.all():
    user = staff.admin
    print(f"   ✓ {user.first_name} {user.last_name} ({user.username})")

print(f"\n👨‍🎓 STUDENTS: {Students.objects.count()}")
for student in Students.objects.all()[:15]:
    user = student.admin
    print(f"   ✓ {user.first_name} {user.last_name} ({user.username}) - {student.course_id.course_name}")

print(f"\n📖 SUBJECTS: {Subjects.objects.count()}")
for subject in Subjects.objects.all():
    print(f"   ✓ {subject.subject_name} (Instructor: {subject.staff_id.first_name})")

print(f"\n📊 ATTENDANCE RECORDS: {Attendance.objects.count()}")
print(f"📋 ATTENDANCE REPORTS: {AttendanceReport.objects.count()}")
print(f"📈 STUDENT RESULTS: {StudentResult.objects.count()}")

print(f"\n👤 TOTAL USERS: {CustomUser.objects.count()}")
print(f"   - HOD (Admin): {CustomUser.objects.filter(user_type=1).count()}")
print(f"   - Staff: {CustomUser.objects.filter(user_type=2).count()}")
print(f"   - Students: {CustomUser.objects.filter(user_type=3).count()}")

print("\n" + "=" * 70)
print("✅ All data is stored in MySQL database 'educoredb'")
print("🔧 Stored Procedures, Functions, and Triggers are available")
print("=" * 70)
