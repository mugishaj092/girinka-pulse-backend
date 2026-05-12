# ✅ Render Deployment Checklist

## Pre-Deployment

- [ ] Code pushed to GitHub
- [ ] `build.sh` is executable (`git update-index --chmod=+x build.sh`)
- [ ] All tests passing locally (`pytest tests/ -v`)
- [ ] `.env.render` reviewed and values prepared
- [ ] Cloudinary credentials verified
- [ ] Resend API key verified
- [ ] ML service URL confirmed: https://girinka-pulse-ml.onrender.com

---

## Render Setup

### Database
- [ ] PostgreSQL database created on Render
- [ ] Database name: `girinka_pulse_db`
- [ ] Internal Database URL copied
- [ ] Database plan selected (Free or Starter)

### API Service (Web)
- [ ] Web service created and connected to GitHub
- [ ] Build command: `./build.sh`
- [ ] Start command: `gunicorn girinka.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --timeout 120`
- [ ] All environment variables added (see `.env.render`)
- [ ] DATABASE_URL linked to database
- [ ] Service deployed successfully
- [ ] API URL copied: `https://________________.onrender.com`

### Celery Worker
- [ ] Background worker created
- [ ] Build command: `pip install -r requirements/production.txt`
- [ ] Start command: `celery -A girinka worker -l info --concurrency=2`
- [ ] Environment variables added (DATABASE_URL, Cloudinary, Resend, ML_SERVICE_URL)
- [ ] Service deployed successfully

### Celery Beat
- [ ] Background worker created
- [ ] Build command: `pip install -r requirements/production.txt`
- [ ] Start command: `celery -A girinka beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler`
- [ ] Environment variables added (DATABASE_URL, DJANGO_SETTINGS_MODULE)
- [ ] Service deployed successfully

---

## Post-Deployment Verification

### Database Seeding
- [ ] Districts seeded (30 districts)
- [ ] AI models seeded (4 models)
- [ ] Celery schedules seeded (9 tasks)

### Admin Access
- [ ] Superuser created via shell
- [ ] Admin panel accessible: `https://your-api.onrender.com/admin/`
- [ ] Can log in to admin panel

### API Testing
- [ ] Root endpoint works: `GET /api/v1/`
- [ ] Swagger docs accessible: `/api/v1/docs/`
- [ ] ReDoc accessible: `/api/v1/redoc/`
- [ ] Login endpoint works: `POST /api/v1/auth/login/`
- [ ] Districts endpoint works: `GET /api/v1/districts/`

### Celery Verification
- [ ] Periodic tasks visible in Django Admin
- [ ] Worker service logs show "ready" status
- [ ] Beat service logs show scheduler running
- [ ] Test task execution (trigger a prediction)

### ML Integration
- [ ] Health check endpoint works: `GET /api/v1/predictions/models/health_check/`
- [ ] All 4 models reported as loaded
- [ ] Test prediction works (mortality, milk, disease, or birth)

### Email System
- [ ] Password reset email sends successfully
- [ ] Alert emails configured
- [ ] FROM_EMAIL domain verified in Resend

### File Storage
- [ ] Cloudinary connection verified
- [ ] Test file upload (cow photo)
- [ ] File accessible via Cloudinary URL

---

## Security Verification

- [ ] `DEBUG=False` in production
- [ ] `SECRET_KEY` is strong and unique (50+ characters)
- [ ] `ALLOWED_HOSTS` set to `.onrender.com`
- [ ] `CORS_ALLOWED_ORIGINS` set to frontend domain only
- [ ] `SECURE_SSL_REDIRECT=True`
- [ ] Database password is strong
- [ ] No sensitive data in Git repository
- [ ] `.env` file in `.gitignore`

---

## Frontend Integration

- [ ] Frontend updated with production API URL
- [ ] CORS working (no CORS errors in browser console)
- [ ] Authentication flow working
- [ ] File uploads working
- [ ] Real-time notifications working (if applicable)

---

## Monitoring Setup

- [ ] Render logs accessible for all services
- [ ] Sentry configured (optional)
- [ ] Error alerts configured
- [ ] Uptime monitoring configured (optional)

---

## Documentation

- [ ] API URL documented for team
- [ ] Admin credentials shared securely
- [ ] Environment variables documented
- [ ] Deployment process documented
- [ ] Rollback procedure documented

---

## Performance Testing

- [ ] Load testing completed
- [ ] Response times acceptable
- [ ] Database queries optimized
- [ ] Celery tasks completing successfully
- [ ] No memory leaks detected

---

## Final Checks

- [ ] All services showing "Live" status in Render
- [ ] No errors in service logs
- [ ] Database backups configured
- [ ] SSL certificate active (https://)
- [ ] API accessible from frontend
- [ ] All scheduled tasks running on time

---

## 🎉 Deployment Complete!

**Production URLs:**
- API: `https://________________.onrender.com`
- Docs: `https://________________.onrender.com/api/v1/docs/`
- Admin: `https://________________.onrender.com/admin/`

**Next Steps:**
1. Monitor logs for first 24 hours
2. Test all critical user flows
3. Set up automated backups
4. Configure monitoring alerts
5. Document any issues and resolutions

---

**Deployed by:** _______________
**Date:** _______________
**Version:** _______________
