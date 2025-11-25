# 🚀 Checklist Deploy Vercel

## ✅ Sudah Siap Deploy

- [x] `app.py` - Flask application ready
- [x] `database.py` - Database helpers configured
- [x] `templates/` - All templates in place
- [x] `static/` - CSS & assets ready
- [x] `requirements.txt` - Python dependencies listed
- [x] `vercel.json` - Vercel configuration set
- [x] `.gitignore` - Excluded unnecessary files
- [x] `.env.example` - Environment template
- [x] `DEPLOY_GUIDE.md` - Deployment instructions

---

## 📋 Langkah Deploy (Cepat)

### 1️⃣ Siapkan GitHub Repository

```bash
cd c:\project_absensi
git init
git add .
git commit -m "Initial commit - Attendance System Ready for Vercel"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/project_absensi.git
git push -u origin main
```

### 2️⃣ Deploy ke Vercel

**Via Dashboard (Recommended):**

1. Buka https://vercel.com/dashboard
2. Klik "Add New..." → "Project"
3. Select repository `project_absensi`
4. Add Environment Variable:
   - `KEY`: `SECRET_KEY`
   - `VALUE`: `any-secure-key-here`
5. Click "Deploy" ✨

**Via CLI:**

```bash
npm install -g vercel
vercel login
vercel
```

### 3️⃣ Selesai! 🎉

Vercel akan memberikan URL:

- Format: `https://project-absensi-xxx.vercel.app`
- Live otomatis setelah deployment sukses

---

## 📝 Environment Variables yang Dibutuhkan

Vercel Dashboard → Settings → Environment Variables:

| Key          | Value                              | Required |
| ------------ | ---------------------------------- | -------- |
| `SECRET_KEY` | Kunci unik (dari randomkeygen.com) | ✓ Yes    |
| `FLASK_ENV`  | `production`                       | Optional |

---

## ⚠️ Important Notes

- **Database**: SQLite saat ini (ephemeral di Vercel)
  - Data akan hilang setiap deployment
  - Upgrade ke PostgreSQL/MongoDB untuk production
- **Secret Key**:
  - **Jangan** gunakan `dika1234` di production
  - Generate kunci kuat: https://randomkeygen.com/
- **Updates**:
  - Push ke GitHub → Vercel redeploy otomatis
  ```bash
  git add .
  git commit -m "Update: ..."
  git push origin main
  ```

---

## 🆘 Jika Ada Error

1. Cek Vercel Build Logs:

   - https://vercel.com/dashboard → [Project] → Deployments → [Latest] → View Logs

2. Common Issues:

   - ❌ ModuleNotFoundError → Update `requirements.txt`
   - ❌ Database error → Ubah ke PostgreSQL
   - ❌ Import error → Verify `database.py` path

3. Testing Local Dulu:
   ```bash
   pip install -r requirements.txt
   python app.py  # Test at http://localhost:5000
   ```

---

## 📚 Full Guide

Untuk petunjuk lengkap, baca: `DEPLOY_GUIDE.md`

---

## 🎯 Status: READY TO DEPLOY ✅

Semua file sudah siap. Langsung ke GitHub → Vercel!
