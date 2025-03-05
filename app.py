from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import csv
import os
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
from keras.models import load_model

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Paths
BASE_DIR = r"C:/Users/mazin/Downloads/final"
MODEL_PATH = os.path.join(BASE_DIR, "models", "keras_model.h5")
LABELS_PATH = os.path.join(BASE_DIR, "models", "labels.txt")
STUDENTS_CSV = os.path.join(BASE_DIR, "models", "students.csv")
ATTENDANCE_CSV = os.path.join(BASE_DIR, "models", "attendance.csv")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

# Initialize model and labels
model = load_model(MODEL_PATH, compile=False)

with open(LABELS_PATH, "r") as f:
    labels = [line.strip() for line in f.readlines()]

def clean_label(label):
    return " ".join(label.split()[1:]).lower()

cleaned_labels = [clean_label(label) for label in labels]

# Load student data
def load_students_data():
    students_data = {}
    if os.path.exists(STUDENTS_CSV):
        df = pd.read_csv(STUDENTS_CSV)
        for _, row in df.iterrows():
            students_data[row["name"].lower()] = {
                "subject": row["subject"],
                "classroom": row["classroom"],
                "seat_no": str(row["seat_no"])
            }
    return students_data

# Create required directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Dictionary to track recognition attempts
recognition_attempts = {}

# NEW FUNCTION: Track and manage recognition attempts
def manage_recognition_attempts(ip_address):
    """
    Track and manage recognition attempts for a specific IP address.
    Returns True if the user still has attempts remaining, False if attempts are exhausted.
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Reset attempts if it's a new day
    if ip_address in recognition_attempts:
        if recognition_attempts[ip_address].get('date') != current_date:
            recognition_attempts[ip_address] = {'count': 0, 'date': current_date}
    else:
        recognition_attempts[ip_address] = {'count': 0, 'date': current_date}
    
    # Increment attempt count
    recognition_attempts[ip_address]['count'] += 1
    
    # Check if attempts are exhausted
    if recognition_attempts[ip_address]['count'] > 3:
        return False
    return True

# Home Page
@app.route('/')
def home():
    return render_template('home.html')

# Student Login Page
@app.route('/student_login')
def student_login():
    return render_template('index.html')

# Admin Login Page
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid Credentials')
    return render_template('admin_login.html')

# Admin Dashboard
@app.route('/admin')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    students = read_csv(STUDENTS_CSV)
    attendance = read_csv(ATTENDANCE_CSV)
    return render_template('admin.html', students=students, attendance=attendance)

# Add Student
@app.route('/add_student', methods=['POST'])
def add_student():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    name = request.form['name']
    subject = request.form['subject']
    classroom = request.form['classroom']
    seat_no = request.form['seat_no']
    write_csv(STUDENTS_CSV, [name, subject, classroom, seat_no])
    return redirect(url_for('admin_dashboard'))

# Edit Student
@app.route('/edit_student', methods=['POST'])
def edit_student():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    data = request.form.to_dict()
    update_csv(STUDENTS_CSV, data['old_name'], data)
    return redirect(url_for('admin_dashboard'))

# Delete Student
@app.route('/delete_student', methods=['POST'])
def delete_student():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    name = request.form['name']
    delete_from_csv(STUDENTS_CSV, name)
    return redirect(url_for('admin_dashboard'))

# Upload Model
@app.route('/upload_model', methods=['POST'])
def upload_model():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    file = request.files['model_file']
    if file and file.filename.endswith('.h5'):
        file.save(MODEL_PATH)
        global model
        model = load_model(MODEL_PATH, compile=False)
    return redirect(url_for('admin_dashboard'))

# CSV Utility Functions
def read_csv(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, 'r') as file:
        return list(csv.reader(file))

def write_csv(filename, row):
    with open(filename, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(row)

def update_csv(filename, old_value, new_data):
    rows = read_csv(filename)
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        for row in rows:
            if row[0] == old_value:
                writer.writerow([new_data['name'], new_data['subject'], new_data['classroom'], new_data['seat_no']])
            else:
                writer.writerow(row)

def delete_from_csv(filename, value):
    rows = read_csv(filename)
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        for row in rows:
            if row[0] != value:
                writer.writerow(row)

# Attendance Marking Function
def mark_attendance(student_name):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_key = datetime.now().strftime("%Y-%m-%d")
    
    if os.path.exists(ATTENDANCE_CSV):
        df_attendance = pd.read_csv(ATTENDANCE_CSV)
        if ((df_attendance["name"] == student_name) & (df_attendance["date"] == date_key)).any():
            return False
    
    with open(ATTENDANCE_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        if os.path.getsize(ATTENDANCE_CSV) == 0:
            writer.writerow(["name", "date", "timestamp", "status"])
        writer.writerow([student_name, date_key, timestamp, "Present"])
    
    return True

# Face Recognition Endpoint
CONFIDENCE_THRESHOLD = 80

@app.route("/recognize", methods=["POST"])
def recognize():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    # Get user IP address for tracking attempts
    ip_address = request.remote_addr
    attempts_allowed = manage_recognition_attempts(ip_address)
    
    if not attempts_allowed:
        return jsonify({"error": "Maximum recognition attempts exceeded. Access denied."}), 403
    
    file = request.files["image"]
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    image = cv2.imread(filepath)
    if image is None:
        return jsonify({"error": "Invalid image file"}), 400
    
    image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
    image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
    image = (image / 127.5) - 1
    
    prediction = model.predict(image)
    index = np.argmax(prediction[0])
    predicted_label = cleaned_labels[index]
    confidence_score = prediction[0][index] * 100
    
    os.remove(filepath)
    
    students_data = load_students_data()
    
    if confidence_score >= CONFIDENCE_THRESHOLD:
        # Reset attempts on successful recognition
        if ip_address in recognition_attempts:
            recognition_attempts[ip_address]['count'] = 0
        
        student_info = students_data.get(predicted_label, None)
        
        if student_info:
            attendance_marked = mark_attendance(predicted_label)
            
            response = {
                "name": predicted_label,
                "exam": student_info["subject"],
                "classroom": student_info["classroom"],
                "seat_no": student_info["seat_no"],
                "confidence": f"{confidence_score:.2f}%",
                "attendance": "Already Marked ✅" if not attendance_marked else "Marked ✅"
            }
        else:
            response = {"error": "Student not found", "message": "Face not recognized"}
    else:
        attempts_remaining = 3 - recognition_attempts[ip_address]['count']
        response = {
            "error": "Face not recognized",
            "message": f"Attempt {recognition_attempts[ip_address]['count']} of 3. {attempts_remaining} attempts remaining."
        }
    
    return jsonify(response)

# Logout Admin
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)