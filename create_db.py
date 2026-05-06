#!/usr/bin/env python
import sys
import os

# Try to connect and create database
try:
    import MySQLdb
    conn = MySQLdb.connect(host='localhost', user='root', passwd='')
    cursor = conn.cursor()
    cursor.execute('CREATE DATABASE IF NOT EXISTS educoredb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
    conn.commit()
    cursor.close()
    conn.close()
    print("Database 'educoredb' created successfully!")
except ImportError:
    print("MySQLdb not available, trying pymysql...")
    try:
        import pymysql
        conn = pymysql.connect(host='localhost', user='root', password='')
        cursor = conn.cursor()
        cursor.execute('CREATE DATABASE IF NOT EXISTS educoredb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        conn.commit()
        cursor.close()
        conn.close()
        print("Database 'educoredb' created successfully!")
    except Exception as e:
        print(f"Error creating database: {e}")
        print("Please ensure MySQL is running on localhost:3306")
        sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    print("Please ensure MySQL is running on localhost:3306")
    sys.exit(1)
