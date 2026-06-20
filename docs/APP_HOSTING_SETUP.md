# App Hosting Setup Guide

This guide covers various hosting options for your Odysseus/Devante Codex application.

## Quick Start Options

### Option 1: Firebase Hosting (Recommended for Firebase Integration)
### Option 2: Vercel (Simple deployment)
### Option 3: Railway (Backend deployment)
### Option 4: Self-hosted (Docker/Traditional)
### Option 5: Cloud Run (Google Cloud)

---

## Option 1: Firebase Hosting (Recommended)

Since you're moving to Firebase, Firebase Hosting is the natural choice.

### Prerequisites
- Firebase project created
- Node.js installed
- Firebase CLI installed

### Setup Steps

1. **Install Firebase CLI:**
```bash
npm install -g firebase-tools
firebase login
```

2. **Initialize Firebase in your project:**
```bash
firebase init
```
Choose:
- Hosting
- Use existing project (your Firebase project)
- Public directory: `static`
- Configure as single-page app: Yes
- Set up automatic builds with GitHub: Yes (optional)

3. **Create firebase.json configuration:**
```json
{
  "hosting": {
    "public": "static",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      },
      {
        "source": "/api/**",
        "function": "api"
      }
    ]
  },
  "functions": {
    "source": ".",
    "runtime": "python3.10"
  }
}
```

4. **Deploy frontend:**
```bash
firebase deploy --only hosting
```

5. **Deploy backend as Firebase Functions:**
```bash
firebase deploy --only functions
```

### Benefits
- Integrated with Firebase services
- Global CDN
- SSL certificates included
- Easy rollback
- Preview channels

---

## Option 2: Vercel Deployment

### Prerequisites
- Vercel account
- GitHub repository
- Node.js installed

### Setup Steps

1. **Create `vercel.json`:**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "app.py"
    }
  ],
  "env": {
    "DATABASE_URL": "@database_url"
  }
}
```

2. **Install Vercel CLI:**
```bash
npm install -g vercel
vercel login
```

3. **Deploy:**
```bash
vercel
```

### Configuration
- Set environment variables in Vercel dashboard
- Configure domain settings
- Set up preview deployments

---

## Option 3: Railway Deployment

### Prerequisites
- Railway account
- GitHub repository

### Setup Steps

1. **Create `railway.json`:**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "healthcheckPath": "/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

2. **Create `railway.env.example`:**
```bash
DATABASE_URL=postgresql://user:password@host:port/database
OPENAI_API_KEY=your-api-key
```

3. **Install Railway CLI:**
```bash
npm install -g @railway/cli
railway login
```

4. **Initialize and deploy:**
```bash
railway init
railway up
```

### Configuration
- Set environment variables in Railway dashboard
- Configure auto-deploy from GitHub
- Set up custom domains

---

## Option 4: Docker Deployment

### Prerequisites
- Docker installed
- Docker Compose installed (for multi-container setup)

### Setup Steps

1. **Build Docker image:**
```bash
docker build -t odysseus-app .
```

2. **Run container:**
```bash
docker run -p 7000:7000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  odysseus-app
```

3. **Use Docker Compose (recommended):**
```yaml
version: '3.8'
services:
  odysseus:
    build: .
    ports:
      - "7000:7000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - DATABASE_URL=sqlite:///./data/app.db
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: unless-stopped
```

4. **Deploy to cloud:**
- **Docker Hub:** Push and pull from Docker Hub
- **AWS ECS:** Use Amazon Elastic Container Service
- **Google Cloud Run:** Deploy container to Cloud Run
- **Azure Container Instances:** Use Azure Container Instances

---

## Option 5: Google Cloud Run

### Prerequisites
- Google Cloud account
- Google Cloud SDK installed
- gcloud CLI configured

### Setup Steps

1. **Build and push container:**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/odysseus-app
```

2. **Deploy to Cloud Run:**
```bash
gcloud run deploy odysseus-app \
  --image gcr.io/PROJECT_ID/odysseus-app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=sqlite:///./data/app.db
```

3. **Set environment variables:**
```bash
gcloud run services update odysseus-app \
  --set-env-vars OPENAI_API_KEY=your-key
```

### Benefits
- Auto-scaling
- Pay-per-use
- Global availability
- SSL included

---

## Option 6: Traditional VPS/Cloud Server

### Providers
- DigitalOcean
- Linode (Akamai)
- AWS EC2
- Google Compute Engine
- Azure Virtual Machines

### Setup Steps

1. **Provision server** (Ubuntu/Debian recommended)

2. **Install dependencies:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3 python3-pip python3-venv -y

# Install Nginx
sudo apt install nginx -y

# Install SSL certbot
sudo apt install certbot python3-certbot-nginx -y
```

3. **Setup application:**
```bash
# Create user
sudo useradd -m -s /bin/bash odysseus

# Clone repository
sudo -u odysseus git clone <your-repo> /opt/odysseus
cd /opt/odysseus

# Create virtual environment
sudo -u odysseus python3 -m venv venv
sudo -u odysseus venv/bin/pip install -r requirements.txt

# Setup systemd service
sudo nano /etc/systemd/system/odysseus.service
```

4. **Create systemd service:**
```ini
[Unit]
Description=Odysseus Application
After=network.target

[Service]
User=odysseus
Group=odysseus
WorkingDirectory=/opt/odysseus
Environment="PATH=/opt/odysseus/venv/bin"
ExecStart=/opt/odysseus/venv/bin/uvicorn app:app --host 0.0.0.0 --port 7000
Restart=always

[Install]
WantedBy=multi-user.target
```

5. **Configure Nginx reverse proxy:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:7000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /opt/odysseus/static/;
    }
}
```

6. **Setup SSL:**
```bash
sudo certbot --nginx -d your-domain.com
```

---

## Environment Variables Configuration

### Essential Variables
```bash
# Database
DATABASE_URL=sqlite:///./data/app.db

# AI Model Configuration
OPENAI_API_KEY=your-api-key
LLM_HOST=https://api.openai.com

# Authentication
AUTH_ENABLED=true
JWT_SECRET=your-jwt-secret

# CORS
ALLOWED_ORIGINS=https://your-domain.com,https://another-domain.com
```

### Platform-Specific Setup

#### Firebase Hosting
Set in Firebase Console or firebase.json

#### Vercel
Set in Vercel Dashboard → Settings → Environment Variables

#### Railway
Set in Railway Dashboard → Variables

#### Docker Compose
Set in docker-compose.yml under environment:

```yaml
environment:
  - DATABASE_URL=sqlite:///./data/app.db
  - OPENAI_API_KEY=${OPENAI_API_KEY}
```

#### Cloud Run
Set with `--set-env-vars` flag or in Cloud Console

---

## Performance Optimization

### 1. Enable GZIP Compression
```python
# In app.py
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware)
```

### 2. Configure Caching Headers
```python
# For static files
@app.mount("/static", StaticFiles(directory="static"), name="static")
```

### 3. Use CDN for Static Assets
- Upload static files to CDN
- Update static URLs to point to CDN

### 4. Database Optimization
- Use connection pooling
- Enable query caching
- Add database indexes

### 5. Load Balancing
- Use load balancer for multiple instances
- Configure health checks
- Set up auto-scaling

---

## Security Best Practices

### 1. Environment Variables
- Never commit secrets to git
- Use platform-specific secret management
- Rotate keys regularly

### 2. HTTPS/SSL
- Always use HTTPS in production
- Configure proper SSL certificates
- Update certificates automatically

### 3. Authentication
- Enable authentication in production
- Use strong JWT secrets
- Implement rate limiting

### 4. Firewall
- Configure proper firewall rules
- Only expose necessary ports
- Use VPN for admin access

### 5. Regular Updates
- Keep dependencies updated
- Monitor for security vulnerabilities
- Apply security patches promptly

---

## Monitoring and Logging

### 1. Application Monitoring
- Use platform monitoring tools
- Set up error tracking (Sentry, Rollbar)
- Monitor performance metrics

### 2. Logging
- Centralize logs (ELK stack, Cloud Logging)
- Set up log aggregation
- Configure log retention policies

### 3. Health Checks
- Implement health check endpoints
- Configure uptime monitoring
- Set up alerting

---

## Backup and Disaster Recovery

### 1. Database Backups
- Regular automated backups
- Offsite backup storage
- Test restore procedures

### 2. Application Backups
- Version control for code
- Configuration backups
- Static asset backups

### 3. Disaster Recovery Plan
- Document recovery procedures
- Test recovery process
- Maintain contact information

---

## Deployment Checklist

Before deploying to production:

- [ ] Update all environment variables
- [ ] Set up authentication
- [ ] Configure HTTPS/SSL
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Test health check endpoints
- [ ] Configure error tracking
- [ ] Set up alerting
- [ ] Performance testing
- [ ] Security audit
- [ ] Document deployment process
- [ ] Create rollback plan

---

## Cost Comparison

| Platform | Free Tier | Cost (Small App) | Best For |
|----------|-----------|------------------|----------|
| Firebase Hosting | Yes | $0-25/month | Static + Firebase integration |
| Vercel | Yes | $0-20/month | Fast deployment, preview environments |
| Railway | $5 free credits | $5-20/month | Backend services, databases |
| Cloud Run | Free tier available | Pay-per-use | Auto-scaling, container-based |
| DigitalOcean | No | $5-10/month | Full control, predictable pricing |
| AWS EC2 | 12 months free | Variable | Enterprise, existing AWS users |

---

## Support and Troubleshooting

### Common Issues

**1. Port Already in Use:**
```bash
# Find process using port 7000
lsof -i :7000
# Kill process
kill -9 <PID>
```

**2. Database Connection Errors:**
- Check DATABASE_URL is correct
- Ensure database is accessible
- Verify network connectivity

**3. File Permission Errors:**
- Check file permissions on data directory
- Ensure proper user/group ownership
- Fix with: `chmod -R 755 data/`

**4. Memory Issues:**
- Increase memory limits
- Optimize application code
- Add swap space

### Getting Help
- Check platform documentation
- Review application logs
- Test locally first
- Use platform support channels

---

## Recommended Setup

**For Firebase Integration:**
1. **Firebase Hosting** (frontend)
2. **Firebase Functions** (backend)
3. **Firebase Firestore** (database)
4. **Firebase Storage** (files)

**For Complete Solution:**
1. **Vercel** (frontend hosting)
2. **Railway** (backend + database)
3. **Firebase Storage** (files)
4. **Cloudflare** (DNS + security)

**For Cost-Effective Solution:**
1. **DigitalOcean** (all-in-one)
2. **PostgreSQL** (database)
3. **Nginx** (reverse proxy)
4. **Certbot** (SSL)

Choose the option that best fits your requirements, budget, and technical expertise.