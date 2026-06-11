# GitHub Actions CI/CD Setup for Render Deployment

This guide explains the GitHub Actions workflows configured for this project and how to set up deployment to Render.

## Workflows Overview

### 1. `deploy-render.yml` - Production Deployment
**Triggers:** Push to `main` branch or manual workflow dispatch

**What it does:**
- Builds Docker image with multi-stage caching
- Pushes image to GitHub Container Registry (ghcr.io)
- Triggers Render deployment via webhook
- Tags images with commit SHA and semantic versioning

**Required Secrets:**
- `RENDER_DEPLOY_HOOK` - Your Render deployment webhook URL

### 2. `build-test.yml` - CI Pipeline
**Triggers:** Pull requests to `main`/`develop` or push to `develop`

**What it does:**
- Builds Docker image (validation only, no push)
- Tests Python backend dependencies
- Tests Node.js frontend build
- Lints Python code (non-blocking)
- Caches dependencies for faster builds

**No secrets required** - runs automatically on PRs

---

## Setup Instructions

### Step 1: Get Your Render Deploy Hook

1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Select your Web Service
3. Go to **Settings** → **Deploy Hook**
4. Copy the webhook URL (format: `https://api.render.com/deploy/...`)

### Step 2: Add GitHub Secret

1. Go to your GitHub repository
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `RENDER_DEPLOY_HOOK`
5. Value: Paste your Render webhook URL
6. Click **Add secret**

### Step 3: Push to Trigger Deployment

```bash
git push origin main
```

The workflow will:
1. Build your Docker image
2. Push to ghcr.io
3. Call Render's deploy hook
4. Render will pull and deploy the latest image

---

## Workflow Files Location

```
.github/
└── workflows/
    ├── deploy-render.yml      # Production deployment
    └── build-test.yml         # CI pipeline (PR validation)
```

---

## Manual Workflow Dispatch

You can manually trigger the deployment workflow:

1. Go to **Actions** tab in GitHub
2. Select **Deploy to Render**
3. Click **Run workflow** → **Run workflow**

---

## Environment Variables

### For Render Deployment

Create a `render.yaml` file in your project root (optional, for advanced config):

```yaml
services:
  - type: web
    name: cloudmerg-chatbot
    env: docker
    dockerfilePath: ./Dockerfile
    dockerContext: ./
    port: 8000
    envVars:
      - key: MISTRAL_API_KEY
        sync: false
      - key: LOG_LEVEL
        value: INFO
```

Or configure directly in Render Dashboard:
1. **Settings** → **Environment** 
2. Add your environment variables (API keys, etc.)

---

## Caching Strategy

- **Docker layer caching:** GitHub Actions caches Docker layers between builds
- **Python pip cache:** Dependencies cached based on `requirements.txt`
- **Node.js npm cache:** Dependencies cached based on `package-lock.json`

---

## Troubleshooting

### Deployment not triggering
- Check that `RENDER_DEPLOY_HOOK` secret is set correctly
- Verify you're pushing to the `main` branch
- Check **Actions** tab for workflow run logs

### Image build fails
- Review logs in **Actions** tab
- Check `Dockerfile` for errors
- Ensure all dependencies are in `requirements.txt` and `package.json`

### Render deployment fails
- Verify the deploy hook URL is correct
- Check Render logs in Render Dashboard
- Ensure your Dockerfile exposes port 8000

---

## Customization

### Change deployment trigger branch
Edit `deploy-render.yml`:
```yaml
on:
  push:
    branches:
      - main        # Change this
```

### Add more environments (staging/production)
Create additional workflow files:
- `.github/workflows/deploy-staging.yml` (triggers on `develop`)
- `.github/workflows/deploy-production.yml` (triggers on `main`)

### Add PR comment on deployment
Add this step to `deploy-render.yml`:
```yaml
- name: Comment on PR
  uses: actions/github-script@v7
  with:
    script: |
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: '✅ Deployment initiated to Render'
      })
```

---

## Next Steps

1. ✅ Workflows are ready
2. 📝 Add `RENDER_DEPLOY_HOOK` secret
3. 🚀 Push to `main` to deploy
4. 📊 Monitor in GitHub Actions & Render Dashboard
