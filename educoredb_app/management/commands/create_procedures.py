"""
Django management command to create MySQL stored procedures, functions, and triggers
for the EDUCoreDB project. This satisfies the requirement for PL/SQL procedures/functions,
cursors, and triggers in the student project.
"""

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Create MySQL stored procedures, functions, and triggers for EDUCoreDB"

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            self.stdout.write("Creating MySQL stored procedures, functions, and triggers...")
            
            # 1. Stored Procedure: Get Student Attendance Report
            cursor.execute("""
                CREATE PROCEDURE IF NOT EXISTS GetStudentAttendanceReport(
                    IN p_student_id INT,
                    IN p_session_id INT
                )
                BEGIN
                    DECLARE v_total_classes INT DEFAULT 0;
                    DECLARE v_classes_attended INT DEFAULT 0;
                    DECLARE v_attendance_percentage DECIMAL(5, 2);
                    
                    SELECT COUNT(*) INTO v_total_classes
                    FROM educoredb_app_attendance
                    WHERE session_year_id = p_session_id;
                    
                    SELECT COUNT(*) INTO v_classes_attended
                    FROM educoredb_app_attendancereport ar
                    INNER JOIN educoredb_app_attendance a ON ar.attendance_id = a.id
                    WHERE ar.student_id = p_student_id
                    AND a.session_year_id = p_session_id
                    AND ar.status = 1;
                    
                    IF v_total_classes > 0 THEN
                        SET v_attendance_percentage = (v_classes_attended / v_total_classes) * 100;
                    ELSE
                        SET v_attendance_percentage = 0;
                    END IF;
                    
                    SELECT 
                        p_student_id AS student_id,
                        v_total_classes AS total_classes,
                        v_classes_attended AS classes_attended,
                        v_attendance_percentage AS attendance_percentage;
                END
            """)
            self.stdout.write(self.style.SUCCESS("✓ Procedure: GetStudentAttendanceReport"))
            
            # 2. Stored Procedure: Calculate Student GPA
            cursor.execute("""
                CREATE PROCEDURE IF NOT EXISTS CalculateStudentGPA(
                    IN p_student_id INT
                )
                BEGIN
                    DECLARE v_total_marks DECIMAL(10, 2) DEFAULT 0;
                    DECLARE v_subject_count INT DEFAULT 0;
                    DECLARE v_gpa DECIMAL(5, 2);
                    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET v_gpa = 0;
                    
                    SELECT 
                        COALESCE(SUM(subject_exam_marks + subject_assignment_marks), 0),
                        COUNT(DISTINCT subject_id)
                    INTO v_total_marks, v_subject_count
                    FROM educoredb_app_studentresult
                    WHERE student_id = p_student_id;
                    
                    IF v_subject_count > 0 THEN
                        SET v_gpa = v_total_marks / v_subject_count;
                    ELSE
                        SET v_gpa = 0;
                    END IF;
                    
                    SELECT 
                        p_student_id AS student_id,
                        v_total_marks AS total_marks,
                        v_subject_count AS subject_count,
                        v_gpa AS gpa;
                END
            """)
            self.stdout.write(self.style.SUCCESS("✓ Procedure: CalculateStudentGPA"))
            
            # 3. Stored Function: Get Leave Status Description
            cursor.execute("""
                CREATE FUNCTION IF NOT EXISTS GetLeaveStatus(p_status INT)
                RETURNS VARCHAR(20)
                DETERMINISTIC
                READS SQL DATA
                BEGIN
                    DECLARE v_status_text VARCHAR(20);
                    
                    CASE p_status
                        WHEN 0 THEN SET v_status_text = 'Pending';
                        WHEN 1 THEN SET v_status_text = 'Approved';
                        WHEN 2 THEN SET v_status_text = 'Rejected';
                        ELSE SET v_status_text = 'Unknown';
                    END CASE;
                    
                    RETURN v_status_text;
                END
            """)
            self.stdout.write(self.style.SUCCESS("✓ Function: GetLeaveStatus"))
            
            # 4. Stored Function: Count Active Students in Course
            cursor.execute("""
                CREATE FUNCTION IF NOT EXISTS CountStudentsInCourse(p_course_id INT)
                RETURNS INT
                READS SQL DATA
                BEGIN
                    DECLARE v_count INT;
                    
                    SELECT COUNT(*) INTO v_count
                    FROM educoredb_app_students
                    WHERE course_id = p_course_id;
                    
                    RETURN COALESCE(v_count, 0);
                END
            """)
            self.stdout.write(self.style.SUCCESS("✓ Function: CountStudentsInCourse"))
            
            # 5. Trigger: Update Student Last Modified on Result Change
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS tr_studentresult_update
                AFTER INSERT ON educoredb_app_studentresult
                FOR EACH ROW
                BEGIN
                    UPDATE educoredb_app_students
                    SET updated_at = NOW()
                    WHERE id = NEW.student_id_id;
                END
            """)
            self.stdout.write(self.style.SUCCESS("✓ Trigger: tr_studentresult_update"))
            
            # 6. Trigger: Log Attendance Changes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS educoredb_app_attendance_audit (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    attendance_id INT NOT NULL,
                    student_id INT NOT NULL,
                    old_status BOOLEAN,
                    new_status BOOLEAN,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (attendance_id) REFERENCES educoredb_app_attendance(id),
                    FOREIGN KEY (student_id) REFERENCES educoredb_app_students(id)
                )
            """)
            
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS tr_attendancereport_audit
                AFTER UPDATE ON educoredb_app_attendancereport
                FOR EACH ROW
                BEGIN
                    IF OLD.status <> NEW.status THEN
                        INSERT INTO educoredb_app_attendance_audit 
                        (attendance_id, student_id, old_status, new_status)
                        VALUES (NEW.attendance_id_id, NEW.student_id_id, OLD.status, NEW.status);
                    END IF;
                END
            """)
            self.stdout.write(self.style.SUCCESS("✓ Trigger: tr_attendancereport_audit"))
            
            # 7. Stored Procedure with Cursor: Generate Attendance Report
            cursor.execute("""
                CREATE PROCEDURE IF NOT EXISTS GenerateAttendanceReport()
                BEGIN
                    DECLARE v_student_id INT;
                    DECLARE v_student_name VARCHAR(100);
                    DECLARE v_attendance_pct DECIMAL(5, 2);
                    DECLARE v_done INT DEFAULT FALSE;
                    
                    DECLARE student_cursor CURSOR FOR
                        SELECT s.id, cu.first_name
                        FROM educoredb_app_students s
                        INNER JOIN educoredb_app_customuser cu ON s.admin_id = cu.id
                        LIMIT 10;
                    
                    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = TRUE;
                    
                    CREATE TEMPORARY TABLE IF NOT EXISTS temp_attendance_report (
                        student_id INT,
                        student_name VARCHAR(100),
                        attendance_percentage DECIMAL(5, 2)
                    );
                    
                    OPEN student_cursor;
                    
                    read_loop: LOOP
                        FETCH student_cursor INTO v_student_id, v_student_name;
                        IF v_done THEN
                            LEAVE read_loop;
                        END IF;
                        
                        SELECT 
                            (COUNT(CASE WHEN ar.status = 1 THEN 1 END) / COUNT(*) * 100)
                        INTO v_attendance_pct
                        FROM educoredb_app_attendancereport ar
                        WHERE ar.student_id = v_student_id;
                        
                        INSERT INTO temp_attendance_report VALUES 
                            (v_student_id, v_student_name, COALESCE(v_attendance_pct, 0));
                    END LOOP;
                    
                    CLOSE student_cursor;
                    
                    SELECT * FROM temp_attendance_report;
                    
                    DROP TEMPORARY TABLE temp_attendance_report;
                END
            """)
            self.stdout.write(self.style.SUCCESS("✓ Procedure: GenerateAttendanceReport (with Cursor)"))
            
            # 8. Trigger: Prevent Invalid Leave Dates
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS tr_leavereport_validation
                BEFORE INSERT ON educoredb_app_leavereportstudent
                FOR EACH ROW
                BEGIN
                    IF NEW.leave_date IS NULL OR NEW.leave_message IS NULL THEN
                        SIGNAL SQLSTATE '45000'
                        SET MESSAGE_TEXT = 'Leave date and message cannot be null';
                    END IF;
                END
            """)
            self.stdout.write(self.style.SUCCESS("✓ Trigger: tr_leavereport_validation"))
            
            self.stdout.write(self.style.SUCCESS("\n✅ All stored procedures, functions, and triggers created successfully!"))
            self.stdout.write("""
            
Created Database Objects:
═════════════════════════════════════════════════════════════

STORED PROCEDURES:
  1. GetStudentAttendanceReport(p_student_id, p_session_id)
     - Calculates attendance percentage for a student
  
  2. CalculateStudentGPA(p_student_id)
     - Computes GPA from exam and assignment marks
  
  3. GenerateAttendanceReport()
     - Generates attendance report using cursor loop
     - Demonstrates cursor, loop, and temporary table usage

STORED FUNCTIONS:
  1. GetLeaveStatus(p_status)
     - Returns descriptive status text for leave request
  
  2. CountStudentsInCourse(p_course_id)
     - Returns count of students in a course

TRIGGERS:
  1. tr_studentresult_update
     - Updates student record when grades change
  
  2. tr_attendancereport_audit
     - Audits attendance status changes to audit table
  
  3. tr_leavereport_validation
     - Validates leave request data before insertion

TABLES:
  1. educoredb_app_attendance_audit
     - Audit table for tracking attendance changes

═════════════════════════════════════════════════════════════
            """)
