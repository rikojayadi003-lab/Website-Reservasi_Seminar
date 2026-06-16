from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'kunci_rahasia_kampus_kamu'

# --- ROUTE: AUTENTIKASI / HOMEPAGE ---
@app.route('/')
def index():
    db = get_db_connection()
    cursor = db.cursor()
    # Mengambil daftar seminar terbaru dari database TiDB
    cursor.execute("SELECT * FROM seminar ORDER BY jadwal ASC")
    seminars = cursor.fetchall()
    db.close()
    
    # Mengirim data 'seminars' ke index.html agar bisa ditampilkan secara dinamis
    return render_template('index.html', seminars=seminars)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        role = request.form['role'] # 'mahasiswa' atau 'admin'
        
        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO user (username, password, role) VALUES (%s, %s, %s)", (username, password, role))
            db.commit() 
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.rollback()
            flash(f'Gagal mendaftar. Username mungkin sudah ada atau terjadi kesalahan: {str(e)}', 'danger')
        finally:
            db.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
        user = cursor.fetchone()
        db.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('mhs_dashboard'))
        
        flash('Username atau password salah.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# --- ROUTE: MAHASISWA ---
@app.route('/dashboard/mahasiswa')
def mhs_dashboard():
    if 'role' not in session or session['role'] != 'mahasiswa':
        return redirect(url_for('login'))
        
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM seminar")
    seminars = cursor.fetchall()
    
    cursor.execute("""
        SELECT b.id, s.judul, s.jadwal, b.status 
        FROM booking b 
        JOIN seminar s ON b.seminar_id = s.id 
        WHERE b.user_id = %s
    """, (session['user_id'],))
    my_bookings = cursor.fetchall()
    db.close()
    
    return render_template('dashboard_mhs.html', seminars=seminars, my_bookings=my_bookings)

@app.route('/booking/<int:seminar_id>', methods=['POST'])
def booking_seminar(seminar_id):
    if 'role' not in session or session['role'] != 'mahasiswa':
        return redirect(url_for('login'))
        
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM booking WHERE user_id = %s AND seminar_id = %s", (session['user_id'], seminar_id))
    exist = cursor.fetchone()
    
    if not exist:
        cursor.execute("INSERT INTO booking (user_id, seminar_id) VALUES (%s, %s)", (session['user_id'], seminar_id))
        db.commit()
        flash('Booking berhasil diajukan, menunggu persetujuan admin.', 'success')
    else:
        flash('Kamu sudah membooking seminar ini.', 'warning')
    db.close()
    return redirect(url_for('mhs_dashboard'))


# --- ROUTE: ADMIN ---
@app.route('/dashboard/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
        
    db = get_db_connection()
    cursor = db.cursor()
    
    if request.method == 'POST':
        judul = request.form['judul']
        pembicara = request.form['pembicara']
        jadwal = request.form['jadwal']
        kuota = request.form['kuota']
        
        cursor.execute("INSERT INTO seminar (judul, pembicara, jadwal, kuota) VALUES (%s, %s, %s, %s)", (judul, pembicara, jadwal, kuota))
        db.commit()
        flash('Seminar baru berhasil ditambahkan!', 'success')
        return redirect(url_for('admin_dashboard'))
        
    cursor.execute("""
        SELECT b.id, u.username, s.judul, b.status 
        FROM booking b
        JOIN user u ON b.user_id = u.id
        JOIN seminar s ON b.seminar_id = s.id
        WHERE b.status = 'pending'
    """)
    pending_bookings = cursor.fetchall()
    db.close()
    
    return render_template('dashboard_admin.html', bookings=pending_bookings)

@app.route('/admin/booking/<int:booking_id>/<string:action>')
def handle_booking(booking_id, action):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
        
    status = 'disetujui' if action == 'approve' else 'ditolak'
    
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE booking SET status = %s WHERE id = %s", (status, booking_id))
    db.commit()
    db.close()
    
    flash(f'Booking berhasil {status}.', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)