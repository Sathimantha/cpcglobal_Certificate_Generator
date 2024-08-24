import mariadb
import sys
from datetime import datetime
from config import DB_CONFIG

def get_db_connection():
    try:
        conn = mariadb.connect(**DB_CONFIG)
        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        sys.exit(1)

def get_person(search_term):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    query = """
    SELECT * FROM students 
    WHERE student_id = ? OR LOWER(full_name) = LOWER(?) OR NID = ?
    """
    
    cur.execute(query, (search_term, search_term, search_term))
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    return result

def get_all_students():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    
    cur.execute("SELECT * FROM students")
    result = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return result

def create_students_table():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        student_id VARCHAR(50) PRIMARY KEY,
        full_name VARCHAR(100) NOT NULL,
        NID VARCHAR(20),
        phone_no VARCHAR(20),
        remark LONGTEXT
    )
    """)
    
    conn.commit()
    cur.close()
    conn.close()

def import_excel_to_db(excel_file):
    import pandas as pd
    df = pd.read_excel(excel_file)
    conn = get_db_connection()
    cur = conn.cursor()
    
    for _, row in df.iterrows():
        cur.execute("""
        INSERT INTO students (student_id, full_name, NID, phone_no, remark)
        VALUES (?, ?, ?, ?, ?)
        ON DUPLICATE KEY UPDATE
        full_name = VALUES(full_name),
        NID = VALUES(NID),
        phone_no = VALUES(phone_no)
        """, (str(row['student_id']), row['full_name'], row['NID'], str(row['phone_no']), ""))
    
    conn.commit()
    cur.close()
    conn.close()

def log_certificate_download(student_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_remark = f"Certificate downloaded on {timestamp}"
    
    cur.execute("""
    UPDATE students
    SET remark = CASE
        WHEN remark IS NULL OR remark = '' THEN ?
        ELSE CONCAT(remark, '\n', ?)
    END
    WHERE student_id = ?
    """, (new_remark, new_remark, student_id))
    
    conn.commit()
    cur.close()
    conn.close()

def add_remark(student_id, new_remark):
    conn = get_db_connection()
    cur = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_remark = f"[{timestamp}] {new_remark}"
    
    cur.execute("""
    UPDATE students
    SET remark = CASE
        WHEN remark IS NULL OR remark = '' THEN ?
        ELSE CONCAT(remark, '\n', ?)
    END
    WHERE student_id = ?
    """, (formatted_remark, formatted_remark, student_id))
    
    conn.commit()
    cur.close()
    conn.close()

def get_download_stats():
    #Turned off due to cybersecurity concerns
    #    conn = get_db_connection()
    #    cur = conn.cursor(dictionary=True)
    #    
    #    cur.execute("""
    #    SELECT 
    #        COUNT(*) as total_downloads,
    #        COUNT(DISTINCT student_id) as unique_students,
    #        SUM(CASE WHEN remark LIKE '%Certificate downloaded on%' 
    #                  AND STR_TO_DATE(SUBSTRING_INDEX(SUBSTRING_INDEX(remark, 'Certificate downloaded on ', -1), '\n', 1), '%Y-%m-%d %H:%i:%s') > DATE_SUB(NOW(), INTERVAL 7 DAY) 
    #            THEN 1 ELSE 0 END) as recent_downloads
    #    FROM students
    #    WHERE remark LIKE '%Certificate downloaded on%'
    #    """)
    #    
    #    result = cur.fetchone()
    #    
    #   cur.close()
    #    conn.close()
    #    
    #    return result
    return 0