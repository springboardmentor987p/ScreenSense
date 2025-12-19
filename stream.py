# app.py
"""
Drop `Indian_Kids_Screen_Time.csv` next to this file (optional).
"""

from datetime import datetime, timedelta
from io import StringIO
import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# ---------------------------- Config ----------------------------
APP_TITLE = "Smart Screen Time -Recommendation System"
CHART_FIGSIZE = (4, 3)  # compact charts
sns.set_theme(style="darkgrid")

st.set_page_config(page_title=APP_TITLE, layout="wide")

# ---------------------------- CSS: Black bg, white fonts ----------------------------
st.markdown(
    """
    <style>
    :root { color-scheme: dark; }
    html, body, [class*="css"]  {
      background: #000000 !important;
      color: #ffffff !important;
      font-family: 'Inter', 'Segoe UI', Roboto, Arial, sans-serif;
    }
    header { background: transparent !important; }
    .stButton>button { background-color: #0b63d6; color: white; }
    .card {
      background: #0f1724;  /* dark card */
      border: 1px solid #1f2937;
      padding: 12px;
      border-radius: 10px;
      margin-bottom: 10px;
    }
    .metric {
      background: linear-gradient(90deg,#07132a,#0b2540);
      padding: 10px;
      border-radius: 8px;
      text-align: center;
      margin-bottom: 8px;
    }
    .header {
      background: linear-gradient(90deg, #021622, #0b2540);
      padding: 18px;
      border-radius: 10px;
      margin-bottom: 14px;
      text-align: center;
    }
    .small { color: #9ca3af; font-size:13px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------- Helper: load dataset (safe fallback) ----------------------------
@st.cache_data
def load_dataset(path: str = "Indian_Kids_Screen_Time.csv") -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
    except Exception:
        # synthetic fallback dataset so the app never breaks
        rng = np.random.default_rng(42)
        n = 400
        df = pd.DataFrame({
            "Age": rng.integers(6, 18, n),
            "Gender": rng.choice(["Male", "Female", "Other"], n),
            "Avg_Daily_Screen_Time_hr": np.clip(rng.normal(3.6, 1.8, n), 0, 12),
        })
        df["Health_Impacts"] = np.clip(df["Avg_Daily_Screen_Time_hr"] * 10 + rng.normal(0, 7, n), 0, 100)
    # normalize common alternate column names
    df = df.copy()
    if "Screen_Time" in df.columns and "Avg_Daily_Screen_Time_hr" not in df.columns:
        df.rename(columns={"Screen_Time": "Avg_Daily_Screen_Time_hr"}, inplace=True)
    if "AvgDailyScreenTime" in df.columns and "Avg_Daily_Screen_Time_hr" not in df.columns:
        df.rename(columns={"AvgDailyScreenTime": "Avg_Daily_Screen_Time_hr"}, inplace=True)
    df.drop_duplicates(inplace=True)
    df.fillna(df.mean(numeric_only=True), inplace=True)
    if "Health_Impacts" in df.columns:
        df["Health_Impacts"] = pd.to_numeric(df["Health_Impacts"], errors="coerce")
    return df

# ---------------------------- Recommendation helpers ----------------------------
def compute_mental_risk(stress_level: int, mood_score: int):
    composite = (stress_level * 0.65) + ((10 - mood_score) * 0.35)
    if composite >= 7:
        return "High", "High stress and low mood — short-term wellness tasks and professional support if persistent."
    elif composite >= 4:
        return "Moderate", "Moderate stress — add micro-wellness practices and track mood."
    else:
        return "Low", "Low risk — continue current wellness habits."

def generate_weekly_plan(screen_time, study_time, sleep_time, activity_minutes, stress_level, mood_score, age):
    plan = {}
    target = 4.0
    if screen_time > target:
        step = (screen_time - target) / 7.0
    else:
        step = max(0.0, (screen_time - (target - 1)) / 14.0)
    base = datetime.now().date()
    for i in range(7):
        day = (base + timedelta(days=i)).isoformat()
        planned_screen = round(max(0.5, screen_time - step * (i + 1)), 2)
        planned_study = round(min(max(1.0, study_time), 6.0), 2)
        if sleep_time < 7:
            planned_sleep = round(min(9.0, sleep_time + 0.2 * (i + 1)), 2)
        elif sleep_time > 9:
            planned_sleep = round(max(7.0, sleep_time - 0.2 * (i + 1)), 2)
        else:
            planned_sleep = round(sleep_time, 2)
        planned_activity = round(max(0.25, activity_minutes / 60.0), 2)
        if stress_level >= 7 or mood_score <= 4:
            mental_task = "10-min guided breathing + 20-min hobby or family time"
        elif stress_level >= 4 or mood_score <= 6:
            mental_task = "10-min journaling or short walk"
        else:
            mental_task = "Mindful micro-breaks (5 min)"
        plan[day] = {
            "screen_limit_hrs": planned_screen,
            "study_hrs": planned_study,
            "sleep_hrs": planned_sleep,
            "activity_hrs": planned_activity,
            "mental_task": mental_task
        }
    return plan

def study_screen_balance_score(screen_time, study_time, sleep_time, activity_minutes):
    score = 50.0
    score += min(25.0, study_time * 4.0)
    if screen_time <= 2:
        score += 10
    elif screen_time <= 4:
        score += 5
    elif screen_time <= 6:
        score -= 5
    else:
        score -= 20
    if 7 <= sleep_time <= 9:
        score += 8
    else:
        if sleep_time < 6:
            score -= 8
        elif sleep_time > 10:
            score -= 6
    score += min(12, activity_minutes / 10.0)
    return int(np.clip(score, 0, 100))

def recommend(inputs: dict, df: pd.DataFrame = None):
    age = int(inputs.get("age", 12))
    gender = inputs.get("gender", "Other")
    screen_time = float(inputs.get("screen_time", 3.0))
    study_time = float(inputs.get("study_time", 2.0))
    sleep_time = float(inputs.get("sleep_time", 8.0))
    activity_minutes = int(inputs.get("activity_minutes", 30))
    stress_level = int(inputs.get("stress_level", 4))
    mood_score = int(inputs.get("mood_score", 7))

    # dataset baselines
    age_baseline = None
    gender_baseline = None
    if df is not None and "Avg_Daily_Screen_Time_hr" in df.columns:
        try:
            age_baseline = float(df.groupby("Age")["Avg_Daily_Screen_Time_hr"].mean().get(age, np.nan))
        except Exception:
            age_baseline = None
        try:
            gender_baseline = float(df.groupby("Gender")["Avg_Daily_Screen_Time_hr"].mean().get(gender, np.nan))
        except Exception:
            gender_baseline = None

    if screen_time < 3:
        usage = "Low"
    elif screen_time <= 6:
        usage = "Moderate"
    else:
        usage = "High"

    if screen_time > 7:
        phys = "Very High"
    elif screen_time > 5:
        phys = "High"
    elif screen_time > 3:
        phys = "Moderate"
    else:
        phys = "Low"

    mental_label, mental_expl = compute_mental_risk(stress_level, mood_score)

    suggestions = []
    if usage == "High":
        suggestions += [
            "Gradually reduce leisure screen time by 30–45 mins/week; set fixed off-screen windows.",
            "Avoid screens 60 minutes before bed; enable blue-light filters after 8 PM."
        ]
    elif usage == "Moderate":
        suggestions += [
            "Use the 20–20–20 rule during extended sessions.",
            "Prioritize active or creative screen activities over passive scrolling."
        ]
    else:
        suggestions += ["Maintain the balanced routine and nurture offline hobbies."]

    if mental_label == "High":
        suggestions.append("Start daily guided breathing (10 min) and consider professional support if stress persists.")
    elif mental_label == "Moderate":
        suggestions.append("Add short walks or journaling; log mood daily for 2 weeks.")
    else:
        suggestions.append("Keep current wellbeing practices and social activities.")

    if study_time < 2:
        suggestions.append("Increase focused study to 2–3 hours using Pomodoro or 50/10 structure.")
    elif study_time > 6:
        suggestions.append("If studying >6 hrs/day, ensure structured breaks and avoid late-night sessions.")

    parental_tips = [
        "Set collaborative screen rules (device-off window before bedtime).",
        "Model healthy behavior: device-free family meals and evenings.",
        "Reward study & activity with limited screen treats."
    ]
    recommended_tools = [
        "Digital Wellbeing (Android) / Screen Time (iOS)",
        "Forest (focus timer)",
        "Headspace / Calm (guided breathing)",
        "Use Night Shift / blue-light filters after 8 PM"
    ]

    balance_score = study_screen_balance_score(screen_time, study_time, sleep_time, activity_minutes)
    weekly_plan = generate_weekly_plan(screen_time, study_time, sleep_time, activity_minutes, stress_level, mood_score, age)

    out = {
        "age": age,
        "gender": gender,
        "screen_time": screen_time,
        "study_time": study_time,
        "sleep_time": sleep_time,
        "activity_minutes": activity_minutes,
        "usage_level": usage,
        "physical_risk": phys,
        "mental_risk": {"level": mental_label, "explanation": mental_expl},
        "suggestions": suggestions,
        "parental_tips": parental_tips,
        "recommended_tools": recommended_tools,
        "study_screen_balance_score": balance_score,
        "weekly_plan": weekly_plan,
        "baselines": {"age_group_avg": age_baseline, "gender_group_avg": gender_baseline},
        "generated_at": datetime.now().isoformat()
    }
    return out

# ---------------------------- Load dataset & session init ----------------------------
if "df" not in st.session_state:
    st.session_state["df"] = load_dataset()
df = st.session_state["df"]

if "history" not in st.session_state:
    st.session_state["history"] = []

# ---------------------------- Header ----------------------------
st.markdown(f'<div class="header"><h2 style="margin:0;color:#ffffff;">📱 {APP_TITLE}</h2><div class="small">Clean, professional, presentation-ready — black theme</div></div>', unsafe_allow_html=True)

# ---------------------------- Sidebar (inputs/upload) ----------------------------
with st.sidebar:
    st.header("Profile & Data")
    uploaded = st.file_uploader("Upload CSV (optional)", type=["csv"])
    if uploaded is not None:
        try:
            uploaded_df = pd.read_csv(uploaded)
            # normalize columns
            if "Screen_Time" in uploaded_df.columns and "Avg_Daily_Screen_Time_hr" not in uploaded_df.columns:
                uploaded_df.rename(columns={"Screen_Time": "Avg_Daily_Screen_Time_hr"}, inplace=True)
            st.session_state["df"] = uploaded_df
            df = st.session_state["df"]
            st.success("Dataset uploaded and loaded.")
        except Exception as e:
            st.error(f"Failed to load CSV: {e}")
    st.markdown("---")
    st.markdown("**Quick dataset stats**")
    st.write(f"Rows: {len(df)}")
    if "Avg_Daily_Screen_Time_hr" in df.columns:
        st.write(f"Dataset avg screen time: {df['Avg_Daily_Screen_Time_hr'].mean():.2f} hrs")
    st.markdown("---")
    if st.button("Clear Local History"):
        st.session_state["history"] = []
        st.success("History cleared.")

# ---------------------------- Input form ----------------------------
with st.form("input_form", clear_on_submit=False):
    st.subheader("Enter child / user details")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        age = st.number_input("Age", min_value=4, max_value=25, value=12, step=1)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=0)
    with c2:
        screen_time = st.slider("Avg daily screen time (hrs)", 0.0, 16.0, 4.0, 0.25)
        study_time = st.slider("Avg daily study time (hrs)", 0.0, 12.0, 2.0, 0.25)
    with c3:
        sleep_time = st.slider("Avg daily sleep (hrs)", 0.0, 16.0, 8.0, 0.25)
        activity_minutes = st.slider("Daily physical activity (minutes)", 0, 180, 30, 5)
    with c4:
        st.markdown("**Mental wellness**")
        stress_level = st.slider("Stress (0 = none, 10 = very high)", 0, 10, 4)
        mood_score = st.slider("Mood (1 = low, 10 = excellent)", 1, 10, 7)
        private = st.checkbox("I confirm inputs are approximate and private to this session", value=True)
    submitted = st.form_submit_button("Generate Recommendation & Weekly Plan")

# ---------------------------- Process submission ----------------------------
if submitted:
    inputs = {
        "age": age, "gender": gender, "screen_time": screen_time, "study_time": study_time,
        "sleep_time": sleep_time, "activity_minutes": activity_minutes,
        "stress_level": stress_level, "mood_score": mood_score
    }
    out = recommend(inputs, df=df)
    st.session_state["last_result"] = out
    # store history
    entry = {"ts": datetime.now().isoformat(), "inputs": inputs, "output": out}
    st.session_state["history"].insert(0, entry)
    st.session_state["history"] = st.session_state["history"][:25]
    st.success("Recommendation generated.")

# ---------------------------- Tabs ----------------------------
tabs = st.tabs(["Overview", "Health", "Education", "Risk Zone"])

# ---------------------------- Overview Tab ----------------------------
with tabs[0]:
    st.header("Overview")
    if "last_result" in st.session_state:
        out = st.session_state["last_result"]
        # Top metrics
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Screen (hrs/day)", f"{out['screen_time']:.2f}")
        r2.metric("Usage level", out["usage_level"])
        r3.metric("Balance score (0-100)", out["study_screen_balance_score"])
        age_avg = out["baselines"].get("age_group_avg", None)
        r4.metric("Age group avg (hrs)", f"{age_avg:.2f}" if age_avg else "N/A")
        st.markdown("---")
        # Charts: distribution + you vs healthy
        c1, c2 = st.columns(2)
        with c1:
            fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
            if "Avg_Daily_Screen_Time_hr" in df.columns:
                ax.hist(df["Avg_Daily_Screen_Time_hr"].dropna(), bins=12, color="#1f77b4")
            else:
                ax.hist(df.iloc[:, 0].dropna(), bins=12, color="#1f77b4")
            ax.set_title("Dataset: Screen time distribution", color="white")
            ax.tick_params(colors="white")
            ax.set_facecolor("#000000")
            fig.patch.set_facecolor("#000000")
            st.pyplot(fig)
            plt.close(fig)
        with c2:
            fig2, ax2 = plt.subplots(figsize=CHART_FIGSIZE)
            ax2.bar(["You", "Healthy limit"], [out["screen_time"], 4.0], color=["#ff7f0e", "#2ca02c"])
            ax2.set_title("You vs Healthy (4 hrs)", color="white")
            ax2.tick_params(colors="white")
            ax2.set_facecolor("#000000")
            fig2.patch.set_facecolor("#000000")
            st.pyplot(fig2)
            plt.close(fig2)
    else:
        st.info("Fill the form and click 'Generate Recommendation & Weekly Plan' to see the overview.")

# ---------------------------- Health Tab ----------------------------
with tabs[1]:
    st.header("Health & Wellbeing")
    if "last_result" in st.session_state:
        out = st.session_state["last_result"]
        colA, colB = st.columns(2)
        with colA:
            st.subheader("Physical Risk")
            st.write(f"**Usage level:** {out['usage_level']}")
            st.write(f"**Physical risk:** {out['physical_risk']}")
            fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
            val = 10 if out["physical_risk"] == "Very High" else (7 if out["physical_risk"] == "High" else (4 if out["physical_risk"] == "Moderate" else 1))
            ax.barh(["Physical risk"], [val], color="#ff6347")
            ax.set_xlim(0, 10)
            ax.set_facecolor("#000000")
            fig.patch.set_facecolor("#000000")
            ax.tick_params(colors="white", labelcolor="white")
            st.pyplot(fig)
            plt.close(fig)
        with colB:
            st.subheader("Mental Risk")
            st.write(f"**Level:** {out['mental_risk']['level']}")
            st.write(out['mental_risk']['explanation'])
            fig2, ax2 = plt.subplots(figsize=CHART_FIGSIZE)
            mval = 10 if out["mental_risk"]["level"] == "High" else (6 if out["mental_risk"]["level"] == "Moderate" else 2)
            ax2.barh(["Mental risk"], [mval], color="#7b61ff")
            ax2.set_xlim(0, 10)
            ax2.set_facecolor("#000000")
            fig2.patch.set_facecolor("#000000")
            ax2.tick_params(colors="white", labelcolor="white")
            st.pyplot(fig2)
            plt.close(fig2)
        st.markdown("---")
        st.subheader("Balanced Suggestions")
        for s in out["suggestions"]:
            st.write("•", s)
        st.markdown("---")
        st.subheader("Weekly Plan")
        plan_df = pd.DataFrame.from_dict(out["weekly_plan"], orient="index")
        st.dataframe(plan_df, use_container_width=True)
    else:
        st.info("Generate a recommendation to see health guidance and the weekly plan.")

# ---------------------------- Education Tab ----------------------------
with tabs[2]:
    st.header("Education & Focus")
    if "last_result" in st.session_state:
        out = st.session_state["last_result"]
        st.metric("Study–Screen Balance Score", out["study_screen_balance_score"])
        st.markdown("**Study Suggestions**")
        study_sugs = [s for s in out["suggestions"] if "study" in s.lower() or "focus" in s.lower() or "pomodoro" in s.lower()]
        if not study_sugs:
            study_sugs = out["suggestions"][:2]
        for s in study_sugs:
            st.write("•", s)
        st.markdown("**Recommended Tools & Apps**")
        for t in out["recommended_tools"]:
            st.write("•", t)
    else:
        st.info("Generate a recommendation to see study suggestions and tools.")

# ---------------------------- Risk Zone Tab ----------------------------
with tabs[3]:
    st.header("Risk Zone & Parental Tips")
    if "last_result" in st.session_state:
        out = st.session_state["last_result"]
        if "Health_Impacts" in df.columns and "Avg_Daily_Screen_Time_hr" in df.columns:
            fig, ax = plt.subplots(figsize=CHART_FIGSIZE)
            sns.scatterplot(data=df, x="Avg_Daily_Screen_Time_hr", y="Health_Impacts", alpha=0.6, ax=ax)
            ax.axvline(out["screen_time"], color="red", linestyle="--", label=f"You ({out['screen_time']} hrs)")
            ax.set_xlabel("Screen time (hrs/day)", color="white")
            ax.set_ylabel("Health impact score", color="white")
            ax.set_title("Dataset: Screen time vs Health Impact", color="white")
            ax.tick_params(colors="white")
            fig.patch.set_facecolor("#000000")
            ax.set_facecolor("#000000")
            ax.legend()
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("Dataset doesn't have both screen-time & health-impact columns for scatter plot.")
        st.markdown("**Parental Tips**")
        for p in out["parental_tips"]:
            st.write("•", p)
    else:
        st.info("Generate a recommendation to view risk visuals and parental tips.")

# ---------------------------- History & Exports ----------------------------
st.markdown("---")
st.header("History & Export")
if st.session_state["history"]:
    st.write(f"Local session history: {len(st.session_state['history'])} entries")
    for i, h in enumerate(st.session_state["history"][:6]):
        with st.expander(f"{i+1}. {h['ts']}", expanded=(i == 0)):
            st.write("Inputs:")
            st.json(h["inputs"])
            st.write("Top suggestions:")
            for s in h["output"]["suggestions"][:5]:
                st.write("-", s)
            # download item
            buff = StringIO()
            json.dump(h["output"], buff, indent=2)
            st.download_button(f"Download entry {i+1} (JSON)", data=buff.getvalue(), file_name=f"recommendation_{i+1}.json", mime="application/json")
else:
    st.info("No history yet — generate a recommendation to store results here.")

# latest download
if "last_result" in st.session_state:
    st.markdown("### Export latest recommendation")
    last = st.session_state["last_result"]
    jbuf = StringIO()
    json.dump(last, jbuf, indent=2)
    st.download_button("Download Recommendation (JSON)", data=jbuf.getvalue(), file_name="recommendation.json", mime="application/json")
    # weekly plan csv
    plan_df = pd.DataFrame.from_dict(last["weekly_plan"], orient="index")
    cbuf = StringIO()
    plan_df.to_csv(cbuf)
    st.download_button("Download Weekly Plan (CSV)", data=cbuf.getvalue(), file_name="weekly_plan.csv", mime="text/csv")

st.caption("Black theme / white fonts applied. If any text still appears faint, tell me which area and I'll adjust contrast & font sizes.")
