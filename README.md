#  Screen Time Advisor

A comprehensive digital wellness application that analyzes children's screen time and provides personalized recommendations using AI.

---

##  Quick Start

### Prerequisites
- Python 3.12+
- Google Gemini API Key: [Get it here](https://ai.google.dev/)

### Installation (2 minutes)

\\\ash
# Clone the repository
git clone https://github.com/Dona-Sojan/screenspace-analysis.git
cd screenspace-analysis

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo GEMINI_API_KEY=your-api-key-here > .env
\\\

### Run Locally

\\\ash
python main.py
\\\

Open: **http://127.0.0.1:3000**

---

##  Key Features

 **Screen Time Analysis** - Personalized health scoring based on age & usage  
 **AI Recommendations** - Google Gemini-powered insights  
 **Break Routines** - 10 different 2-minute digital break plans  
 **Dashboard** - Visual analytics with Tableau integration  
 **Mobile Responsive** - Works perfectly on all devices  
 **Feedback System** - User experience rating & AI analysis  

---

##  Project Structure

\\\
dona/
 main.py                          # FastAPI backend
 style.html                       # Frontend (all-in-one)
 Indian_Kids_Screen_Time.csv      # Dataset (9,712 records)
 recommend.py                     # Recommendation engine
 requirements.txt                 # Python dependencies
 .env                            # Environment variables
 DEPLOYMENT_GUIDE.md             # Detailed deployment options
 COMPREHENSIVE_DOCUMENTATION.md  # Full technical docs
\\\

---

##  Deployment

### Fastest Option: Vercel (5 minutes)

1. Go to: https://vercel.com
2. Sign in with GitHub
3. New Project  Select \screenspace-analysis\
4. Add Environment Variable: \GEMINI_API_KEY\
5. Deploy

**Live URL:** \https://screenspace-analysis.vercel.app\

### Other Options
- **Render**: https://render.com (10 min)
- **Railway**: https://railway.app (10 min)
- **PythonAnywhere**: https://pythonanywhere.com (10 min)

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed steps.

---

##  Environment Variables

\\\env
GEMINI_API_KEY=your-google-gemini-api-key
\\\

Get API key: https://ai.google.dev/

---

##  Key API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| \/\ | GET | Load application |
| \/api/recommend-gemini\ | POST | Get AI recommendations |
| \/api/feedback\ | POST | Submit user feedback |
| \/api/dashboard\ | GET | Get analytics data |
| \/health\ | GET | Health check |

---

##  Features at a Glance

### Advisor View
- Enter age, daily screen time, device type
- Get personalized digital health score
- AI-powered improvement suggestions

### Break Routines
- 10 randomized break activity types
- Physical, Mindfulness, Outdoor, Social, Creative, etc.
- 2-minute structured activities with 5 steps each

### Dashboard
- Real-time analytics charts
- Health impact distribution
- Embedded Tableau visualizations
- User statistics

### Feedback System
- Star rating (1-5)
- Text feedback input
- AI analysis using Gemini
- Automatic storage

---

##  Technology Stack

**Backend:**
- FastAPI (Python web framework)
- Google Gemini API (AI/ML)
- Pandas (Data processing)
- Uvicorn (ASGI server)

**Frontend:**
- HTML5, CSS3, JavaScript
- Tailwind CSS (Styling)
- Chart.js (Data visualization)
- Font Awesome (Icons)

**Data:**
- CSV dataset (9,712 Indian children records)
- Tableau dashboards (embedded)

---

##  Responsive Design

 Mobile (320px+) - Full functionality  
 Tablet (768px+) - Sidebar navigation  
 Desktop (1024px+) - Full layout  
 All devices: Touch-friendly (44px+ targets)

---

##  API Rate Limiting

- Exponential backoff retry (5, 10, 20, 40, 80 seconds)
- Graceful fallback for API limits
- Demo mode with pre-generated responses

---

##  Documentation

- **[COMPREHENSIVE_DOCUMENTATION.md](COMPREHENSIVE_DOCUMENTATION.md)** - Complete technical guide
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Deployment options & steps

---

##  Testing

\\\ash
# Run tests
python -m pytest test_all.py

# Quick health check
curl http://127.0.0.1:3000/health
\\\

---

##  Sample Data

Dataset includes:
- 9,712 children records from India
- Age range: 3-18 years
- Screen time: 0-12 hours/day
- Device types: Smartphone, Tablet, Laptop, Desktop, Gaming Console, Smart TV

---

##  Configuration

All settings in \main.py\:
- API endpoint: \http://127.0.0.1:3000\
- Port: \3000\
- CORS enabled
- Gemini model: \gemini-1.5-flash\

---

##  Troubleshooting

**Issue:** API Key not working  
**Solution:** Check \.env\ file has correct key from https://ai.google.dev/

**Issue:** Port already in use  
**Solution:** Change port in \main.py\

**Issue:** Slow response  
**Solution:** Wait 2-3 seconds for Gemini API (exponential backoff active)

---

##  Performance

- Load time: < 2 seconds
- API response: < 3 seconds
- Mobile optimized: 

---

##  Get Started Now!

\\\ash
git clone https://github.com/Dona-Sojan/screenspace-analysis.git
cd screenspace-analysis
python main.py
\\\

Open: **http://127.0.0.1:3000**

---

**Author:** Dona Sojan  
**Repository:** https://github.com/Dona-Sojan/screenspace-analysis  
**Status:**  Production Ready
