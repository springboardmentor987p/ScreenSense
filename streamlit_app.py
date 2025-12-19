import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
from io import StringIO

# -------------------------------
# Helper: load dataset (cached)
# -------------------------------
@st.cache_data
def load_data(path: str = "Indian_Kids_Screen_Time.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.copy()
    df.drop_duplicates(inplace=True)
    df.fillna(df.mean(numeric_only=True), inplace=True)
    if 'Health_Impacts' in df.columns:
        df['Health_Impacts'] = pd.to_numeric(df['Health_Impacts'], errors='coerce')
    return df

# -------------------------------
# Recommendation logic
# -------------------------------
def get_recommendation(age, gender, screen_time, study_time, sleep_time, physical_activity):
    df = st.session_state.get("df")

    if "avg_by_age" not in st.session_state:
        st.session_state["avg_by_age"] = df.groupby('Age')['Avg_Daily_Screen_Time_hr'].mean()
    if "avg_by_gender" not in st.session_state:
        st.session_state["avg_by_gender"] = df.groupby('Gender')['Avg_Daily_Screen_Time_hr'].mean()

    avg_by_age = st.session_state["avg_by_age"]
    avg_by_gender = st.session_state["avg_by_gender"]
    avg_screen_time = df['Avg_Daily_Screen_Time_hr'].mean()

    if age in avg_by_age.index:
        avg_age_screen = float(avg_by_age.loc[age])
    else:
        closest_age = int(min(avg_by_age.index, key=lambda x: abs(x - age)))
        avg_age_screen = float(avg_by_age.loc[closest_age])

    if gender in avg_by_gender.index:
        avg_gender_screen = float(avg_by_gender.loc[gender])
    else:
        avg_gender_screen = float(avg_screen_time)

    if screen_time < 3:
        usage_level = "Low"
    elif 3 <= screen_time <= 6:
        usage_level = "Moderate"
    else:
        usage_level = "High"

    if 'Health_Impacts' in df.columns:
        correlation = df['Avg_Daily_Screen_Time_hr'].corr(df['Health_Impacts'])
        if correlation > 0.3:
            base_message = "More screen time generally worsens health."
        elif correlation < -0.3:
            base_message = "Higher screen time unexpectedly improves health (dataset-specific trend)."
        else:
            base_message = "Screen time and health have a weak correlation in this dataset."
    else:
        base_message = "Health data not found — using general wellness rules."

    if screen_time > 7:
        health_risk = "⚠️ Very High risk of eye strain, anxiety, or poor sleep."
    elif 5 < screen_time <= 7:
        health_risk = "⚠️ High risk — try reducing leisure screen hours."
    elif 3 < screen_time <= 5:
        health_risk = "🟡 Moderate risk — manageable with breaks."
    else:
        health_risk = "🟢 Low risk — well balanced."

    lifestyle_tips = []
    if sleep_time < 7:
        lifestyle_tips.append("Increase sleep to 7–9 hours/day.")
    elif sleep_time > 9:
        lifestyle_tips.append("Sleeping longer than 9 hours may reduce daytime productivity.")
    else:
        lifestyle_tips.append("Healthy sleep duration maintained.")

    if study_time < 2:
        lifestyle_tips.append("Increase study focus time to at least 3 hours/day.")
    elif 2 <= study_time <= 5:
        lifestyle_tips.append("Balanced study schedule maintained.")
    else:
        lifestyle_tips.append("Excellent study dedication!")

    if physical_activity.lower() == "no":
        lifestyle_tips.append("Add at least 30 minutes of daily physical activity.")
    else:
        lifestyle_tips.append("Good — daily physical activity helps reduce negative effects of screen time.")

    personalised = []
    if usage_level == "High":
        personalised += [
            "Reduce screen time gradually by 30–60 mins each week.",
            "Use apps (e.g., Digital Wellbeing) to set limits.",
            "Avoid screens 1 hour before bedtime."
        ]
    elif usage_level == "Moderate":
        personalised += [
            "Follow the 20-20-20 rule during long screen sessions.",
            "Prefer educational/creative screen use when possible."
        ]
    else:
        personalised += [
            "Maintain your balanced routine.",
            "Keep replacing screen time with hobbies and outdoor play."
        ]

    if gender.lower() == "male":
        personalised.append("Boys may spend more time gaming — balance with offline activities.")
    elif gender.lower() == "female":
        personalised.append("Girls may multitask between studies and social media — schedule screen breaks.")

    summary = {
        "age": int(age),
        "gender": gender,
        "screen_time": float(screen_time),
        "usage_level": usage_level,
        "avg_age_group": avg_age_screen,
        "avg_gender_group": avg_gender_screen,
        "health_prediction": base_message,
        "health_risk": health_risk,
        "lifestyle_tips": lifestyle_tips,
        "recommendations": personalised
    }

    return summary


# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="Smart Screen Time — Demo", layout="wide")
st.title("🎯 Smart Screen Time — Recommendations")

with st.sidebar:
    st.header("Data & Settings")
    uploaded = st.file_uploader("Upload dataset CSV (optional)", type=["csv"])
    if uploaded is not None:
        df = pd.read_csv(uploaded)
        df.drop_duplicates(inplace=True)
        df.fillna(df.mean(numeric_only=True), inplace=True)
        if 'Health_Impacts' in df.columns:
            df['Health_Impacts'] = pd.to_numeric(df['Health_Impacts'], errors='coerce')
        st.session_state['df'] = df
        st.success("Loaded uploaded dataset")
    else:
        try:
            df = load_data()
            st.session_state['df'] = df
        except Exception as e:
            st.error(f"Could not load default dataset: {e}")

    st.markdown("---")
    if 'df' in st.session_state:
        st.write(f"Rows: {len(st.session_state['df'])}")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("👤 Enter child / user details")
    age = st.number_input("Age", min_value=1, max_value=25, value=12)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    screen_time = st.slider("Avg daily screen time (hrs)", 0.0, 16.0, 3.0, 0.25)
    study_time = st.slider("Avg daily study time (hrs)", 0.0, 12.0, 2.0, 0.25)
    sleep_time = st.slider("Avg daily sleep time (hrs)", 0.0, 16.0, 8.0, 0.25)
    physical_activity = st.radio("Daily outdoor/physical activity?", ["yes", "no"])
    if st.button("Get Recommendation"):
        st.session_state['last_result'] = get_recommendation(
            age, gender, screen_time, study_time, sleep_time, physical_activity
        )

with col2:
    st.subheader("📈 Dataset visuals & comparison")
    if 'df' in st.session_state:
        df = st.session_state['df']

        fig, ax = plt.subplots(figsize=(6, 3))
        ax.hist(df['Avg_Daily_Screen_Time_hr'].dropna(), bins=20)
        ax.set_xlabel('Avg daily screen time (hrs)')
        ax.set_ylabel('Count')
        ax.set_title('Distribution of Avg Daily Screen Time')
        st.pyplot(fig)

        age_group = df.groupby('Age')['Avg_Daily_Screen_Time_hr'].mean().sort_index()
        fig2, ax2 = plt.subplots(figsize=(6, 3))
        ax2.bar(age_group.index.astype(str), age_group.values)
        ax2.set_xlabel('Age')
        ax2.set_ylabel('Avg hrs/day')
        ax2.set_title('Average Screen Time by Age')
        plt.xticks(rotation=45)
        st.pyplot(fig2)
    else:
        st.info("Upload dataset or place 'Indian_Kids_Screen_Time.csv' next to this app to show visuals.")

st.markdown("---")

if 'last_result' in st.session_state:
    res = st.session_state['last_result']
    st.subheader("🔎 Recommendation Summary")
    st.markdown(
        f"**Age:** {res['age']}  \n"
        f"**Gender:** {res['gender']}  \n"
        f"**Screen time:** {res['screen_time']} hrs/day ({res['usage_level']})"
    )
    st.markdown(
        f"**Dataset age-group avg:** {res['avg_age_group']:.2f} hrs/day  \n"
        f"**Dataset gender-group avg:** {res['avg_gender_group']:.2f} hrs/day"
    )
    st.markdown(f"**Health prediction:** {res['health_prediction']}")
    st.markdown(f"**Health risk:** {res['health_risk']}")

    st.subheader("🧾 Lifestyle Tips")
    for tip in res['lifestyle_tips']:
        st.write(f"- {tip}")

    st.subheader("✅ Personalized Recommendations")
    for rec in res['recommendations']:
        st.write(f"- {rec}")

    buffer = StringIO()
    json.dump(res, buffer, indent=2)
    st.download_button("Download recommendation (JSON)", buffer.getvalue(), "recommendation.json", "application/json")
else:
    st.info("Fill the form on the left and click 'Get Recommendation' to see personalized advice.")

st.markdown("---")
st.caption("Built with Streamlit — Smart Screen Time Demo")
