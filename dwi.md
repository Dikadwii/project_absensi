## Product Requirements Document (PRD)
## Aplikasi Absensi  Siswa
### 1. Tujuan Produk
Aplikasi ini bertujuan untuk memudahkan proses absensi siswa di sekolah secara digital, memungkinkan guru dan admin mengelola data absensi, siswa, dan laporan dengan efisien serta menyediakan fitur edit profil dan rekap laporan yang interaktif.

### 2. Fitur Utama
#### A. Autentikasi & Registrasi

- Guru dapat melakukan registrasi dan login menggunakan nama, mata pelajaran, dan password.
- Siswa dapat didaftarkan oleh guru ke dalam kelas masing-masing.
#### B. Dashboard Guru

Menampilkan daftar guru beserta mata pelajaran.
- Fitur pencarian dan filter guru berdasarkan nama atau mata pelajaran.
- Klik nama guru untuk melihat detail profil (nama, mata pelajaran, foto profil).
- Tombol edit profil guru untuk mengubah mata pelajaran dan password.
- Tombol logout berada di pojok kanan atas.
#### C. Manajemen Kelas & Siswa

- Guru dapat melihat daftar kelas yang diajar.
- Guru dapat melihat, menambah, mengedit, dan menghapus siswa di kelas.
- Form tambah siswa: nama, NIS, password, kelas.
- Edit data siswa: nama, NIS, password.

#### D. Absensi Siswa

Guru dapat mencatat kehadiran siswa (Hadir, Alpha, Izin, Sakit) setiap hari.
Validasi agar siswa tidak bisa absen dua kali di hari yang sama.
#### E. Laporan Absensi

Guru dapat melihat rekap absensi bulanan dan semester untuk setiap kelas.
Fitur filter berdasarkan bulan/semester.
Tabel rekap absensi yang dapat diekspor (CSV/PDF).
#### F. Role Admin (Opsional)

Admin dapat mengelola data guru, kelas, dan siswa.
Hak akses admin lebih luas dibanding guru.
### 3. Teknologi
- Backend: Python 3.11, Flask, SQLite
- Frontend: HTML, CSS, JavaScript
- Database: SQLite, tabel users, students, classes, attendance
- Keamanan: Password di-hash, validasi session, role-based access
### 4. Alur Pengguna
1. Guru melakukan registrasi dan login.
2. Guru mengelola profil, kelas, dan siswa.
3. Guru mencatat absensi siswa setiap hari.
4. Guru melihat dan mengekspor laporan absensi.
5. Admin (opsional) mengelola seluruh data.
### 5. Desain UI/UX
- Desain minimalis dan intuitif.
- Dashboard modern, responsif, dan mudah digunakan.
- Modal interaktif untuk detail dan edit profil.
- Navigasi jelas, tombol aksi mudah dijangkau.
- Warna dan ikon menarik untuk meningkatkan pengalaman pengguna.
### 6. Ekspor & Integrasi
- Laporan absensi dapat diekspor ke CSV/PDF.
- Data absensi juga dapat diintegrasikan ke sistem lain jika diperlukan.