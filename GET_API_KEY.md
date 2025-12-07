# How to Get Your Gemini API Key

## Quick Setup (2 minutes)

1. **Go to Google AI Studio:**
   - Open: https://aistudio.google.com/app/apikey

2. **Create API Key:**
   - Click "Create API Key"
   - Select "Create API key in new project" or choose existing project
   - Copy the API key (it looks like: `AIzaSyD...`)

3. **Add to `.env` file:**
   - Open `.env` in your project folder
   - Replace this line:
     ```
     GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
     ```
   - With your actual key:
     ```
     GEMINI_API_KEY=AIzaSyD1234567890...
     ```

4. **Save and Restart Server:**
   - Save the `.env` file
   - Stop the server (Ctrl+C in terminal)
   - Restart with: `python -m uvicorn main:app --reload`

5. **Test It:**
   - Go to http://127.0.0.1:3000
   - Fill in the form and click "Generate My Personal Plan"
   - It should now work!

## Troubleshooting

- **Still getting error?** Make sure you saved the `.env` file and restarted the server.
- **Invalid API Key?** Double-check you copied the entire key correctly.
- **Rate limited?** Free tier has limits. Wait a few minutes and try again.

---

If you don't want to use Gemini, I can add a **demo mode** that shows sample recommendations instead!
