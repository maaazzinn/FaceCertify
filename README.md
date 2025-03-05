# Face Recognition-Based Student Login & Exam Attendance

## Overview

This project is a prototype for a face recognition-based student login and exam attendance system. It allows students to log in using facial recognition, mark their exam attendance, and retrieve their exam details (such as subject name, class number, and seat number). The project is built using Flask for the backend and HTML, CSS, and JavaScript for the frontend. Custom CNN is used for face recognition.

## Features

- **Student Login via Face Recognition**
- **Automated Exam Attendance Recording**
- **Retrieval of Exam Details** (Subject Name, Class Number, Seat Number)
- **Admin Panel for Management**
- **CSV-Based Data Storage** for Students and Attendance
- **Custom Model Training**: You need to train your own face recognition model and generate `students.csv` for storing student details.

## Tech Stack

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Flask (Python)
- **Machine Learning Model:** Custom CNN
- **Database:** CSV files for storing student and attendance data

## Installation & Setup

1. **Clone the repository**

   ```sh
   git clone https://github.com/maaazzinn/FaceCertify
   cd FaceCertify
   ```

2. **Create a virtual environment and activate it**

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**

   ```sh
   pip install -r requirements.txt
   ```

4. **Train Your Model**

   - Collect images of students.
   - Train a custom CNN model for face recognition.
   - Save the trained model as `keras_model.h5` and labels in `labels.txt`.
   - Create `students.csv` containing student details.

5. **Run the Flask app**

   ```sh
   python app.py
   ```

6. **Access the Web Interface**
   Open `http://127.0.0.1:5000/` in your browser.

## Project Structure

```
final/
│-- app.py               # Main application script
│-- requirements.txt     # Required dependencies
│-- models/              # ML model and CSV-based data
│   │-- keras_model.h5   # Trained face recognition model
│   │-- labels.txt       # Corresponding labels for face recognition
│   │-- students.csv     # Student database
│   │-- attendance.csv   # Attendance records
│-- templates/           # HTML templates for the web app
│   │-- home.html        # Homepage
│   │-- admin.html       # Admin panel
│   │-- admin_login.html # Admin login page
```

## Usage

1. **Admin Panel**: Manage student records and monitor attendance.
2. **Student Login**: Recognizes students using the trained face recognition model.
3. **Attendance System**: Automatically marks student attendance upon login.
4. **Exam Seat Retrieval**: Displays assigned exam details upon successful login.

## Future Enhancements

- Integration with a database for better data management.
- Enhancing model accuracy with a larger dataset.
- Deploying as a cloud-based solution for real-world use.

## Contributing

Feel free to fork this repository and submit pull requests with improvements.

## License

This project is open-source and available under the MIT License.

