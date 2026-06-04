# 🎂 Birthday Memories — Complete Setup Guide

## What's inside

| Page | URL | Access |
|------|-----|--------|
| Home | `/` | Public — search by DOB |
| Birthday | `/1999-06-01/` | Public — dreamy celebration page |
| Manage | `/1999-06-01/manage/` | Password per page |
| **Admin Portal** | `/admin-portal/` | **You only — master password** |
| Create | `/create/` | Admin only (redirects if not logged in) |

---

## 🔐 Admin Portal (new!)

Visit `/admin-portal/` — this URL is **not linked anywhere** on the public site.

- **Default master password:** `birthday@admin2025`
- Change it by setting `ADMIN_MASTER_PASSWORD` in your `.env`
- From the portal you can: create pages, delete pages, view all pages + photo counts

---

## ☁️ Cloudinary Setup (free photo storage — 25 GB!)

1. Sign up free at **cloudinary.com**
2. Go to your Dashboard → copy Cloud Name, API Key, API Secret
3. Add to your `.env` file:

```
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

That's it — all uploaded photos automatically go to Cloudinary!

> **Without Cloudinary:** photos are stored locally (fine for PythonAnywhere / Fly.io).

---

## 🚀 Run locally

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
# Open: http://127.0.0.1:8000/
# Admin: http://127.0.0.1:8000/admin-portal/
```

---

## 🌐 Free Hosting — PythonAnywhere

1. Sign up at **pythonanywhere.com** → get `yourname.pythonanywhere.com`
2. Upload zip via Files tab → extract
3. Bash console:
   ```bash
   pip install -r requirements.txt --user
   python manage.py migrate
   ```
4. Web tab → Add web app → Manual → Python 3.12 → set WSGI config
5. Static: `/static/` → `staticfiles/`, Media: `/media/` → `media/`
6. Add env vars in the WSGI file or a `.env` file
7. Reload → share your URL!

---

## 🎵 Song tips
- Upload MP3 directly on the Manage page
- Google Drive: `https://drive.google.com/uc?export=download&id=FILE_ID`
- Dropbox: change `dl=0` → `dl=1` in share URL
