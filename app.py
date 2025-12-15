from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

db_config = {
    'host': '',
    'user': '',  
    'password': '',  
    'database': ''
}

def get_db_connection():
    """Establishes a connection to the database."""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as err:
        print(f"Error connecting to database: {err}")
        return None

@app.route('/')
def index():
    """Main student management page."""
    conn = get_db_connection()
    if conn is None:
        return "Error: Database connection failed."
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Student")
    students = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('index.html', students=students)

@app.route('/add_student', methods=['POST'])
def add_student():
    """Handles adding a new student via the AddStudent stored procedure."""
    form_data = request.form
    conn = get_db_connection()
    if conn is None:
        return "Error: Database connection failed."

    cursor = conn.cursor()
    try:
        cursor.callproc('AddStudent', (
            form_data['student_id'], 
            form_data['first_name'], 
            form_data['last_name'], 
            form_data['dob'], 
            form_data['gender']
        ))
        conn.commit()
    except Error as err:
        print(f"Error calling 'AddStudent' procedure: {err}")
    
    cursor.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard for managing questions."""
    conn = get_db_connection()
    if conn is None:
        return "Error: Database connection failed."
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM Course")
    courses = cursor.fetchall()
    
    cursor.execute("""
        SELECT E.Exam_ID, E.Exam_Type, C.Course_Name 
        FROM Exam E
        JOIN Course C ON E.Course_ID = C.Course_ID
        ORDER BY E.Exam_ID
    """)
    questions = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin_dashboard.html', courses=courses, questions=questions)

@app.route('/add_question', methods=['POST'])
def add_question():
    """Handles adding a new question/exam."""
    form_data = request.form
    conn = get_db_connection()
    if conn is None:
        return "Error: Database connection failed."

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT MAX(Exam_ID) FROM Exam")
        max_id_result = cursor.fetchone()
        
        new_id = (max_id_result[0] or 500) + 1

        query = "INSERT INTO Exam (Exam_ID, Course_ID, Exam_Date, Exam_Type) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (new_id, form_data['course_id'], form_data['exam_date'], form_data['exam_type']))
        conn.commit()
    except Error as err:
        print(f"Error inserting into Exam: {err}")
    
    cursor.close()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/remove_question/<int:exam_id>')
def remove_question(exam_id):
    """Handles removing a question."""
    conn = get_db_connection()
    if conn is None:
        return "Error: Database connection failed."

    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Result WHERE Exam_ID = %s", (exam_id,))
        cursor.execute("DELETE FROM Exam WHERE Exam_ID = %s", (exam_id,))
        conn.commit()
    except Error as err:
        print(f"Error deleting from Exam: {err}")
    
    cursor.close()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/departments')
def departments_page():
    """Department management page."""
    conn = get_db_connection()
    if conn is None:
        return "Error: Database connection failed."
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Department")
    departments = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('departments.html', departments=departments)

@app.route('/add_department', methods=['POST'])
def add_department():
    """Handles adding a new department."""
    form_data = request.form
    conn = get_db_connection()
    if conn is None:
        return "Error: Database connection failed."

    cursor = conn.cursor()
    try:
        query = "INSERT INTO Department (Department_ID, Department_Name, Head_of_Department) VALUES (%s, %s, %s)"
        cursor.execute(query, (form_data['dept_id'], form_data['dept_name'], form_data['hod_name']))
        conn.commit()
    except Error as err:
        print(f"Error inserting into Department: {err}")
    
    cursor.close()
    conn.close()
    return redirect(url_for('departments_page'))

@app.route('/remove_department/<int:dept_id>')
def remove_department(dept_id):
    """Handles removing a department."""
    conn = get_db_connection()
    if conn is None:
        return "Error: Database connection failed."

    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Department WHERE Department_ID = %s", (dept_id,))
        conn.commit()
    except Error as err:
        print(f"Error deleting from Department: {err}")
    
    cursor.close()
    conn.close()
    return redirect(url_for('departments_page'))

@app.route('/faculty')
def faculty_page():
    """Faculty management page."""
    conn = get_db_connection()
    if conn is None:
        return "Error: Database connection failed."
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT F.Faculty_ID, F.Faculty_Name, D.Department_Name 
        FROM Faculty F
        LEFT JOIN Department D ON F.Department_ID = D.Department_ID
        ORDER BY F.Faculty_ID
    """)
    faculty_list = cursor.fetchall()
    
    cursor.execute("SELECT * FROM Department")
    departments = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('faculty.html', faculty_list=faculty_list, departments=departments)

@app.route('/add_faculty', methods=['POST'])
def add_faculty():
    """Handles adding a new faculty member."""
    form_data = request.form
    conn = get_db_connection()
    if conn is None:
        return "Error: Database connection failed."

    cursor = conn.cursor()
    try:
        query = "INSERT INTO Faculty (Faculty_ID, Faculty_Name, Department_ID) VALUES (%s, %s, %s)"
        cursor.execute(query, (form_data['faculty_id'], form_data['faculty_name'], form_data['dept_id']))
        conn.commit()
    except Error as err:
        print(f"Error inserting into Faculty: {err}")
    
    cursor.close()
    conn.close()
    return redirect(url_for('faculty_page'))

@app.route('/remove_faculty/<int:faculty_id>')
def remove_faculty(faculty_id):
    """Handles removing a faculty member."""
    conn = get_db_connection()
    if conn is None:
        return "Error: Database connection failed."

    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Faculty WHERE Faculty_ID = %s", (faculty_id,))
        conn.commit()
    except Error as err:
        print(f"Error deleting from Faculty: {err}")
    
    cursor.close()
    conn.close()
    return redirect(url_for('faculty_page'))

@app.route('/results')
def results_page():
    """Results management page."""
    conn = get_db_connection()
    if conn is None:
        return "Error: Database connection failed."
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT 
            R.Result_ID, 
            CONCAT(S.First_Name, ' ', S.Last_Name) AS Student_Name, 
            C.Course_Name, 
            E.Exam_Type, 
            R.Marks_Obtained, 
            R.Grade 
        FROM Result R
        JOIN Student S ON R.Student_ID = S.Student_ID
        JOIN Exam E ON R.Exam_ID = E.Exam_ID
        JOIN Course C ON E.Course_ID = C.Course_ID
        ORDER BY R.Result_ID
    """)
    results = cursor.fetchall()
    
    cursor.execute("SELECT * FROM Student")
    students = cursor.fetchall()
    cursor.execute("SELECT Exam_ID, Exam_Type, Course_ID FROM Exam")
    exams = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('results.html', results=results, students=students, exams=exams)

@app.route('/add_result', methods=['POST'])
def add_result():
    """Handles adding a new result."""
    form_data = request.form
    conn = get_db_connection()
    if conn is None:
        return "Error: Database connection failed."

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT MAX(Result_ID) FROM Result")
        max_id_result = cursor.fetchone()
        new_id = (max_id_result[0] or 900) + 1 
        query = "INSERT INTO Result (Result_ID, Student_ID, Exam_ID, Marks_Obtained, Grade) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (
            new_id, 
            form_data['student_id'], 
            form_data['exam_id'], 
            form_data['marks'], 
            form_data['grade']
        ))
        conn.commit()
    except Error as err:
        print(f"Error inserting into Result: {err}")
    
    cursor.close()
    conn.close()
    return redirect(url_for('results_page'))

@app.route('/remove_result/<int:result_id>')
def remove_result(result_id):
    """Handles removing a result."""
    conn = get_db_connection()
    if conn is None:
        return "Error: Database connection failed."

    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Result WHERE Result_ID = %s", (result_id,))
        conn.commit()
    except Error as err:
        print(f"Error deleting from Result: {err}")
    
    cursor.close()
    conn.close()
    return redirect(url_for('results_page'))

if __name__ == '__main__':

    app.run(debug=True)
