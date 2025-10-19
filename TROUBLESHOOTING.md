
# Troubleshooting Guide

This guide covers common issues and their solutions. If you're having problems, check here first!

## Table of Contents

- [Local Development Issues](#local-development-issues)
- [Database Issues](#database-issues)
- [Backend API Issues](#backend-api-issues)
- [Dashboard Issues](#dashboard-issues)
- [Deployment Issues](#deployment-issues)
- [Data and Prediction Issues](#data-and-prediction-issues)

---

## Local Development Issues

### "Command not found" or "Not recognized as a command"

**Problem:** When trying to run Python, Node, or other commands, you get an error saying the command isn't recognized.

**Solution:**
1. Make sure you installed Python/Node.js
2. Restart your terminal/command prompt
3. On Windows, make sure "Add to PATH" was checked during installation
4. Try using `python3` instead of `python` (or vice versa)
5. Try using `npm` with full path: `C:\Program Files\nodejs\npm`

### Scripts won't run on Mac/Linux

**Problem:** `./start_backend.sh` says "Permission denied"

**Solution:**
```bash
chmod +x start_backend.sh
chmod +x start_dashboard.sh
```

### Port already in use

**Problem:** "Port 5000 is already in use" or "Port 3000 is already in use"

**Solution:**
1. Check if you already have the server running in another window
2. Close any other programs using that port
3. On Mac/Linux:
   ```bash
   # Kill process on port 5000
   lsof -ti:5000 | xargs kill -9
   # Kill process on port 3000
   lsof -ti:3000 | xargs kill -9
   ```
4. On Windows:
   ```cmd
   # Find and kill process on port 5000
   netstat -ano | findstr :5000
   taskkill /PID [PID_NUMBER] /F
   ```

---

## Database Issues

### Can't connect to database

**Problem:** "Connection refused" or "Could not connect to database"

**Solution:**
1. Make sure PostgreSQL is running:
   - **Windows:** Check Services, start PostgreSQL
   - **Mac:** `brew services start postgresql`
   - **Linux:** `sudo systemctl start postgresql`

2. Check your `.env` file in `betting_backend/api/`:
   - Is the password correct?
   - Is the database name correct?
   - Is the host correct? (should be `localhost` for local)

3. Verify the database exists:
   ```sql
   # In PostgreSQL
   \l  # List all databases
   # Should see 'betting_analysis' in the list
   ```

### "database does not exist"

**Problem:** Error saying the database doesn't exist

**Solution:**
1. Open PostgreSQL (pgAdmin or psql)
2. Create the database:
   ```sql
   CREATE DATABASE betting_analysis;
   ```
3. Load the schema:
   - Open `betting_backend/database/schema.sql`
   - Copy and paste into PostgreSQL
   - Run it

### "relation does not exist" or "table does not exist"

**Problem:** Tables aren't created in the database

**Solution:**
1. Make sure you ran the schema.sql file
2. Check you're connected to the right database
3. Re-run the schema:
   ```bash
   cd betting_backend/database
   psql -U postgres -d betting_analysis -f schema.sql
   ```

### "password authentication failed"

**Problem:** Wrong database password

**Solution:**
1. Check your `.env` file has the correct password
2. Try resetting the PostgreSQL password:
   ```sql
   ALTER USER postgres PASSWORD 'new_password';
   ```
3. Update the password in `.env` file

---

## Backend API Issues

### Backend won't start

**Problem:** Backend crashes immediately or shows errors

**Solution:**
1. Check if you have all dependencies:
   ```bash
   cd betting_backend
   pip install -r api/requirements.txt
   ```

2. Check for Python errors in the output
3. Verify your `.env` file exists in `api/` folder
4. Test the database connection:
   ```bash
   cd api
   python connection.py
   ```

### "ModuleNotFoundError"

**Problem:** Python can't find required modules

**Solution:**
1. Make sure you installed requirements:
   ```bash
   pip install -r api/requirements.txt
   ```
2. If using virtual environment, make sure it's activated:
   ```bash
   source venv/bin/activate  # Mac/Linux
   venv\Scripts\activate     # Windows
   ```

### API returns 500 errors

**Problem:** API is running but returns error 500 on requests

**Solution:**
1. Check the terminal/console for error messages
2. Verify database connection is working
3. Check that tables exist in database
4. Look for Python errors in the backend logs

### CORS errors in browser

**Problem:** Browser console shows CORS errors

**Solution:**
1. Check `CORS_ORIGINS` in backend `.env` file
2. Make sure it includes your dashboard URL:
   ```
   CORS_ORIGINS=http://localhost:3000
   ```
3. Restart the backend after changing `.env`

---

## Dashboard Issues

### Dashboard shows blank page

**Problem:** Dashboard loads but nothing shows up

**Solution:**
1. Check browser console (Press F12) for errors
2. Verify backend is running (go to http://localhost:5000/api/health)
3. Check `.env.local` has correct API URL:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:5000
   ```
4. Restart the dashboard

### "Failed to fetch" or "Network error"

**Problem:** Dashboard can't connect to backend

**Solution:**
1. Verify backend is running:
   - Visit http://localhost:5000/api/health
   - Should see a health check message

2. Check `.env.local` in dashboard folder:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:5000
   ```

3. Check for CORS errors in browser console (F12)

4. Make sure firewall isn't blocking connections

### Dashboard won't start

**Problem:** Dashboard crashes or won't start

**Solution:**
1. Delete `node_modules` and reinstall:
   ```bash
   cd betting_dashboard
   rm -rf node_modules
   npm install
   ```

2. Clear Next.js cache:
   ```bash
   rm -rf .next
   npm run dev
   ```

3. Check for Node.js errors in the output

### "npm not found" or "node not found"

**Problem:** Can't run npm commands

**Solution:**
1. Install Node.js from https://nodejs.org
2. Restart your terminal
3. Verify installation:
   ```bash
   node --version
   npm --version
   ```

---

## Deployment Issues (Render.com)

### Service fails to deploy

**Problem:** Render shows "Deploy failed"

**Solution:**
1. Click on "Logs" in Render to see the error
2. Common issues:
   - Wrong build command
   - Wrong start command
   - Missing environment variables
   - Wrong root directory

3. Verify your settings match DEPLOYMENT.md

### Database connection fails on Render

**Problem:** API can't connect to database

**Solution:**
1. Check environment variables:
   - `DATABASE_URL` should be set
   - Copy from your database's "Internal Database URL"

2. Make sure you're using the **Internal** URL, not external

3. Verify the database is running (check Render dashboard)

### 503 Service Unavailable

**Problem:** Site shows 503 error

**Solution:**
1. Free tier services "sleep" after 15 minutes
2. First request wakes them up (takes 30-60 seconds)
3. Refresh the page after waiting
4. If problem persists, check Render logs

### Environment variables not working

**Problem:** Settings in Render don't seem to apply

**Solution:**
1. After changing environment variables, service must redeploy
2. Render should auto-redeploy, but you can trigger manually:
   - Go to service settings
   - Click "Manual Deploy" → "Deploy latest commit"

### CORS errors after deployment

**Problem:** Dashboard can't connect to API

**Solution:**
1. Update API's `CORS_ORIGINS` environment variable:
   ```
   CORS_ORIGINS=https://your-dashboard-url.onrender.com
   ```

2. Update dashboard's `NEXT_PUBLIC_API_URL`:
   ```
   NEXT_PUBLIC_API_URL=https://your-api-url.onrender.com
   ```

3. Make sure both services redeploy after changes

---

## Data and Prediction Issues

### No predictions showing

**Problem:** Predictions page is empty

**Solution:**
1. You need to run the ML models first to generate predictions
2. Check the backend quickstart guides:
   - `NBA_QUICKSTART.md`
   - `ML_QUICKSTART.md`

3. Run the prediction generation scripts:
   ```bash
   cd betting_backend
   python scripts/generate_predictions.py
   ```

4. Verify data exists in database:
   ```sql
   SELECT COUNT(*) FROM projections;
   ```

### No games showing

**Problem:** Can't see any games

**Solution:**
1. Need to collect game data first:
   ```bash
   cd betting_backend
   python collect_data.py
   ```

2. Check if games exist in database:
   ```sql
   SELECT COUNT(*) FROM games;
   ```

### Predictions seem wrong or outdated

**Problem:** Predictions don't look right

**Solution:**
1. Predictions are based on historical data
2. Update your data regularly:
   ```bash
   python collect_data.py
   ```

3. Retrain models with new data periodically

4. Check for player injuries or trades (manual verification)

---

## General Troubleshooting Tips

### Check Logs

**Local:**
- Terminal/command prompt shows errors in real-time
- Read the error messages carefully

**Render:**
- Click on service → Logs tab
- Shows detailed deployment and runtime logs

### Restart Everything

When in doubt:
1. Stop all running services
2. Restart database
3. Restart backend
4. Restart dashboard
5. Clear browser cache (Ctrl+Shift+Delete)
6. Try again

### Verify File Locations

Make sure files are in the right place:
```
betting_backend/
  api/
    .env          ← Environment file
    server.py     ← Main API file
    connection.py ← Database connection
  database/
    schema.sql    ← Database schema

betting_dashboard/
  .env.local      ← Environment file
  lib/
    api-client.js ← API client
```

### Browser Developer Tools

Press **F12** in your browser to:
- See JavaScript errors (Console tab)
- Inspect network requests (Network tab)
- View data being sent/received

### Still Stuck?

1. Check if the issue is in GitHub repository issues
2. Review all documentation files
3. Search for the error message online
4. Check Render.com documentation if deployed
5. Verify you followed all setup steps

---

## Error Messages Reference

### Common Error Messages and Solutions

| Error | Likely Cause | Solution |
|-------|-------------|----------|
| "ECONNREFUSED" | Backend not running | Start the backend |
| "CORS policy" | CORS not configured | Update CORS_ORIGINS |
| "relation does not exist" | Database tables missing | Run schema.sql |
| "password authentication failed" | Wrong DB password | Fix .env file |
| "MODULE_NOT_FOUND" | Missing dependencies | Run npm install or pip install |
| "Port already in use" | Port occupied | Kill process or use different port |
| "Cannot find module" | Missing import | Check file paths |
| "502 Bad Gateway" | Backend crashed | Check Render logs |

---

## Prevention Tips

### To avoid issues:

1. ✅ Always check .env files are correct
2. ✅ Keep dependencies updated
3. ✅ Test locally before deploying
4. ✅ Commit code regularly
5. ✅ Read error messages carefully
6. ✅ Keep database backed up
7. ✅ Document any custom changes

### Best Practices:

1. **Before starting work:**
   - Pull latest code from Git
   - Check all services are running
   - Verify database connection

2. **During development:**
   - Test changes frequently
   - Check browser console for errors
   - Read backend logs

3. **Before deploying:**
   - Test everything locally
   - Commit and push code
   - Verify environment variables

---

## Still Need Help?

If you've tried everything and still have issues:

1. **Collect Information:**
   - What were you trying to do?
   - What error message did you see?
   - What have you already tried?
   - Screenshots of errors

2. **Check Documentation:**
   - SETUP.md for local setup
   - DEPLOYMENT.md for Render issues
   - USER_GUIDE.md for usage questions

3. **Community Resources:**
   - Render Community: https://community.render.com
   - Stack Overflow
   - GitHub Issues (if using a repository)

Remember: Most issues are simple fixes - stay calm and work through the steps systematically! 🔧
