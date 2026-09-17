import os
import pickle

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import mysql.connector

from predict import predict_disease


# =========================================================
# Project Root
# =========================================================

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


# =========================================================
# Flask App
# =========================================================

app = Flask(__name__)

CORS(app)


# =========================================================
# Upload Folder
# =========================================================

UPLOAD_FOLDER = os.path.join(
    PROJECT_ROOT,
    "uploads"
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# =========================================================
# MySQL Connection
# =========================================================

def get_db_connection():

    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "localhost"),
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ.get("MYSQL_PASSWORD"),
        database=os.environ.get(
            "MYSQL_DATABASE",
            "smart_hospital"
        ),
        port=int(
            os.environ.get(
                "MYSQL_PORT",
                3306
            )
        ),
        autocommit=True
    )


# =========================================================
# Get MySQL Cursor
# =========================================================

def get_cursor(dictionary=True):

    db = None

    try:

        db = get_db_connection()

        cursor = db.cursor(
            dictionary=dictionary
        )

        return db, cursor

    except mysql.connector.Error as e:

        if db:

            try:
                db.close()

            except:
                pass

        raise e


# =========================================================
# Home
# =========================================================

@app.route("/", methods=["GET"])
def home():

    return (
        "AI Smart Hospital Assistant Backend + "
        "MySQL + ML Connected Successfully!"
    )


# =========================================================
# Serve Frontend
# =========================================================

@app.route(
    "/frontend/<path:filename>",
    methods=["GET"]
)
def serve_frontend(filename):

    frontend_folder = os.path.join(
        PROJECT_ROOT,
        "frontend"
    )

    return send_from_directory(
        frontend_folder,
        filename
    )


# =========================================================
# Patient Registration
# =========================================================

@app.route(
    "/api/register",
    methods=["POST"]
)
def register_patient():

    data = request.json or {}

    name = data.get("name")
    age = data.get("age")
    gender = data.get("gender")
    blood_group = data.get("blood_group")
    phone = data.get("phone")
    email = data.get("email")
    password = data.get("password")
    address = data.get("address")

    if not name or not email or not password:

        return jsonify({
            "message":
                "Name, email and password are required"
        }), 400

    db = None
    cursor = None

    try:

        db, cursor = get_cursor()

        cursor.execute(
            """
            INSERT INTO patients
            (
                name,
                age,
                gender,
                blood_group,
                phone,
                email,
                password_hash,
                address
            )
            VALUES
            (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                name,
                age,
                gender,
                blood_group,
                phone,
                email,
                password,
                address
            )
        )

        return jsonify({
            "message":
                "Patient registered successfully"
        }), 201

    except mysql.connector.Error as e:

        return jsonify({
            "message":
                "Registration failed",
            "error":
                str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# Patient Login
# =========================================================

@app.route(
    "/api/login",
    methods=["POST"]
)
def login_patient():

    data = request.json or {}

    email = data.get("email")
    password = data.get("password")

    db = None
    cursor = None

    try:

        db, cursor = get_cursor()

        cursor.execute(
            """
            SELECT
                patient_id,
                name,
                email
            FROM patients
            WHERE email = %s
            AND password_hash = %s
            """,
            (
                email,
                password
            )
        )

        patient = cursor.fetchone()

        if patient:

            return jsonify({

                "message":
                    "Login successful",

                "patient_id":
                    patient["patient_id"],

                "name":
                    patient["name"],

                "email":
                    patient["email"]

            }), 200

        return jsonify({
            "message":
                "Invalid email or password"
        }), 401

    except Exception as e:

        return jsonify({
            "message":
                "Login failed",
            "error":
                str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# Patient Profile
# =========================================================

@app.route(
    "/api/patient/<int:patient_id>",
    methods=["GET"]
)
def get_patient(patient_id):

    db = None
    cursor = None

    try:

        db, cursor = get_cursor()

        cursor.execute(
            """
            SELECT
                patient_id,
                name,
                age,
                gender,
                blood_group,
                phone,
                email,
                address,
                created_at
            FROM patients
            WHERE patient_id = %s
            """,
            (patient_id,)
        )

        patient = cursor.fetchone()

        if not patient:

            return jsonify({
                "message":
                    "Patient not found"
            }), 404

        return jsonify(
            patient
        ), 200

    except Exception as e:

        return jsonify({
            "message":
                "Unable to fetch patient",
            "error":
                str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# Doctors
# =========================================================

@app.route(
    "/api/doctors",
    methods=["GET"]
)
def get_doctors():

    db = None
    cursor = None

    try:

        db, cursor = get_cursor()

        cursor.execute(
            """
            SELECT
                doctor_id,
                doctor_name,
                specialization,
                experience,
                phone,
                email
            FROM doctors
            ORDER BY doctor_id
            """
        )

        doctors = cursor.fetchall()

        return jsonify(
            doctors
        ), 200

    except Exception as e:

        return jsonify({
            "message":
                "Unable to fetch doctors",
            "error":
                str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# Book Appointment
# =========================================================

@app.route(
    "/api/appointments",
    methods=["POST"]
)
def book_appointment():

    data = request.json or {}

    patient_id = data.get(
        "patient_id"
    )

    doctor_id = data.get(
        "doctor_id"
    )

    appointment_date = data.get(
        "appointment_date"
    )

    reason = data.get(
        "reason"
    )

    if (
        not patient_id
        or not doctor_id
        or not appointment_date
    ):

        return jsonify({
            "message":
                "Patient, doctor and appointment date are required"
        }), 400

    db = None
    cursor = None

    try:

        db, cursor = get_cursor()

        cursor.execute(
            """
            INSERT INTO appointments
            (
                patient_id,
                doctor_id,
                appointment_date,
                status,
                reason
            )
            VALUES
            (%s,%s,%s,%s,%s)
            """,
            (
                patient_id,
                doctor_id,
                appointment_date,
                "Pending",
                reason
            )
        )

        appointment_id = cursor.lastrowid

        return jsonify({

            "message":
                "Appointment booked successfully",

            "appointment_id":
                appointment_id

        }), 201

    except Exception as e:

        return jsonify({

            "message":
                "Unable to book appointment",

            "error":
                str(e)

        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# Patient Appointments
# =========================================================

@app.route(
    "/api/appointments/<int:patient_id>",
    methods=["GET"]
)
def get_appointments(patient_id):

    db = None
    cursor = None

    try:

        db, cursor = get_cursor()

        cursor.execute(
            """
            SELECT
                a.appointment_id,
                a.patient_id,
                a.doctor_id,
                d.doctor_name,
                d.specialization,
                a.appointment_date,
                a.status,
                a.reason,
                a.created_at
            FROM appointments a
            JOIN doctors d
                ON a.doctor_id = d.doctor_id
            WHERE a.patient_id = %s
            ORDER BY a.appointment_date DESC
            """,
            (patient_id,)
        )

        appointments = cursor.fetchall()

        return jsonify(
            appointments
        ), 200

    except Exception as e:

        return jsonify({
            "message":
                "Unable to fetch appointments",
            "error":
                str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# Upload Medical Report
# =========================================================

@app.route(
    "/api/upload-report",
    methods=["POST"]
)
def upload_report():

    patient_id = request.form.get(
        "patient_id"
    )

    report_name = request.form.get(
        "report_name"
    )

    file = request.files.get(
        "file"
    )

    if (
        not patient_id
        or not report_name
        or not file
    ):

        return jsonify({
            "message":
                "Patient ID, report name and file are required"
        }), 400

    db = None
    cursor = None

    try:

        original_filename = file.filename

        filename = (
            str(patient_id)
            + "_"
            + original_filename
        )

        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        file.save(
            file_path
        )

        db, cursor = get_cursor()

        cursor.execute(
            """
            INSERT INTO medical_reports
            (
                patient_id,
                report_name,
                file_name
            )
            VALUES
            (%s,%s,%s)
            """,
            (
                patient_id,
                report_name,
                filename
            )
        )

        return jsonify({
            "message":
                "Medical report uploaded successfully"
        }), 201

    except Exception as e:

        return jsonify({
            "message":
                "Unable to upload report",
            "error":
                str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# Get Medical Reports
# =========================================================

@app.route(
    "/api/reports/<int:patient_id>",
    methods=["GET"]
)
def get_reports(patient_id):

    db = None
    cursor = None

    try:

        db, cursor = get_cursor()

        cursor.execute(
            """
            SELECT
                report_id,
                patient_id,
                report_name,
                file_name,
                upload_date
            FROM medical_reports
            WHERE patient_id = %s
            ORDER BY upload_date DESC
            """,
            (patient_id,)
        )

        reports = cursor.fetchall()

        return jsonify(
            reports
        ), 200

    except Exception as e:

        return jsonify({
            "message":
                "Unable to fetch reports",
            "error":
                str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# Download Medical Report
# =========================================================

@app.route(
    "/api/reports/file/<filename>",
    methods=["GET"]
)
def download_report(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


# =========================================================
# Disease Prediction
# =========================================================

@app.route(
    "/api/predict",
    methods=["POST"]
)
def predict():

    data = request.json or {}

    patient_id = data.get(
        "patient_id"
    )

    age = data.get(
        "age"
    )

    gender = data.get(
        "gender"
    )

    blood_pressure = data.get(
        "blood_pressure"
    )

    sugar = data.get(
        "sugar"
    )

    heart_rate = data.get(
        "heart_rate"
    )

    symptom_score = data.get(
        "symptom_score"
    )

    if patient_id is None:

        return jsonify({
            "message":
                "Patient ID is required"
        }), 400

    db = None
    cursor = None

    try:

        disease, risk = predict_disease(
            age,
            gender,
            blood_pressure,
            sugar,
            heart_rate,
            symptom_score
        )

        db, cursor = get_cursor()

        symptoms = (
            f"BP: {blood_pressure}, "
            f"Sugar: {sugar}, "
            f"Heart Rate: {heart_rate}, "
            f"Symptom Score: {symptom_score}"
        )

        cursor.execute(
            """
            INSERT INTO medical_records
            (
                patient_id,
                symptoms,
                disease,
                risk_percentage
            )
            VALUES
            (%s,%s,%s,%s)
            """,
            (
                patient_id,
                symptoms,
                disease,
                risk
            )
        )

        record_id = cursor.lastrowid

        return jsonify({

            "message":
                "Prediction successful",

            "disease":
                disease,

            "risk_percentage":
                risk,

            "record_id":
                record_id

        }), 200

    except Exception as e:

        return jsonify({

            "message":
                "Prediction failed",

            "error":
                str(e)

        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# Prediction History
# =========================================================

@app.route(
    "/api/medical-records/<int:patient_id>",
    methods=["GET"]
)
def get_medical_records(patient_id):

    db = None
    cursor = None

    try:

        db, cursor = get_cursor()

        cursor.execute(
            """
            SELECT
                record_id,
                patient_id,
                symptoms,
                disease,
                risk_percentage,
                record_date
            FROM medical_records
            WHERE patient_id = %s
            ORDER BY record_date DESC
            """,
            (patient_id,)
        )

        records = cursor.fetchall()

        return jsonify(
            records
        ), 200

    except Exception as e:

        return jsonify({

            "message":
                "Unable to fetch medical records",

            "error":
                str(e)

        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# Analytics
# =========================================================

@app.route(
    "/api/analytics",
    methods=["GET"]
)
def get_analytics():

    db = None
    cursor = None

    try:

        db, cursor = get_cursor()

        # Total Patients

        cursor.execute(
            """
            SELECT COUNT(*) AS total_patients
            FROM patients
            """
        )

        total_patients = (
            cursor.fetchone()
            ["total_patients"]
        )


        # Total Doctors

        cursor.execute(
            """
            SELECT COUNT(*) AS total_doctors
            FROM doctors
            """
        )

        total_doctors = (
            cursor.fetchone()
            ["total_doctors"]
        )


        # Total Reports

        cursor.execute(
            """
            SELECT COUNT(*) AS total_reports
            FROM medical_reports
            """
        )

        total_reports = (
            cursor.fetchone()
            ["total_reports"]
        )


        # Total Appointments

        cursor.execute(
            """
            SELECT COUNT(*) AS total_appointments
            FROM appointments
            """
        )

        total_appointments = (
            cursor.fetchone()
            ["total_appointments"]
        )


        # Total Predictions

        cursor.execute(
            """
            SELECT COUNT(*) AS total_predictions
            FROM medical_records
            """
        )

        total_predictions = (
            cursor.fetchone()
            ["total_predictions"]
        )


        # Disease Analysis

        cursor.execute(
            """
            SELECT
                disease,
                COUNT(*) AS count
            FROM medical_records
            GROUP BY disease
            ORDER BY count DESC
            """
        )

        disease_data = cursor.fetchall()


        return jsonify({

            "total_patients":
                total_patients,

            "total_doctors":
                total_doctors,

            "total_reports":
                total_reports,

            "total_appointments":
                total_appointments,

            "total_predictions":
                total_predictions,

            "disease_analysis":
                disease_data

        }), 200

    except Exception as e:

        return jsonify({

            "message":
                "Unable to load analytics",

            "error":
                str(e)

        }), 500

    finally:

        if cursor:
            cursor.close()

        if db:
            db.close()


# =========================================================
# Run Application
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
