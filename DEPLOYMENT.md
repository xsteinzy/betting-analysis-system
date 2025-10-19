# Deployment Guide - Publishing Your System Online with Render.com

This guide will help you deploy your betting analysis system to the internet using Render.com, so you can access it from anywhere! Render.com offers a free tier that's perfect for personal projects.

## Why Render.com?

- ✅ **Free tier available** - No credit card required to start
- ✅ **Automatic deployment** - Updates automatically when you push code
- ✅ **Built-in database** - PostgreSQL included
- ✅ **Easy to use** - Much simpler than AWS or other platforms
- ✅ **HTTPS included** - Secure connections built-in

## Prerequisites

Before you begin, you need:

1. **A GitHub account** (free) - Sign up at https://github.com
2. **Your code in a GitHub repository** - We'll help you set this up below
3. **A Render.com account** (free) - Sign up at https://render.com

## Step 1: Push Your Code to GitHub

### If you already have Git installed:

1. **Open Terminal/Command Prompt**
   - Navigate to your project folder (the parent folder containing both betting_backend and betting_dashboard)

2. **Initialize Git** (if not already done)
   ```bash
   git init
   git add .
   git commit -m "Initial commit - betting analysis system"
   ```

3. **Create a GitHub repository**
   - Go to https://github.com and click the "+" icon → "New repository"
   - Name it something like "betting-analysis-system"
   - Don't initialize with README (you already have code)
   - Click "Create repository"

4. **Push your code**
   GitHub will show you commands to run. They'll look like:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/betting-analysis-system.git
   git branch -M main
   git push -u origin main
   ```
   Replace YOUR_USERNAME with your actual GitHub username.

### If you're not comfortable with Git:

1. Go to https://github.com and create a new repository
2. Use GitHub Desktop (download from https://desktop.github.com/)
3. Drag your project folder into GitHub Desktop
4. Click "Publish repository"

## Step 2: Sign Up for Render.com

1. **Go to Render.com**
   - Visit https://render.com
   - Click "Get Started"

2. **Sign up with GitHub**
   - Click "Sign up with GitHub"
   - This automatically connects your GitHub account
   - Authorize Render to access your repositories

3. **You're done!** No credit card needed for the free tier.

## Step 3: Deploy the Database

1. **Create a new PostgreSQL database**
   - In Render dashboard, click "New +"
   - Select "PostgreSQL"

2. **Configure the database**
   - **Name:** betting-db (or any name you like)
   - **Database:** betting_analysis
   - **User:** betting_user (or any username)
   - **Region:** Choose the closest to you
   - **Plan:** Free

3. **Create the database**
   - Click "Create Database"
   - Wait for it to deploy (takes 1-2 minutes)
   - **Important:** Copy the "Internal Database URL" - you'll need this!

4. **Load the schema**
   - Click on your database in the Render dashboard
   - Click "Connect" → "External Connection"
   - You'll see connection commands
   - Use a PostgreSQL client to connect and run the `schema.sql` file
   - OR: Use Render's web shell to paste and run the schema

## Step 4: Deploy the Backend API

1. **Create a new Web Service**
   - In Render dashboard, click "New +"
   - Select "Web Service"
   - Click "Connect" next to your GitHub repository

2. **Configure the service**
   Fill in these settings:
   
   - **Name:** betting-api (or any name you like)
   - **Region:** Same as your database
   - **Branch:** main
   - **Root Directory:** betting_backend
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r api/requirements.txt`
   - **Start Command:** `cd api && gunicorn server:app`
   - **Plan:** Free

3. **Add environment variables**
   Click "Advanced" → "Add Environment Variable" and add these:
   
   | Key | Value |
   |-----|-------|
   | FLASK_ENV | production |
   | PORT | 5000 |
   | DATABASE_URL | (Paste the Internal Database URL from Step 3) |
   | CORS_ORIGINS | https://YOUR-DASHBOARD-NAME.onrender.com |
   
   **Note:** For CORS_ORIGINS, you'll need to come back and update this after you deploy the dashboard (Step 5).

4. **Create the service**
   - Click "Create Web Service"
   - Wait 3-5 minutes for deployment
   - Once it says "Live", copy the URL (something like https://betting-api.onrender.com)

5. **Test the API**
   - Visit https://YOUR-API-URL.onrender.com/api/health
   - You should see a health check response
   - If you see an error, check the logs in Render

## Step 5: Deploy the Dashboard

1. **Create another Web Service**
   - Click "New +"
   - Select "Web Service"
   - Connect your GitHub repository again

2. **Configure the service**
   Fill in these settings:
   
   - **Name:** betting-dashboard (or any name you like)
   - **Region:** Same as your database and API
   - **Branch:** main
   - **Root Directory:** betting_dashboard
   - **Runtime:** Node
   - **Build Command:** `npm install && npm run build`
   - **Start Command:** `npm start`
   - **Plan:** Free

3. **Add environment variables**
   Click "Advanced" → "Add Environment Variable":
   
   | Key | Value |
   |-----|-------|
   | NEXT_PUBLIC_API_URL | https://YOUR-API-URL.onrender.com |
   | NODE_ENV | production |
   
   Replace YOUR-API-URL with the actual URL from Step 4.

4. **Create the service**
   - Click "Create Web Service"
   - Wait 5-10 minutes (Next.js takes longer to build)
   - Once it says "Live", copy the URL

## Step 6: Update CORS Settings

Now that you have your dashboard URL, go back and update the API:

1. **Go to your betting-api service in Render**
2. **Click "Environment"**
3. **Find CORS_ORIGINS variable**
4. **Update it to:** https://YOUR-DASHBOARD-URL.onrender.com
5. **Click "Save Changes"**
6. The API will automatically redeploy (takes 2-3 minutes)

## Step 7: Verify Everything Works

1. **Visit your dashboard URL**
   - Open https://YOUR-DASHBOARD-URL.onrender.com
   - You should see your betting analysis dashboard

2. **Check the connection**
   - Click around the different pages
   - If you see data loading errors, check the browser console (F12)
   - Make sure the API URL in environment variables is correct

3. **Test the API directly**
   - Visit https://YOUR-API-URL.onrender.com/api/health
   - Should return a healthy status

## Important Notes

### Free Tier Limitations

- **Spin down:** Free services "sleep" after 15 minutes of inactivity
- **Spin up time:** Takes 30-60 seconds to wake up when you visit
- **Solution:** Upgrade to paid plan ($7/month per service) for always-on

### Database Limitations

- **Free tier:** 90 days, then you need to upgrade
- **Storage:** 1GB limit on free tier
- **Upgrade:** Only $7/month for PostgreSQL Starter (unlimited time, 10GB storage)

### Automatic Deployments

Every time you push code to GitHub:
- Render automatically detects the changes
- Rebuilds and redeploys your services
- Takes 3-10 minutes depending on the service

### Cost Summary

- **Free:** Database (90 days) + API + Dashboard = $0
- **After 90 days:** $7/month for database
- **Always-on (optional):** $7/month per service (API + Dashboard = $14/month)
- **Recommended:** $21/month total (database + always-on API + always-on dashboard)

## Updating Your Deployed System

To update your system after making changes:

1. **Make your changes locally**
2. **Commit and push to GitHub:**
   ```bash
   git add .
   git commit -m "Description of changes"
   git push
   ```
3. **Render automatically deploys!**
4. Wait 3-10 minutes for the deployment to complete

## Monitoring Your System

### View Logs

1. Go to your service in Render
2. Click "Logs" tab
3. See real-time logs of your application

### Check Status

1. Dashboard shows service status (Live/Failed/Deploying)
2. Set up email alerts for failures (in service settings)

### View Metrics

1. Click on a service
2. See CPU, memory, and bandwidth usage
3. Free tier includes basic metrics

## Need Help?

- **Render Docs:** https://render.com/docs
- **Community:** https://community.render.com
- **Support:** support@render.com (paid plans get priority)

## Troubleshooting

See TROUBLESHOOTING.md for common deployment issues and solutions.

## Security Reminder

- ✅ Never commit `.env` files to GitHub
- ✅ Use environment variables in Render for secrets
- ✅ The `.env.example` files are safe to commit (no real passwords)
- ✅ Render automatically provides HTTPS for security
