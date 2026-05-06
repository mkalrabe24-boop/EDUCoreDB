import sqlite3
import os

db_path = "sms.sqlite3"
if not os.path.exists(db_path):
    print("Database not found!")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Rename tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'student_management_app_%';")
tables = cursor.fetchall()
for table in tables:
    old_name = table[0]
    new_name = old_name.replace("student_management_app_", "educoredb_app_")
    print(f"Renaming {old_name} to {new_name}")
    try:
        cursor.execute(f"ALTER TABLE {old_name} RENAME TO {new_name};")
    except Exception as e:
        print(f"Error renaming {old_name}: {e}")

# 2. Update django_content_type
print("Updating django_content_type")
cursor.execute("UPDATE django_content_type SET app_label = 'educoredb_app' WHERE app_label = 'student_management_app';")

# 3. Update django_migrations
print("Updating django_migrations")
cursor.execute("UPDATE django_migrations SET app = 'educoredb_app' WHERE app = 'student_management_app';")

conn.commit()
conn.close()
print("Database update complete.")
