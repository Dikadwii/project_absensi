from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from database import (
    init_db, get_db_connection, get_user_by_id, get_all_users, get_list_mapel,
    get_all_kelas, add_kelas, delete_kelas_by_id, get_kelas_by_id, 
    get_siswa_by_kelas, add_new_siswa, delete_siswa_by_id, get_siswa_by_nis,
    add_attendance, attendance_exists, get_attendance_for_student, update_siswa_kelas
)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dika1234') 


with app.app_context():
    init_db()

def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('home')) 
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM guru WHERE email = ?", (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        return render_template('login.html', error="Email atau password salah")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        #breakpoint()
        nama = request.form['nama']
        email = request.form['email']
        mata_pelajaran = request.form['mata_pelajaran']
        password = request.form['password']
        conn = get_db_connection()
        hashed_password = generate_password_hash(password)
        try:
            conn.execute(
                "INSERT INTO guru (nama, email, mata_pelajaran, password, role) VALUES (?, ?, ?, ?, ?)",
                (nama, email, mata_pelajaran, hashed_password, 'guru')
            )
            conn.commit()
            return render_template('login.html', success="Registrasi berhasil, silakan login")
        except sqlite3.IntegrityError:
            conn.rollback()
            return render_template('register.html', error="Email sudah terdaftar. Mohon gunakan email lain.")
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))



@app.route('/dashboard')
@login_required
def dashboard():
    guru = get_user_by_id(session['user_id'])
    
    # Logika Filter dan Pencarian Guru
    search_term = request.args.get('search', '').strip()
    filter_mapel = request.args.get('mapel', 'Semua')
    all_users = get_all_users(search_term, filter_mapel)
    mapel_list = get_list_mapel()

    return render_template('dashboard.html', 
                           guru=guru, 
                           all_users=all_users, 
                           mapel_list=mapel_list,
                           current_search=search_term,
                           current_mapel=filter_mapel)

@app.route('/manage_kelas', methods=['GET', 'POST'])
@login_required
def manage_kelas():
    message = request.args.get('msg')
    msg_type = request.args.get('type', 'success')
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            nama_kelas = request.form['nama_kelas'].strip()
            
            if not nama_kelas:
                return redirect(url_for('manage_kelas', msg="Nama kelas tidak boleh kosong.", type='error'))
            
            if add_kelas(nama_kelas):
                return redirect(url_for('manage_kelas', msg=f"Kelas '{nama_kelas}' berhasil ditambahkan."))
            else:
                return redirect(url_for('manage_kelas', msg=f"Kelas '{nama_kelas}' sudah ada di database.", type='error'))

    kelas_list = get_all_kelas()
    return render_template('manage_kelas.html', 
                           kelas_list=kelas_list,
                           message=message,
                           msg_type=msg_type)


@app.route('/delete_kelas/<int:kelas_id>', methods=['POST'])
@login_required
def delete_kelas(kelas_id):
    if delete_kelas_by_id(kelas_id):
        return redirect(url_for('manage_kelas', msg="Kelas berhasil dihapus."))
    else:
        return redirect(url_for('manage_kelas', msg="Gagal menghapus kelas.", type='error'))

        
@app.route('/manage_kelas/<int:kelas_id>')
@login_required
def detail_kelas(kelas_id):
    # Menampilkan detail kelas dan daftar siswa
    kelas = get_kelas_by_id(kelas_id)
    
    if not kelas:
        return redirect(url_for('manage_kelas', msg="Kelas tidak ditemukan.", type='error'))
    
    siswa_list = get_siswa_by_kelas(kelas_id)
    message = request.args.get('msg')
    msg_type = request.args.get('type', 'success')
    
    return render_template('detail_kelas.html', 
                           kelas=kelas, 
                           siswa_list=siswa_list,
                           message=message,
                           msg_type=msg_type)

@app.route('/kelas/<int:kelas_id>/add_siswa', methods=['POST'])
def add_siswa_to_kelas(kelas_id):
    # Ambil data dari form
    nama = request.form.get('nama')
    nis = request.form.get('nis')
    password_mentah = request.form.get('password') 
    existing = get_siswa_by_nis(nis)
    if existing:
        message = f"Gagal: NIS {nis} sudah terdaftar (Nama: {existing['nama']})."
        return redirect(url_for('detail_kelas', kelas_id=kelas_id, msg=message, type='error'))

    success = add_new_siswa(nama, nis, kelas_id, password_mentah)

    if success:
        message = f"Siswa {nama} berhasil ditambahkan ke kelas."
        msg_type = 'success'
    else:
        message = f"Gagal menambahkan siswa. Terjadi kesalahan saat menyimpan."
        msg_type = 'error'

    return redirect(url_for('detail_kelas', kelas_id=kelas_id, msg=message, type=msg_type))


@app.route('/delete_siswa/<int:siswa_id>', methods=['POST'])
@login_required
def delete_siswa_route(siswa_id):
    # Menghapus siswa berdasarkan ID dan mengarahkan kembali ke kelas asalnya.
    conn = get_db_connection()
    siswa = conn.execute("SELECT kelas_id FROM siswa WHERE id = ?", (siswa_id,)).fetchone()
    conn.close()
    
    if not siswa:
        return redirect(url_for('manage_kelas', msg="Siswa tidak ditemukan.", type='error'))
        
    kelas_id = siswa['kelas_id']
    
    if delete_siswa_by_id(siswa_id):
        return redirect(url_for('detail_kelas', kelas_id=kelas_id, msg="Siswa berhasil dihapus."))
    else:
        return redirect(url_for('detail_kelas', kelas_id=kelas_id, msg="Gagal menghapus siswa.", type='error'))

        
@app.route('/login/siswa', methods=['GET', 'POST'])
def siswa_login():
    # show available kelas for selection
    kelas_list = get_all_kelas()

    if request.method == 'POST':
        nis_input = request.form.get('nis')
        password_input = request.form.get('password')
        selected_kelas = request.form.get('kelas_id')
        try:
            siswa = get_siswa_by_nis(nis_input)

            if siswa:
                if check_password_hash(siswa['password'], password_input):
                    session['user_type'] = 'siswa'
                    session['user_id'] = siswa['id']
                    session['user_nama'] = siswa['nama']
                    # jika siswa belum punya kelas, dan user memilih kelas saat login, update DB
                    try:
                        if (not siswa['kelas_id'] or siswa['kelas_id'] is None) and selected_kelas:
                            sid = int(selected_kelas)
                            update_siswa_kelas(siswa['id'], sid)
                            siswa = get_siswa_by_nis(nis_input)  # refresh
                        session['user_kelas_id'] = siswa['kelas_id']
                    except Exception:
                        session['user_kelas_id'] = siswa['kelas_id']

                    return redirect(url_for('siswa_dashboard'))
                else:
                    return render_template('login_siswa.html', error_message='NIS atau Password salah.', kelas_list=kelas_list)
            else:
                return render_template('login_siswa.html', error_message='NIS atau Password salah.', kelas_list=kelas_list)
        except Exception as e:
            print(f"Error during siswa_login: {e}")
            return render_template('login_siswa.html', error_message='Terjadi kesalahan saat login. Silakan coba lagi atau hubungi admin.', kelas_list=kelas_list)

    return render_template('login_siswa.html', kelas_list=kelas_list)

@app.route('/catat_absensi')
@login_required
def catat_absensi():
    nis = request.args.get('nis')
    import datetime
    tanggal = datetime.date.today().isoformat()

    siswa = None
    exists = False
    existing_status = None
    checked = False
    if nis:
        checked = True
        siswa = get_siswa_by_nis(nis)
        if siswa:
            if attendance_exists(siswa['id'], tanggal):
                exists = True
                rows = get_attendance_for_student(siswa['id'], limit=200)
                for r in rows:
                    if r['tanggal'] == tanggal:
                        existing_status = r['status']
                        break

    return render_template('catat_absensi.html', 
                           siswa=siswa, 
                           exists=exists, 
                           existing_status=existing_status, 
                           tanggal=tanggal, 
                           checked=checked)


@app.route('/siswa/dashboard')
def siswa_dashboard():  
    if session.get('user_type') != 'siswa' or 'user_id' not in session:
        return redirect(url_for('home'))
    siswa = None
    conn = get_db_connection()
    siswa = conn.execute("SELECT * FROM siswa WHERE id = ?", (session['user_id'],)).fetchone()
    conn.close()
    if not siswa:
        return redirect(url_for('home'))

    import datetime
    today = datetime.date.today().isoformat()
    has_today = attendance_exists(siswa['id'], today)
    today_status = None
    if has_today:
        row = get_attendance_for_student(siswa['id'], limit=1)[0]
        today_status = row['status']

    attendance = get_attendance_for_student(siswa['id'], limit=50)

    
    kelas = None
    kelas_id = None
    try:
        kelas_id = siswa['kelas_id']
    except Exception:
        kelas_id = None

    if kelas_id:
        kelas = get_kelas_by_id(kelas_id)

    return render_template('siswa_dashboard.html', 
                           siswa=siswa, 
                           kelas=kelas,
                           today=today, 
                           has_today=has_today,
                           today_status=today_status, 
                           attendance=attendance)


@app.route('/siswa/absen', methods=['POST'])
def siswa_absen():
    if session.get('user_type') != 'siswa' or 'user_id' not in session:
        return redirect(url_for('home'))
    siswa_id = request.form.get('siswa_id') or session['user_id']
    status = request.form.get('status')
    import datetime
    today = datetime.date.today().isoformat()
    if attendance_exists(siswa_id, today):
        return redirect(url_for('siswa_dashboard'))
    ok = add_attendance(siswa_id, status, today, recorded_by=None)
    return redirect(url_for('siswa_dashboard'))


@app.route('/catat_absensi', methods=['POST'])
@login_required
def catat_absensi_post():
    guru = get_user_by_id(session['user_id'])
    if not guru or guru['role'] != 'guru':
        return "Hanya guru yang dapat mengakses ini", 403
    siswa_id = request.form.get('siswa_id')
    nis = request.form.get('nis')
    status = request.form.get('status')
    import datetime
    tanggal = datetime.date.today().isoformat()
    if not siswa_id and nis:
        s = get_siswa_by_nis(nis)
        if s:
            siswa_id = s['id']
    if not siswa_id:
        return redirect(url_for('catat_absensi', nis=nis, tanggal=tanggal, msg='Siswa tidak ditemukan', type='error'))
    if attendance_exists(siswa_id, tanggal):
        return redirect(url_for('dashboard', msg='Absensi sudah dicatat untuk siswa ini pada tanggal tersebut', type='error'))
    ok = add_attendance(siswa_id, status, tanggal, recorded_by=guru['id'])
    if ok:
        return redirect(url_for('dashboard', msg='Absensi berhasil dicatat'))
    else:
        return redirect(url_for('dashboard', msg='Gagal mencatat absensi', type='error'))


@app.route('/kelas/<int:kelas_id>/absensi', methods=['GET', 'POST'])
@login_required
def kelas_absensi(kelas_id):
    guru = get_user_by_id(session['user_id'])
    if not guru or guru['role'] != 'guru':
        return "Hanya guru yang dapat mengakses ini", 403

    kelas = get_kelas_by_id(kelas_id)
    if not kelas:
        return redirect(url_for('manage_kelas', msg='Kelas tidak ditemukan', type='error'))

    siswa_list = get_siswa_by_kelas(kelas_id)
    import datetime
    today = datetime.date.today().isoformat()

    attendance_map = {}
    for s in siswa_list:
        rows = get_attendance_for_student(s['id'], limit=1)
        if rows:
            if rows[0]['tanggal'] == today:
                attendance_map[s['id']] = rows[0]['status']

    if request.method == 'POST':
        any_changed = False
        for s in siswa_list:
            field = f"status_{s['id']}"
            status = request.form.get(field)
            if status:
                if attendance_exists(s['id'], today):
                    continue
                ok = add_attendance(s['id'], status, today, recorded_by=guru['id'])
                if ok:
                    any_changed = True

        if any_changed:
            return redirect(url_for('kelas_absensi', kelas_id=kelas_id, msg='Absensi berhasil disimpan'))
        else:
            return redirect(url_for('kelas_absensi', kelas_id=kelas_id, msg='Tidak ada perubahan atau absensi sudah ada untuk beberapa siswa', type='error'))

    message = request.args.get('msg')
    msg_type = request.args.get('type', 'success')
    return render_template('kelas_absensi.html', kelas=kelas, siswa_list=siswa_list, guru=guru, today=today, attendance_map=attendance_map, message=message, msg_type=msg_type)


@app.route('/laporan_absensi/<int:siswa_id>')
@login_required
def laporan_absensi(siswa_id):
    guru = get_user_by_id(session['user_id'])
    if not guru or guru['role'] != 'guru':
        return "Hanya guru yang dapat mengakses ini", 403

    from database import get_siswa_by_id
    siswa_row = get_siswa_by_id(siswa_id)
    if not siswa_row:
        return redirect(url_for('dashboard', msg='Siswa tidak ditemukan', type='error'))

    try:
        siswa = dict(siswa_row)
    except Exception:
        siswa = {k: siswa_row[k] for k in siswa_row.keys()} if siswa_row else {}

    if 'nama_siswa' not in siswa:
        siswa['nama_siswa'] = siswa.get('nama')

    attendance_records = get_attendance_for_student(siswa_id, limit=500)

    from collections import defaultdict
    import datetime

    laporan_bulanan = defaultdict(lambda: {'hadir':0, 'sakit':0, 'izin':0, 'alpa':0})
    laporan_semester = defaultdict(lambda: {'hadir':0, 'sakit':0, 'izin':0, 'alpa':0})

    for r in attendance_records:
        try:
            dt = datetime.datetime.fromisoformat(r['tanggal'])
        except Exception:
            dt = datetime.datetime.strptime(r['tanggal'], '%Y-%m-%d')

        bulan_label = dt.strftime('%Y-%m')
        sem_label = 'Semester 1' if dt.month <=6 else 'Semester 2'
        key_sem = f"{dt.year} {sem_label}"

        status = (r['status'] or '').lower()
        if 'hadir' in status or status == 'h' or status == 'present':
            field = 'hadir'
        elif 'sakit' in status or status == 's':
            field = 'sakit'
        elif 'izin' in status or status == 'i':
            field = 'izin'
        else:
            field = 'alpa'

        laporan_bulanan[bulan_label][field] += 1
        laporan_semester[key_sem][field] += 1

    laporan_bulanan = dict(laporan_bulanan)
    laporan_semester = dict(laporan_semester)

   

    return render_template('laporan_absensi.html', siswa=siswa, attendance_records=attendance_records, guru=guru, laporan_bulanan=laporan_bulanan, laporan_semester=laporan_semester)


@app.route('/laporan')
@login_required
def laporan_index():
    guru = get_user_by_id(session['user_id'])
    if not guru or guru['role'] != 'guru':
        return "Hanya guru yang dapat mengakses ini", 403

    from database import get_all_siswa, get_nama_kelas_by_id
    siswa_list = get_all_siswa()
    return render_template('laporan_index.html', siswa_list=siswa_list, get_nama_kelas_by_id=get_nama_kelas_by_id)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    guru = get_user_by_id(session['user_id'])
    if not guru:
        return redirect(url_for('dashboard', msg='User tidak ditemukan', type='error'))

    if request.method == 'POST':
        nama = request.form.get('nama')
        email = request.form.get('email')
        mata_pelajaran = request.form.get('mata_pelajaran')
        password = request.form.get('password')

        conn = get_db_connection()
        try:
            if password:
                hashed_password = generate_password_hash(password)
                conn.execute(
                    "UPDATE guru SET nama = ?, email = ?, mata_pelajaran = ?, password = ? WHERE id = ?",
                    (nama, email, mata_pelajaran, hashed_password, guru['id'])
                )
            else:
                conn.execute(
                    "UPDATE guru SET nama = ?, email = ?, mata_pelajaran = ? WHERE id = ?",
                    (nama, email, mata_pelajaran, guru['id'])
                )
            conn.commit()
            return redirect(url_for('dashboard', msg='Profil berhasil diperbarui'))
        except sqlite3.IntegrityError:
            conn.rollback()
            return render_template('edit_profile.html', guru=guru, error="Email sudah terdaftar. Mohon gunakan email lain.")
        finally:
            conn.close()

    return render_template('edit_profile.html', guru=guru)
      
@app.route('/lihat_detail_guru/<int:guru_id>')
@login_required
def lihat_detail_guru(guru_id):
    guru = get_user_by_id(session['user_id'])
    if not guru or guru['role'] != 'guru':
        return "Hanya guru yang dapat mengakses ini", 403

    detail_guru = get_user_by_id(guru_id)
    if not detail_guru:
        return redirect(url_for('dashboard', msg='Guru tidak ditemukan', type='error'))

    return render_template('detail_guru.html', guru=guru, detail_guru=detail_guru)



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)