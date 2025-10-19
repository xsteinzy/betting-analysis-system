# Setup Guide - Running Your Betting Analysis System Locally

This guide will help you set up and run your betting analysis system on your computer. Don't worry if you're not technical - we'll walk through everything step by step!

## What You'll Need

Before we begin, you'll need to install a few programs on your computer:

### 1. Python (for the backend)
- **What it is:** Python runs the backend server that processes betting data
- **Where to get it:** Visit https://www.python.org/downloads/
- **What version:** Python 3.8 or newer
- **Installation tip:** When installing on Windows, make sure to check "Add Python to PATH"

### 2. Node.js (for the dashboard)
- **What it is:** Node.js runs the web dashboard you'll see in your browser
- **Where to get it:** Visit https://nodejs.org/
- **What version:** Node.js 18 or newer
- **Installation tip:** Download the "LTS" (Long Term Support) version

### 3. PostgreSQL Database (for storing data)
- **What it is:** PostgreSQL is where all your betting data is stored
- **Where to get it:** Visit https://www.postgresql.org/download/
- **What version:** PostgreSQL 14 or newer
- **Installation tip:** Remember the password you set during installation - you'll need it!

### 4. Git (optional, for version control)
- **What it is:** Git helps you manage code versions
- **Where to get it:** Visit https://git-scm.com/downloads/

## Setup Instructions

### Step 1: Set Up the Database

1. **Open PostgreSQL**
   - On Windows: Search for "pgAdmin" or "SQL Shell (psql)" in the Start menu
   - On Mac: Open Terminal and type `psql postgres`
   - On Linux: Open Terminal and type `sudo -u postgres psql`

2. **Create the database**
   ```sql
   CREATE DATABASE betting_analysis;
   ```

3. **Load the database schema**
   - Open the file `betting_backend/database/schema.sql`
   - Copy all the text
   - Paste it into your PostgreSQL tool and run it
   - This creates all the tables your system needs

4. **Remember your database details**
   You'll need these later:
   - **Database name:** betting_analysis
   - **Username:** postgres (or whatever you set up)
   - **Password:** The password you created during installation
   - **Host:** localhost
   - **Port:** 5432 (default)

### Step 2: Configure the Backend

1. **Open your file explorer**
   - Navigate to the `betting_backend/api/` folder

2. **Create your environment file**
   - Find the file named `.env.example`
   - Make a copy of it and rename the copy to `.env` (remove the .example part)
   - Open the `.env` file in a text editor (Notepad is fine)

3. **Fill in your database details**
   Replace the placeholder values with your actual database information:
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=betting_analysis
   DB_USER=postgres
   DB_PASSWORD=your_actual_password_here
   
   FLASK_ENV=development
   PORT=5000
   CORS_ORIGINS=http://localhost:3000
   ```

4. **Save the file**

### Step 3: Configure the Dashboard

1. **Open your file explorer**
   - Navigate to the `betting_dashboard/` folder

2. **Create your environment file**
   - Find the file named `.env.local.example`
   - Make a copy of it and rename the copy to `.env.local`
   - Open the `.env.local` file in a text editor

3. **Check the settings**
   It should look like this:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:5000
   ```
   This tells the dashboard where to find the backend.

4. **Save the file**

### Step 4: Start the Backend Server

#### On Windows:
1. Open File Explorer and go to the `betting_backend` folder
2. Double-click on `start_backend.bat`
3. A black window will open showing the server starting
4. Wait until you see "Starting Flask API Server"
5. **Keep this window open!** If you close it, the backend stops.

#### On Mac/Linux:
1. Open Terminal
2. Navigate to the betting_backend folder:
   ```bash
   cd /path/to/betting_backend
   ```
3. Run the startup script:
   ```bash
   ./start_backend.sh
   ```
4. Wait until you see "Starting Flask API Server"
5. **Keep this terminal window open!**

### Step 5: Start the Dashboard

#### On Windows:
1. Open a NEW File Explorer window (keep the backend running!)
2. Go to the `betting_dashboard` folder
3. Double-click on `start_dashboard.bat`
4. A black window will open showing the dashboard starting
5. Wait a minute or two - it takes time to start the first time
6. Your web browser should automatically open to http://localhost:3000

#### On Mac/Linux:
1. Open a NEW Terminal window (keep the backend running!)
2. Navigate to the betting_dashboard folder:
   ```bash
   cd /path/to/betting_dashboard
   ```
3. Run the startup script:
   ```bash
   ./start_dashboard.sh
   ```
4. Wait a minute or two
5. Open your web browser and go to http://localhost:3000

### Step 6: Verify Everything Works

1. **Check the backend:**
   - Open your web browser
   - Go to http://localhost:5000/api/health
   - You should see a message saying the system is healthy

2. **Check the dashboard:**
   - Go to http://localhost:3000
   - You should see your betting analysis dashboard
   - Try clicking on different pages in the sidebar

## What to Do Next

### Running Predictions
Before you can see real data in your dashboard, you need to:

1. Collect game and player data (see the quickstart guides in betting_backend/)
2. Run the ML models to generate predictions
3. The predictions will then appear in your dashboard

### Stopping the System
When you're done:
1. Close your web browser
2. In each command window/terminal, press **CTRL+C** to stop the servers
3. Wait for them to shut down gracefully

### Starting Again Later
Simply repeat Steps 4 and 5:
1. Start the backend first
2. Then start the dashboard
3. Your data is saved in the database, so you won't lose anything!

## Need Help?

If something isn't working, check the TROUBLESHOOTING.md file for common issues and solutions.
