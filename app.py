from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import functools
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = 'krisha_dental_secret_key_2024'

DB_CONFIG = {
    'host':     'crossover.proxy.rlwy.net',
    'user':     'root',
    'password': 'kIrQZOaUPlWThTKsvdnlDDXMuMdgeSfE',
    'database': 'railway',
    'port':     41731
}

def get_db():
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn

def init_db():
    config = DB_CONFIG.copy()
    config.pop('database')
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS krisha_dental")
    cursor.execute("USE krisha_dental")
    cursor.execute('''CREATE TABLE IF NOT EXISTS patients (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        mobile VARCHAR(20) NOT NULL,
        password VARCHAR(500) NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS appointments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        patient_id INT,
        name VARCHAR(255) NOT NULL,
        mobile VARCHAR(20) NOT NULL,
        email VARCHAR(255) NOT NULL,
        appointment_date DATE NOT NULL,
        appointment_time TIME NOT NULL,
        reason VARCHAR(255) NOT NULL,
        branch VARCHAR(255) DEFAULT "Nallasopara West",
        status VARCHAR(50) DEFAULT "Pending",
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patient_id) REFERENCES patients(id)
    )''')
    cursor.execute("SELECT * FROM patients WHERE email = 'admin@krishadental.com'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO patients (name, email, mobile, password) VALUES (%s, %s, %s, %s)",
            ('Admin', 'admin@krishadental.com', '0000000000', generate_password_hash('admin123'))
        )
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Database connected and tables created!")

def patient_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if 'patient_id' not in session:
            flash('Please register or login first to book an appointment.', 'warning')
            return redirect(url_for('patient_login', next=request.url))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            flash('Admin access required.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/book-appointment', methods=['GET', 'POST'])
@patient_required
def book_appointment():
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        mobile   = request.form.get('mobile', '').strip()
        email    = request.form.get('email', '').strip()
        appt_date= request.form.get('appointment_date', '').strip()
        appt_time= request.form.get('appointment_time', '').strip()
        reason   = request.form.get('reason', '').strip()
        branch   = 'Nallasopara West'
        if not all([name, mobile, email, appt_date, appt_time, reason]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('book_appointment'))
        patient_id = session.get('patient_id')
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO appointments (patient_id, name, mobile, email, appointment_date, appointment_time, reason, branch) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
            (patient_id, name, mobile, email, appt_date, appt_time, reason, branch)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Appointment submitted successfully! We will confirm shortly.', 'success')
        return redirect(url_for('book_appointment'))
    return render_template('book_appointment.html')

@app.route('/patient-login', methods=['GET', 'POST'])
def patient_login():
    if 'patient_id' in session and not session.get('is_admin'):
        return redirect(url_for('patient_dashboard'))
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM patients WHERE email = %s', (email,))
        patient = cursor.fetchone()
        cursor.close()
        conn.close()
        if patient and check_password_hash(patient['password'], password) and email != 'admin@krishadental.com':
            session.clear()
            session['patient_id']   = patient['id']
            session['patient_name'] = patient['name']
            next_page = request.args.get('next') or url_for('patient_dashboard')
            return redirect(next_page)
        flash('Invalid email or password.', 'danger')
    return render_template('patient_login.html')

@app.route('/patient-register', methods=['GET', 'POST'])
def patient_register():
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip()
        mobile   = request.form.get('mobile', '').strip()
        password = request.form.get('password', '').strip()
        if not all([name, email, mobile, password]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('patient_register'))
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id FROM patients WHERE email = %s', (email,))
        existing = cursor.fetchone()
        if existing:
            cursor.close()
            conn.close()
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('patient_login'))
        cursor.execute(
            'INSERT INTO patients (name, email, mobile, password) VALUES (%s,%s,%s,%s)',
            (name, email, mobile, generate_password_hash(password))
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('patient_login'))
    return render_template('patient_register.html')

@app.route('/patient-dashboard')
@patient_required
def patient_dashboard():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM patients WHERE id = %s', (session['patient_id'],))
    patient = cursor.fetchone()
    cursor.execute(
        'SELECT * FROM appointments WHERE patient_id = %s ORDER BY appointment_date DESC, appointment_time DESC',
        (session['patient_id'],)
    )
    appointments = cursor.fetchall()
    cursor.close()
    conn.close()
    for a in appointments:
        if hasattr(a.get('appointment_date'), 'isoformat'):
            a['appointment_date'] = a['appointment_date'].isoformat()
        if hasattr(a.get('appointment_time'), 'total_seconds'):
            total_seconds = int(a['appointment_time'].total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            a['appointment_time'] = f'{hours:02d}:{minutes:02d}'
    upcoming = [a for a in appointments if a['status'] not in ('Completed', 'Rejected', 'Cancelled')]
    history  = [a for a in appointments if a['status'] in ('Completed', 'Rejected', 'Cancelled')]
    # Notification: newly approved appointments
    new_approved = [a for a in upcoming if a['status'] == 'Approved']
    return render_template('patient_dashboard.html', patient=patient, upcoming=upcoming, history=history, new_approved=new_approved)

@app.route('/patient-logout')
def patient_logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('patient_login'))

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM patients WHERE email = %s', (email,))
        admin = cursor.fetchone()
        cursor.close()
        conn.close()
        if admin and email == 'admin@krishadental.com' and check_password_hash(admin['password'], password):
            session.clear()
            session['is_admin']   = True
            session['admin_name'] = 'Admin'
            return redirect(url_for('admin_dashboard'))
        flash('Invalid admin credentials.', 'danger')
    return render_template('admin_login.html')

@app.route('/admin-logout')
def admin_logout():
    session.clear()
    flash('Admin logged out successfully.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin-dashboard')
@admin_required
def admin_dashboard():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    today = date.today().isoformat()
    cursor.execute('SELECT COUNT(*) as cnt FROM appointments')
    total = cursor.fetchone()['cnt']
    cursor.execute('SELECT COUNT(*) as cnt FROM appointments WHERE appointment_date = %s', (today,))
    today_count = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) as cnt FROM appointments WHERE status = 'Pending'")
    pending = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) as cnt FROM appointments WHERE status = 'Completed'")
    completed = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) as cnt FROM appointments WHERE status = 'Cancelled'")
    cancelled = cursor.fetchone()['cnt']
    cursor.execute("SELECT COUNT(*) as cnt FROM appointments WHERE status = 'Rescheduled'")
    rescheduled = cursor.fetchone()['cnt']
    cursor.execute('SELECT * FROM appointments WHERE appointment_date = %s ORDER BY appointment_time ASC', (today,))
    today_appts = cursor.fetchall()
    cursor.execute('SELECT * FROM appointments ORDER BY appointment_date DESC, appointment_time DESC')
    all_appts = cursor.fetchall()
    cursor.execute('SELECT * FROM appointments WHERE appointment_date < %s ORDER BY appointment_date DESC', (today,))
    past_appts = cursor.fetchall()
    cursor.execute("SELECT * FROM patients WHERE email != 'admin@krishadental.com' ORDER BY id DESC")
    all_patients = cursor.fetchall()
    cursor.close()
    conn.close()

    def fix_row(a):
        if hasattr(a.get('appointment_date'), 'isoformat'):
            a['appointment_date'] = a['appointment_date'].isoformat()
        if hasattr(a.get('appointment_time'), 'total_seconds'):
            total_seconds = int(a['appointment_time'].total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            a['appointment_time'] = f'{hours:02d}:{minutes:02d}'
        if a.get('created_at') and hasattr(a['created_at'], 'strftime'):
            a['created_at'] = a['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        return a

    today_appts = [fix_row(a) for a in today_appts]
    all_appts   = [fix_row(a) for a in all_appts]
    past_appts  = [fix_row(a) for a in past_appts]

    stats = {'total': total, 'today': today_count, 'pending': pending,
             'completed': completed, 'cancelled': cancelled, 'rescheduled': rescheduled}
    return render_template('admin_dashboard.html',
        stats=stats, today_appts=today_appts,
        all_appts=all_appts, past_appts=past_appts,
        past_count=len(past_appts), all_patients=all_patients, today=today)

@app.route('/admin/update-status/<int:appt_id>', methods=['POST'])
@admin_required
def update_status(appt_id):
    new_status = request.form.get('status')
    new_date   = request.form.get('new_date', '')
    new_time   = request.form.get('new_time', '')
    conn = get_db()
    cursor = conn.cursor()
    if new_status == 'Rescheduled' and new_date and new_time:
        cursor.execute(
            'UPDATE appointments SET status=%s, appointment_date=%s, appointment_time=%s WHERE id=%s',
            (new_status, new_date, new_time, appt_id)
        )
    else:
        cursor.execute('UPDATE appointments SET status=%s WHERE id=%s', (new_status, appt_id))
    conn.commit()
    cursor.close()
    conn.close()
    flash(f'Appointment status updated to {new_status}.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add-appointment', methods=['POST'])
@admin_required
def admin_add_appointment():
    name      = request.form.get('name', '').strip()
    mobile    = request.form.get('mobile', '').strip()
    email     = request.form.get('email', '').strip()
    appt_date = request.form.get('appointment_date', '').strip()
    appt_time = request.form.get('appointment_time', '').strip()
    reason    = request.form.get('reason', '').strip()
    if not all([name, mobile, email, appt_date, appt_time, reason]):
        flash('All fields are required.', 'danger')
        return redirect(url_for('admin_dashboard'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO appointments (name, mobile, email, appointment_date, appointment_time, reason) VALUES (%s,%s,%s,%s,%s,%s)',
        (name, mobile, email, appt_date, appt_time, reason)
    )
    conn.commit()
    cursor.close()
    conn.close()
    flash('Appointment added successfully.', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
