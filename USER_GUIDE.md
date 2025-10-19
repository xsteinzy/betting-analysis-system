
# User Guide - Using Your Betting Analysis System

Welcome! This guide will show you how to use your betting analysis system once it's up and running. Whether you're running it locally or deployed online, the interface works the same way.

## Table of Contents

1. [Accessing the System](#accessing-the-system)
2. [Dashboard Overview](#dashboard-overview)
3. [Viewing Predictions](#viewing-predictions)
4. [Finding Value Bets](#finding-value-bets)
5. [Tracking Your Bets](#tracking-your-bets)
6. [Analyzing Performance](#analyzing-performance)
7. [Managing Bankroll](#managing-bankroll)
8. [Understanding the Data](#understanding-the-data)

---

## Accessing the System

### Local Setup
- Open your web browser
- Go to: **http://localhost:3000**
- Make sure both backend and dashboard are running (see SETUP.md)

### Online (Render.com)
- Go to your dashboard URL: **https://your-dashboard-name.onrender.com**
- First visit may take 30-60 seconds if the system was sleeping (free tier)

---

## Dashboard Overview

When you first open the system, you'll see the main dashboard with:

### Quick Stats (Top of Page)
- **Total Predictions:** How many predictions the system has made
- **Active Bets:** Your currently pending bets
- **Win Rate:** Percentage of your bets that won
- **Total P&L:** Your profit/loss (green = profit, red = loss)

### Performance Chart
- Shows your profit/loss over time
- Hover over points to see details
- Helps you visualize your betting performance

### Recent Projections
- Latest predictions from the AI models
- Quick view of high-confidence plays

---

## Viewing Predictions

Click **"Projections"** in the sidebar to see today's predictions.

### What You'll See

Each prediction shows:
- **Player Name:** Who the prediction is for
- **Team:** Player's current team
- **Opponent:** Who they're playing against
- **Prop Type:** What stat is being predicted (e.g., Points, Passing Yards)
- **Projection:** The AI's predicted value
- **Confidence:** High/Medium/Low confidence level
- **Expected Value (EV):** How much value this bet has

### Understanding Confidence Levels

- 🟢 **High (80%+):** The AI is very confident in this prediction
- 🟡 **Medium (60-79%):** Moderate confidence, some uncertainty
- 🔴 **Low (<60%):** Less confident, higher risk

### Filtering Predictions

Use the filters at the top to:
- **Sport:** Switch between NBA, NFL, or view both
- **Date:** Look at predictions for different days
- **Confidence:** Show only high-confidence predictions
- **Prop Type:** Filter by specific stat types

### Using the Predictions

1. Review the predictions each day
2. Look for high confidence + high EV combinations
3. Compare with sportsbook lines
4. Place bets through your sportsbook
5. Log the bets in the Bet Tracker

---

## Finding Value Bets

Click **"Value Finder"** in the sidebar to find the best betting opportunities.

### What is a Value Bet?

A value bet is when the AI's projection differs significantly from the sportsbook line, creating positive expected value (EV).

### How to Use Value Finder

1. **Set Your Filters:**
   - Minimum confidence level (default: 60%)
   - Minimum expected value (default: 5%)
   - Sport preference

2. **Review the Results:**
   - Sorted by best value first
   - Shows why each bet has value
   - Includes model confidence

3. **Take Action:**
   - Click on a bet to see more details
   - Compare with your sportsbook's line
   - If the line matches, consider placing the bet
   - Log it in the Bet Tracker

### Value Finder Tips

- ✅ Look for consistent players, not one-hit wonders
- ✅ Check recent player news before betting
- ✅ Consider injury reports
- ✅ Don't bet on everything - be selective
- ✅ Higher EV = better value, but also verify the data

---

## Tracking Your Bets

Click **"Bet Tracker"** in the sidebar to manage your betting history.

### Adding a New Bet

1. **Click "Log New Bet"**

2. **Fill in the details:**
   - **Date:** When you placed the bet
   - **Sport:** NBA or NFL
   - **Entry Type:** How many picks (2-pick, 3-pick, etc.)
   - **Stake:** How much you bet (in dollars)
   - **Status:** Pending (default for new bets)

3. **Add Your Props:**
   - Click "Add Prop" for each pick
   - Enter player name
   - Select prop type (Points, Rebounds, etc.)
   - Enter the line (over/under value)
   - Select Over or Under

4. **Add Notes (Optional):**
   - Why you made this bet
   - Any relevant information
   - Your reasoning

5. **Click "Submit"**

### Viewing Active Bets

The **Active Bets** tab shows:
- All pending bets
- When they were placed
- Expected payout
- Quick action buttons

### Updating Bet Results

When a bet finishes:

1. Find the bet in the Active Bets tab
2. Click the "Update" button
3. Select the outcome:
   - **Won:** All props hit
   - **Lost:** One or more props missed
   - **Push:** Tie, stake returned
4. The system automatically calculates your profit/loss
5. Click "Save"

### Viewing Bet History

The **Bet History** tab shows:
- All completed bets
- Results and profit/loss
- Sortable and filterable
- Search by player name or date

### Deleting Bets

- Click the trash icon on any bet
- Confirm deletion
- Use this to remove test bets or mistakes

---

## Analyzing Performance

Click **"Analytics"** in the sidebar to view detailed performance metrics.

### Overall Statistics

- **Total Bets:** How many bets you've placed
- **Win Rate:** Your success percentage
- **Total Profit/Loss:** Overall results
- **ROI:** Return on investment percentage
- **Average Stake:** Your typical bet size

### Performance by Entry Type

See how you perform with:
- 2-pick bets
- 3-pick bets
- 4-pick bets
- 5-pick bets

This helps you identify which bet types work best for you.

### Performance by Prop Type

See which props are most profitable:
- Points
- Rebounds
- Assists
- Passing Yards
- Receiving Yards
- etc.

### Performance by Sport

Compare your results:
- NBA bets
- NFL bets
- Which sport you're better at

### Daily Trend Chart

- See profit/loss over time
- Identify winning and losing streaks
- Track improvement

### Using Analytics to Improve

1. **Identify Strengths:**
   - Which prop types do you win most on?
   - Which entry types are most profitable?
   - Focus on what works

2. **Identify Weaknesses:**
   - Which bets consistently lose?
   - Are you betting too much?
   - Adjust your strategy

3. **Track Progress:**
   - Is your win rate improving?
   - Is your ROI increasing?
   - Are you staying disciplined?

---

## Managing Bankroll

Click **"Bankroll"** in the sidebar to manage your betting funds.

### Setting Your Bankroll

1. Enter your total betting budget
2. The system tracks how much is at risk
3. Shows available funds
4. Calculates recommended bet sizes

### Bankroll Management Principles

- **Never bet money you can't afford to lose**
- **Typical bet size: 1-5% of bankroll**
- **Don't chase losses with bigger bets**
- **Replenish bankroll periodically from profits**

### Risk Management

The system shows:
- **Total at Risk:** Money on pending bets
- **Exposure:** Percentage of bankroll at risk
- **Available Funds:** What you can still bet
- **Recommended Bet Size:** Based on Kelly Criterion

---

## Understanding the Data

### Where Does the Data Come From?

1. **Game Data:** Collected from ESPN and NBA APIs
2. **Player Stats:** Historical performance data
3. **Predictions:** Generated by machine learning models
4. **Your Bets:** Manually logged by you

### How Are Predictions Made?

1. **Data Collection:** System gathers recent stats
2. **Feature Engineering:** Creates relevant metrics
3. **Model Prediction:** AI analyzes patterns
4. **Confidence Scoring:** Calculates reliability
5. **EV Calculation:** Compares to typical lines

### Prediction Accuracy

- Models improve over time with more data
- High confidence predictions are more reliable
- Always verify with recent news/injuries
- Use as one tool in your decision-making

### Best Practices

✅ **Do:**
- Use predictions as guidance, not gospel
- Verify player status before betting
- Track all your bets honestly
- Review analytics regularly
- Stick to your bankroll management plan
- Be patient and disciplined

❌ **Don't:**
- Bet on every prediction
- Chase losses with bigger bets
- Ignore injury news
- Bet more than you can afford
- Make emotional decisions
- Bet without tracking

---

## Tips for Success

### 1. Start Small
- Begin with small stakes
- Learn the system
- Build confidence

### 2. Be Selective
- Don't bet everything you see
- Focus on high confidence + high EV
- Quality over quantity

### 3. Stay Informed
- Check injury reports
- Follow player news
- Understand team situations

### 4. Track Everything
- Log every bet honestly
- Review your analytics
- Learn from mistakes

### 5. Manage Risk
- Use proper bankroll management
- Don't bet more than 5% on one play
- Diversify your bets

### 6. Be Patient
- Success takes time
- Expect losing streaks
- Stay disciplined

---

## Getting the Most From Your System

### Daily Routine

1. **Morning:**
   - Check today's predictions
   - Review value finder
   - Compare with sportsbook lines

2. **Before Games:**
   - Verify player status
   - Place selected bets
   - Log them in tracker

3. **After Games:**
   - Update bet results
   - Check analytics
   - Plan for tomorrow

### Weekly Review

- Review your weekly performance
- Identify patterns
- Adjust strategy if needed
- Plan for next week

### Monthly Analysis

- Deep dive into analytics
- Calculate actual ROI
- Adjust bankroll if needed
- Set goals for next month

---

## Need Help?

- **Technical Issues:** See TROUBLESHOOTING.md
- **Setup Problems:** See SETUP.md
- **Deployment Issues:** See DEPLOYMENT.md

Remember: This system is a tool to help you make informed decisions. It doesn't guarantee wins, but it gives you an edge through data-driven insights. Always bet responsibly and within your means.

Good luck! 🎯
