# 🚀 Girinka Pulse — Render Deployment Guide

This guide walks you through deploying the Girinka Pulse backend to Render.

---

## 📋 Prerequisites

1. **Render Account** — Sign up at [render.com](https://render.com)
2. **GitHub Repository** — Push your code to GitHub
3. **Cloudinary Account** — Already configured in your `.env`
4. **Resend Account** — Already configured in your `.env`

---

## 🎯 Deployment Options

### Option A: Blueprint Deployment (Automated)

Use `render.yaml` to deploy all services at once.

### Option B: Manual Deployment (Recommended for first-time)

Deploy each service individually through the Render dashboard.

---

## 🔧 Option B: Manual Deployment (Step-by-Step)

### Step 1: Create PostgreSQL Database

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **PostgreSQL**
3. Configure:
   - **Name**: `girinka-db`
   - **Database**: `girinka_pulse_db`
   - **User**: `girinka_user`
   - **Region**: Choose closest to your users (e.g., Oregon)
   - **Plan**: Starter ($7/month) or Free
4. Click **Create Database**
5. **Copy the Internal Database URL** — you'll need this for all services

---

### Step 2: Deploy Django API (Web Service)

1. Click **New +** → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `girinka-api`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn girinka.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120`
   - **Plan**: Starter ($7/month) or Free

4. **Environment Variables** — Add these:

```env
PYTHON_VERSION=3.12.0
DJANGO_SETTINGS_MODULE=girinka.settings.production
DEBUG=False

# Database (use Internal Database URL from Step 1)
DATABASE_URL=postgresql://girinka_user:YOUR_PASSWORD@dpg-xxxxx/girinka_pulse_db

# Django Secret (generate a random 50-char string)
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random

# Cloudinary (from your .env)
CLOUDINARY_CLOUD_NAME=dhforyx1s
CLOUDINARY_API_KEY=577771784241754
CLOUDINARY_API_SECRET=nWNOam5NoSZsVq_E4ySFfFZ12fk

# Resend (from your .env)
RESEND_API_KEY=re_JHLc6JkY_A72P6uHPbXxru9esC9myLZdQ
FROM_EMAIL=Girinka Pulse <no-reply@mugishajoseph.me>

# ML Service
ML_SERVICE_URL=https://girinka-pulse-ml.onrender.com

# Security
ALLOWED_HOSTS=.onrender.com
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
SECURE_SSL_REDIRECT=True

# Optional: Sentry for error tracking
SENTRY_DSN=
```

5. Click **Create Web Service**
6. Wait for deployment to complete (~5-10 minutes)
7. **Copy your API URL** (e.g., `https://girinka-api.onrender.com`)

---

### Step 3: Deploy Celery Worker (Background Service)

1. Click **New +** → **Background Worker**
2. Connect the same GitHub repository
3. Configure:
   - **Name**: `girinka-worker`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements/production.txt`
   - **Start Command**: `celery -A girinka worker -l info --concurrency=2`
   - **Plan**: Starter ($7/month) or Free

4. **Environment Variables** — Add these:

```env
PYTHON_VERSION=3.12.0
DJANGO_SETTINGS_MODULE=girinka.settings.production

# Database (same as API)
DATABASE_URL=postgresql://girinka_user:YOUR_PASSWORD@dpg-xxxxx/girinka_pulse_db

# Cloudinary (same as API)
CLOUDINARY_CLOUD_NAME=dhforyx1s
CLOUDINARY_API_KEY=577771784241754
CLOUDINARY_API_SECRET=nWNOam5NoSZsVq_E4ySFfFZ12fk

# Resend (same as API)
RESEND_API_KEY=re_JHLc6JkY_A72P6uHPbXxru9esC9myLZdQ
FROM_EMAIL=Girinka Pulse <no-reply@mugishajoseph.me>

# ML Service
ML_SERVICE_URL=https://girinka-pulse-ml.onrender.com
```

5. Click **Create Background Worker**

---

### Step 4: Deploy Celery Beat (Scheduler)

1. Click **New +** → **Background Worker**
2. Connect the same GitHub repository
3. Configure:
   - **Name**: `girinka-beat`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements/production.txt`
   - **Start Command**: `celery -A girinka beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler`
   - **Plan**: Starter ($7/month) or Free

4. **Environment Variables** — Add these:

```env
PYTHON_VERSION=3.12.0
DJANGO_SETTINGS_MODULE=girinka.settings.production

# Database (same as API)
DATABASE_URL=postgresql://girinka_user:YOUR_PASSWORD@dpg-xxxxx/girinka_pulse_db
```

5. Click **Create Background Worker**

---

## ✅ Post-Deployment Steps

### 1. Create Superuser

Go to your API service shell:

```bash
# In Render Dashboard → girinka-api → Shell
python manage.py createsuperuser
```

### 2. Verify Deployment

Test these endpoints:

```bash
# Health check
curl https://girinka-api.onrender.com/api/v1/

# API docs
https://girinka-api.onrender.com/api/v1/docs/

# Admin panel
https://girinka-api.onrender.com/admin/
```

### 3. Check Celery Tasks

```bash
# In Django Admin
https://girinka-api.onrender.com/admin/django_celery_beat/periodictask/

# Should see 9 scheduled tasks
```

### 4. Test ML Integration

```bash
curl -X GET https://girinka-api.onrender.com/api/v1/predictions/models/health_check/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🔐 Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` generated (50+ characters)
- [ ] `ALLOWED_HOSTS` set to `.onrender.com`
- [ ] `CORS_ALLOWED_ORIGINS` set to your frontend domain
- [ ] Database password is strong
- [ ] Cloudinary API secret is not exposed
- [ ] Resend API key is not exposed
- [ ] SSL redirect enabled (`SECURE_SSL_REDIRECT=True`)

---

## 📊 Monitoring

### Render Dashboard

- **Logs**: Each service has a Logs tab
- **Metrics**: CPU, Memory, Request count
- **Events**: Deployment history

### Celery Monitoring (Optional)

Deploy Flower for task monitoring:

```bash
# Add as a new web service
Start Command: celery -A girinka flower --port=$PORT
```

---

## 💰 Cost Estimate

| Service | Plan | Cost/Month |
|---------|------|------------|
| PostgreSQL | Starter | $7 |
| Django API | Starter | $7 |
| Celery Worker | Starter | $7 |
| Celery Beat | Starter | $7 |
| **Total** | | **$28/month** |

**Free Tier Option**: Use Free plan for all services (with limitations: services sleep after 15 min inactivity)

---

## 🐛 Troubleshooting

### Build Fails

**Error**: `build.sh: Permission denied`

**Fix**: Make build.sh executable before pushing to GitHub:
```bash
git update-index --chmod=+x build.sh
git commit -m "Make build.sh executable"
git push
```

### Database Connection Error

**Error**: `could not connect to server`

**Fix**: Ensure `DATABASE_URL` uses the **Internal Database URL** from Render, not External.

### Celery Not Running Tasks

**Fix**: Check that:
1. Worker service is running
2. Beat service is running
3. Both have correct `DATABASE_URL`
4. Periodic tasks are seeded (check Django Admin)

### Static Files Not Loading

**Fix**: Ensure `build.sh` runs `collectstatic`:
```bash
python manage.py collectstatic --no-input
```

### CORS Errors

**Fix**: Update `CORS_ALLOWED_ORIGINS` to include your frontend domain:
```env
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://your-frontend.com
```

---

## 🔄 Updating Your Deployment

Push changes to GitHub:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

Render will automatically redeploy all services.

---

## 📞 Support

- **Render Docs**: https://render.com/docs
- **Django Deployment**: https://docs.djangoproject.com/en/5.0/howto/deployment/
- **Celery on Render**: https://render.com/docs/deploy-celery

---

## 🎉 Success!

Your Girinka Pulse backend is now live on Render!

**API URL**: `https://girinka-api.onrender.com`
**API Docs**: `https://girinka-api.onrender.com/api/v1/docs/`
**Admin Panel**: `https://girinka-api.onrender.com/admin/`

Next steps:
1. Update your frontend to use the new API URL
2. Test all endpoints
3. Monitor logs for any errors
4. Set up Sentry for error tracking (optional)
