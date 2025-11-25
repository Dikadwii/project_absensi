# Panduan Deploy ke Vercel

## Persyaratan

- Akun GitHub (untuk menyimpan kode)
- Akun Vercel (gratis di https://vercel.com)
- Git installed (https://git-scm.com)

## Langkah-Langkah Deploy

### 1. Persiapan Git & GitHub

**A. Inisialisasi Git Repository (jika belum ada)**

```bash
cd c:\project_absensi
git init
```

**B. Tambahkan remote GitHub**

```bash
git remote add origin https://github.com/USERNAME/project_absensi.git
```

_Ganti `USERNAME` dengan username GitHub Anda, dan buat repo bernama `project_absensi` di GitHub_

**C. Commit semua file**

```bash
git add .
git commit -m "Initial commit - Attendance Management System"
git branch -M main
git push -u origin main
```

### 2. Deploy ke Vercel

**Opsi A: Via Vercel Dashboard (Mudah)**

1. Buka https://vercel.com/dashboard
2. Klik "New Project" → "Import Git Repository"
3. Pilih repository `project_absensi` dari GitHub
4. Di bagian "Root Directory", pastikan kosong (app.py sudah di root)
5. Klik "Environment Variables" dan tambahkan:
   - **Key**: `SECRET_KEY`
   - **Value**: `your-secret-key-here` (ganti dengan kunci unik panjang)
6. Klik "Deploy"

**Opsi B: Via Vercel CLI (Command Line)**

1. Install Vercel CLI:

   ```bash
   npm install -g vercel
   ```

2. Login ke Vercel:

   ```bash
   vercel login
   ```

3. Deploy:

   ```bash
   cd c:\project_absensi
   vercel
   ```

4. Ikuti prompts, ketika ditanya tentang project settings, pilih default
5. Ketika ditanya "Settings for existing project", pilih "No"
6. Proses deploy akan berjalan otomatis

### 3. Set Environment Variables di Vercel

Jika belum set saat deploy:

1. Buka project di https://vercel.com/dashboard
2. Klik tab "Settings"
3. Klik "Environment Variables" di sidebar
4. Tambahkan variable:
   ```
   KEY: SECRET_KEY
   VALUE: your-secret-key-here
   ```
5. Klik "Save"

### 4. Redeploy Setelah Perubahan

```bash
cd c:\project_absensi
git add .
git commit -m "Deskripsi perubahan"
git push origin main
```

Vercel akan otomatis redeploy ketika ada push ke `main` branch.

---

## Struktur File Deployment

Vercel sudah dikonfigurasi dengan file berikut:

- **vercel.json** - Konfigurasi Vercel Python Serverless Function
- **requirements.txt** - Python dependencies
- **.gitignore** - File yang diabaikan di git
- **.env.example** - Template environment variables
- **app.py** - Flask app utama (diperlukan)
- **database.py** - Database helpers (diperlukan)
- **templates/** - Jinja2 templates (diperlukan)
- **static/** - CSS & assets (diperlukan)

---

## Catatan Penting

### Database

- Saat ini menggunakan SQLite (database.db)
- SQLite di Vercel bersifat **ephemeral** - akan dihapus setiap deployment
- Untuk production dengan data persistent, gunakan:
  - **PostgreSQL** (recommended) - Vercel punya integrasi Vercel Postgres
  - **MongoDB** - lebih mudah untuk setup cepat
  - **Supabase** - PostgreSQL dengan UI admin

**Untuk sekarang**: SQLite cukup untuk testing. Jika mau persistent DB, upgrade nanti.

### Secret Key

- Saat ini hardcoded ke `'dika1234'` sebagai fallback
- Di production (Vercel), gunakan `SECRET_KEY` environment variable yang kuat
- Generate kunci kuat di: https://randomkeygen.com/

### Session Management

- Flask sessions disimpan di memory (ephemeral di Vercel)
- Untuk production dengan multiple instances, gunakan:
  - Redis session store
  - Database session store
- Untuk sekarang cukup OK untuk testing

---

## Troubleshooting

### Deployment Gagal?

1. **Check build logs**

   - Buka https://vercel.com/dashboard → Project → Deployments → Recent deployment
   - Klik "View Logs" untuk melihat error detail

2. **Common errors:**

   **Error: "ModuleNotFoundError: No module named 'flask'"**

   - Fix: Pastikan `requirements.txt` ada di root folder
   - Tambahkan dependencies yang kurang

   **Error: "ImportError in app.py"**

   - Fix: Check `database.py` ada dan accessible
   - Verify semua import statements benar

   **Error: "Port is already in use" (localhost testing)**

   - Fix: Gunakan port berbeda: `flask run --port 5001`

### App running tapi database kosong?

1. Database akan tereset setiap deployment (karena SQLite ephemeral)
2. Solusi temporary: Setup script di vercel.json untuk seed data
3. Solusi permanent: Migrasi ke PostgreSQL/MongoDB

### Login tidak berfungsi?

- Check environment variable `SECRET_KEY` sudah diset di Vercel
- Restart deployment: `vercel --prod`

---

## Testing Sebelum Deploy

Sebelum push ke GitHub, test locally:

```bash
cd c:\project_absensi
python -m venv venv
venv\Scripts\activate  (Windows)
# atau: source venv/bin/activate (Linux/Mac)

pip install -r requirements.txt
python app.py
```

Buka http://localhost:5000 dan test semua fitur.

---

## Vercel URL

Setelah deploy berhasil, Vercel akan generate URL:

- Format: `https://project-absensi-[random].vercel.app`
- URL ini akan diberikan setelah deployment selesai
- Share URL ini untuk akses app dari browser

---

## Next Steps (Optional)

1. **Custom Domain**: Beli domain, connect ke Vercel project
2. **Monitoring**: Enable Vercel Analytics untuk track usage
3. **Database Migration**: Setup PostgreSQL untuk persistent data
4. **CI/CD**: Configure automatic tests sebelum deploy
5. **Backup**: Setup regular database backups

---

## Support

Jika ada error, cek:

1. Vercel build logs: https://vercel.com/dashboard → [Project] → Deployments
2. Flask error: Check `app.py` imports dan syntax
3. Database: Verify `database.py` functions bekerja locally

---

Generated: 2024
Status: Ready to Deploy ✓
