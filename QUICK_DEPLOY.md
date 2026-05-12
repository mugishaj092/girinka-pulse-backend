# 🚀 Quick Deploy to Render

## Prerequisites
- GitHub account with your code pushed
- Render account (free at render.com)

## 5-Minute Deploy

### 1. Create Database
1. Go to [Render Dashboard](https://dashboard.render.com)
2. New + → PostgreSQL
3. Name: `girinka-db`, Plan: Starter
4. **Copy Internal Database URL**

### 2. Deploy API
1. New + → Web Service
2. Connect GitHub repo
3. Settings:
   - **Build**: `./build.sh`
   - **Start**: `gunicorn girinka.wsgi:application --bind 0.0.0.0:$PORT --workers 4`
4. Add Environment Variables (see below)
5. Deploy

### 3. Deploy Workers
Repeat for both:
- **Worker**: `celery -A girinka worker -l info --concurrency=2`
- **Beat**: `celery -A girinka beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler`

---

## Environment Variables (Copy-Paste Ready)

```env
# Required for all services
PYTHON_VERSION=3.12.0
DJANGO_SETTINGS_MODULE=girinka.settings.production
DATABASE_URL=<paste-internal-database-url-here>

# API only
DEBUG=False
SECRET_KEY=<generate-random-50-char-string>
ALLOWED_HOSTS=.onrender.com
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app

# Cloudinary (all services)
CLOUDINARY_CLOUD_NAME=dhforyx1s
CLOUDINARY_API_KEY=577771784241754
CLOUDINARY_API_SECRET=nWNOam5NoSZsVq_E4ySFfFZ12fk

# Resend (API + Worker)
RESEND_API_KEY=re_JHLc6JkY_A72P6uHPbXxru9esC9myLZdQ
FROM_EMAIL=Girinka Pulse <no-reply@mugishajoseph.me>

# ML Service (API + Worker)
ML_SERVICE_URL=https://girinka-pulse-ml.onrender.com
```

---

## After Deploy

### Create Admin User
In API service shell:
```bash
python manage.py createsuperuser
```

### Test Endpoints
- API: `https://your-api.onrender.com/api/v1/`
- Docs: `https://your-api.onrender.com/api/v1/docs/`
- Admin: `https://your-api.onrender.com/admin/`

---

## Troubleshooting

**Build fails?**
```bash
# Make build.sh executable locally
git update-index --chmod=+x build.sh
git commit -m "Make build.sh executable"
git push
```

**Database connection error?**
- Use **Internal Database URL**, not External
- Format: `postgresql://user:pass@host/dbname`

**Celery not running?**
- Check Worker and Beat services are running
- Verify DATABASE_URL is set on both

---

## Cost
- **Free Tier**: All services free (sleep after 15 min)
- **Starter**: $28/month (4 services × $7)

---

## Full Guide
See [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md) for detailed instructions.
