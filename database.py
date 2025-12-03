import sqlite3
import os
import tempfile
from werkzeug.security import generate_password_hash 

# Use an explicit DATABASE_PATH when provided (e.g. Vercel env var).
# Default to a writable temp directory to avoid permission errors on serverless
# platforms where the project root is read-only.
DATABASE = os.environ.get('DATABASE_PATH') or os.path.join(tempfile.gettempdir(), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS guru (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            nama TEXT NOT NULL,
            mata_pelajaran TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'guru'
        )
    ''')
    
    # 2. Tabel untuk Kelas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kelas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_kelas TEXT NOT NULL UNIQUE
        )
    ''')
    
    # 3. Tabel Siswa 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS siswa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            nis TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            kelas_id INTEGER,
            FOREIGN KEY (kelas_id) REFERENCES kelas (id)
        )
    ''')

        
    conn.commit()
    conn.close()


    # 4. Tabel Absensi
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            siswa_id INTEGER NOT NULL,
            status TEXT NOT NULL, 
            tanggal TEXT NOT NULL,
            recorded_by INTEGER, 
            FOREIGN KEY (siswa_id) REFERENCES siswa (id),
            FOREIGN KEY (recorded_by) REFERENCES guru (id),
            UNIQUE (siswa_id, tanggal)
        )
    ''')
    conn.commit()
    conn.close()

    # Seed a default guru account when running in a fresh environment (e.g. serverless)
    # This uses environment variables ADMIN_EMAIL and ADMIN_PASSWORD. If provided and
    # no guru records exist, a default guru will be created so you can login on first deploy.
    try:
        admin_email = os.environ.get('ADMIN_EMAIL')
        admin_password = os.environ.get('ADMIN_PASSWORD')
        conn = get_db_connection()
        cur = conn.execute("SELECT COUNT(*) as cnt FROM guru").fetchone()
        exists = cur['cnt'] if cur is not None else 0
        if exists == 0 and admin_email and admin_password:
            hashed = generate_password_hash(admin_password)
            conn.execute("INSERT INTO guru (email, nama, mata_pelajaran, password, role) VALUES (?, ?, ?, ?, ?)",
                         (admin_email, os.environ.get('ADMIN_NAME', 'Admin'), os.environ.get('ADMIN_MAPEL', 'Administrator'), hashed, 'guru'))
            conn.commit()
        conn.close()
    except Exception as e:
        # avoid breaking init on serverless; log to stdout
        print('Warning: seeding default admin failed:', e)



def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT id, nama, email, mata_pelajaran, role FROM guru WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user

def get_all_users(search_term=None, filter_mapel=None):
    conn = get_db_connection()
    query = "SELECT id, nama, mata_pelajaran, role FROM guru WHERE role = 'guru'"
    params = []
    
    if search_term:
        query += " AND (nama LIKE ? OR mata_pelajaran LIKE ?)"
        search_param = '%' + search_term + '%'
        params.extend([search_param, search_param])
        
    if filter_mapel and filter_mapel != 'Semua':
        query += " AND mata_pelajaran = ?" 
        params.append(filter_mapel)

    query += " ORDER BY nama" 
    
    users = conn.execute(query, tuple(params)).fetchall()
    conn.close()
    return users

def get_list_mapel():
    # Mengambil daftar mata pelajaran unik (MENGGUNAKAN TABEL 'guru').
    conn = get_db_connection()
    mapel = conn.execute("SELECT DISTINCT mata_pelajaran FROM guru ORDER BY mata_pelajaran").fetchall()
    conn.close()
    return [m['mata_pelajaran'] for m in mapel]


def get_all_kelas():
    # Mengambil semua daftar kelas yang ada.
    conn = get_db_connection()
    kelas_list = conn.execute("SELECT id, nama_kelas FROM kelas ORDER BY nama_kelas").fetchall()
    conn.close()
    return kelas_list

def get_kelas_by_id(kelas_id):
    # Mengambil detail satu kelas berdasarkan ID.
    conn = get_db_connection()
    kelas = conn.execute("SELECT id, nama_kelas FROM kelas WHERE id = ?", (kelas_id,)).fetchone()
    conn.close()
    return kelas


def update_siswa_kelas(siswa_id, kelas_id):
    #Perbarui kelas siswa (set kelas_id).
    conn = get_db_connection()
    try:
        conn.execute("UPDATE siswa SET kelas_id = ? WHERE id = ?", (kelas_id, siswa_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating siswa kelas: {e}")
        return False
    finally:
        conn.close()

def add_kelas(nama_kelas):
    # Menambahkan kelas baru ke database.
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO kelas (nama_kelas) VALUES (?)", (nama_kelas,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False 
    finally:
        conn.close()

def delete_kelas_by_id(kelas_id):
    # Menghapus kelas berdasarkan ID dan membersihkan referensi siswa.
    conn = get_db_connection()
    try:
        # PENTING: Set kelas_id siswa yang terkait menjadi NULL 
        conn.execute("UPDATE siswa SET kelas_id = NULL WHERE kelas_id = ?", (kelas_id,))
        conn.execute("DELETE FROM kelas WHERE id = ?", (kelas_id,))
        conn.commit()
        #relasi database dan constraints
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error menghapus kelas: {e}")
        return False
    finally:
        conn.close()


def get_siswa_by_kelas(kelas_id):
    # Mengambil semua siswa yang terdaftar dalam kelas tertentu.
    conn = get_db_connection()
    siswa_list = conn.execute(
        "SELECT id, nama, nis FROM siswa WHERE kelas_id = ? ORDER BY nama", 
        (kelas_id,)
    ).fetchall()
    conn.close()
    return siswa_list

def add_new_siswa(nama, nis, kelas_id, password_mentah):
     # Menyimpan data siswa baru ke database, termasuk password yang di-hash.
    conn = get_db_connection()
    cursor = conn.cursor()
    
    hashed_password = generate_password_hash(password_mentah)
    
    try:
        cursor.execute("""
            INSERT INTO siswa (nama, nis, kelas_id, password)
            VALUES (?, ?, ?, ?)
        """, (nama, nis, kelas_id, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Contoh: jika NIS sudah ada
        return False
    except Exception as e:
        print(f"Database Error: {e}")
        return False
    finally:
        conn.close()

def get_siswa_by_nis(nis):
    # Mengambil data siswa lengkap berdasarkan NIS.
    conn = get_db_connection()
    siswa = conn.execute("SELECT * FROM siswa WHERE nis = ?", (nis,)).fetchone()
    conn.close()
    return siswa

def get_siswa_by_nama(nama):
    # Mengambil data siswa lengkap berdasarkan NAMA.
    conn = get_db_connection()
    siswa = conn.execute("SELECT * FROM siswa WHERE nama = ?", (nama,)).fetchone()
    conn.close()
    return siswa

def get_siswa_by_id(siswa_id):
    # Mengambil data siswa lengkap berdasarkan ID.
    conn = get_db_connection()
    siswa = conn.execute("SELECT * FROM siswa WHERE id = ?", (siswa_id,)).fetchone()
    conn.close()
    return siswa


def get_siswa_by_search(nama, kelas_id=None):
    """Cari siswa berdasarkan nama (partial match). Jika `kelas_id` diberikan, batasi pencarian ke kelas tersebut.
    Mengembalikan satu baris (first match) atau None."""
    conn = get_db_connection()
    params = []
    query = "SELECT * FROM siswa WHERE nama LIKE ?"
    params.append('%' + nama + '%')
    if kelas_id:
        query += " AND kelas_id = ?"
        params.append(kelas_id)
    query += " ORDER BY nama LIMIT 1"
    siswa = conn.execute(query, tuple(params)).fetchone()
    conn.close()
    return siswa

def get_all_siswa():
    # Mengambil semua siswa (untuk laporan/index)
    conn = get_db_connection()
    rows = conn.execute("SELECT id, nama, nis, kelas_id FROM siswa ORDER BY nama").fetchall()
    conn.close()
    return rows

def get_nama_kelas_by_id(kelas_id):
    conn = get_db_connection()
    kelas = conn.execute("SELECT nama_kelas FROM kelas WHERE id = ?", (kelas_id,)).fetchone()
    conn.close()

    return kelas['nama_kelas'] if kelas else "kelas tidak diketahui"

def add_attendance(siswa_id, status, tanggal, recorded_by=None):
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO attendance (siswa_id, status, tanggal, recorded_by) VALUES (?, ?, ?, ?)",
            (siswa_id, status, tanggal, recorded_by)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:

        return False
    except Exception as e:
        print(f"Error adding attendance: {e}")
        return False
    finally:
        conn.close()


def attendance_exists(siswa_id, tanggal):
    conn = get_db_connection()
    cur = conn.execute("SELECT id FROM attendance WHERE siswa_id = ? AND tanggal = ?", (siswa_id, tanggal)).fetchone()
    conn.close()
    return cur is not None


def get_attendance_for_student(siswa_id, limit=100):
    conn = get_db_connection()
    rows = conn.execute(
        """
        SELECT a.id, a.siswa_id, a.status, a.tanggal, a.recorded_by, g.nama AS recorded_by_name
        FROM attendance a
        LEFT JOIN guru g ON a.recorded_by = g.id
        WHERE a.siswa_id = ?
        ORDER BY a.tanggal DESC
        LIMIT ?
        """,
        (siswa_id, limit)
    ).fetchall()
    conn.close()
    return rows

def delete_siswa_by_id(siswa_id):
    # Menghapus siswa berdasarkan ID.
    conn = get_db_connection()
    try:
        conn.execute("DELETE FROM siswa WHERE id = ?", (siswa_id,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error menghapus siswa: {e}")
        return False
    finally:
        conn.close()

