# Fix for API Error 403 - Setup Guide

## Problem
The "Generate My Personal Plan" button was showing **HTTP error! status: 403** because the frontend was calling Google Gemini API directly, which was blocked by CORS (Cross-Origin Resource Sharing).

## Solution Implemented
I've created a **backend proxy endpoint** that handles Gemini API calls server-side, avoiding CORS issues.

## Setup Steps

### 1. Get Your Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click **"Get API Key"** and create a new API key
3. Copy your API key (it looks like: `AIzaSy...`)

### 2. Add API Key to `.env` File
1. Open the `.env` file in your project root (created automatically)
2. Replace `YOUR_GEMINI_API_KEY_HERE` with your actual API key:
   ```
   GEMINI_API_KEY=AIzaSy...YOUR_KEY_HERE...
   ```
3. Save the file

### 3. Restart the Server
Make sure your FastAPI server is running with:
```powershell
& .\venv\Scripts\Activate.ps1
& .\venv\Scripts\python.exe -m uvicorn main:app --reload
```

### 4. Test It
- Open http://127.0.0.1:8000 in your browser
- Fill in the form (Age: 66, Gender: Female, Screen Time: 8 hours, Device: Laptop/Desktop)
- Click **"Generate My Personal Plan"** button
- You should see the recommendation without any 403 error!

## Files Changed
- **main.py**: Added `/api/recommend-gemini` proxy endpoint + .env loading
- **style.html**: Updated `fetchGeminiRecommendations()`, `fetchGeminiBreakPlan()`, and `fetchGeminiTTS()` to use the backend proxy instead of calling Gemini directly
- **.env**: Created with GEMINI_API_KEY placeholder

## How It Works
1. Frontend collects user input and sends it to `http://127.0.0.1:8000/api/recommend-gemini`
2. Backend receives the request and calls Google Gemini API with the API key (server-side, no CORS issues)
3. Backend returns the response to frontend
4. Frontend displays the recommendation to the user

## Troubleshooting
- If you still see 403 error: Make sure your GEMINI_API_KEY in `.env` is correct and the server has restarted
- If you see "API key not configured": You haven't added the key to `.env` or didn't restart the server
- If recommendation is empty: Check browser console (F12) for error messages and report them
