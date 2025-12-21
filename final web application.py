import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
from io import BytesIO
import base64
import plotly.express as px
import plotly.graph_objects as go

# Set style for plots
plt.style.use('seaborn-v0_8-whitegrid')

# -------------------------------
# 1. Load and Prepare Dataset
# -------------------------------
@st.cache_data
def load_and_prepare_data():
    try:
        df = pd.read_csv("Indian_Kids_Screen_Time.csv")
        if df.empty:
            raise ValueError("Dataset is empty.")
    except FileNotFoundError:
        st.error("❌ Dataset 'Indian_Kids_Screen_Time.csv' not found. Please upload or place the file in the directory.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error loading dataset: {e}")
        st.stop()
    
    # Create a copy for original values (before scaling)
    df_original = df.copy()
    
    # Clean the data
    df.drop_duplicates(inplace=True)
    df.fillna(df.mean(numeric_only=True), inplace=True)
    
    # Handle 'Health_Impacts' column: if it's strings like 'Poor Sleep, Eye Strain', convert to count of issues
    if 'Health_Impacts' in df.columns:
        if df['Health_Impacts'].dtype == 'object':
            # Assume comma-separated strings, count the number of issues as a proxy for severity
            df['Health_Impacts'] = df['Health_Impacts'].fillna('').apply(lambda x: len(x.split(',')) if x.strip() else 0)
            df_original['Health_Impacts'] = df['Health_Impacts']  # Update original too
        df['Health_Impacts'] = pd.to_numeric(df['Health_Impacts'], errors='coerce')
        df_original['Health_Impacts'] = pd.to_numeric(df_original['Health_Impacts'], errors='coerce')
    
    # Ensure numeric columns
    numeric_cols = ['Avg_Daily_Screen_Time_hr', 'Age']
    if 'Health_Impacts' in df.columns:
        numeric_cols.append('Health_Impacts')
    
    # Additional preprocessing (scale only for ML, keep original for display)
    scaler = StandardScaler()
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    
    # Add Age_Group for visualizations
    df['Age_Group'] = pd.cut(df_original['Age'], bins=[0, 10, 18, 25, 40, 60],
                             labels=['0-10','11-18','19-25','26-40','41-60'])
    df_original['Age_Group'] = df['Age_Group']  # Add to original too
    
    return df, df_original

df, df_original = load_and_prepare_data()

# -------------------------------
# 2. Basic Statistics (use original df for accurate values)
# -------------------------------
avg_screen_time = df_original['Avg_Daily_Screen_Time_hr'].mean()
avg_by_age = df_original.groupby('Age')['Avg_Daily_Screen_Time_hr'].mean()
avg_by_gender = df_original.groupby('Gender')['Avg_Daily_Screen_Time_hr'].mean()

# -------------------------------
# Streamlit App with Enhanced UI and Bug Fixes
# -------------------------------
st.set_page_config(page_title="Smart Screen Time Recommender", page_icon="📱", layout="wide")

# Sidebar for navigation with auto-switch
if 'tab' not in st.session_state:
    st.session_state['tab'] = "Home & Inputs"

tab_options = ["Home & Inputs", "Dataset Dashboard", "Recommendations", "About & Theory"]
tab = st.sidebar.radio("Navigate to:", tab_options, index=tab_options.index(st.session_state['tab']))

# Custom CSS for better UI (updated metrics color to a more visible blue with !important)
st.markdown("""
    <style>
    .main {background-color: #f5f5f5;}
    .stButton>button {background-color: #4CAF50; color: white; border-radius: 10px;}
    .stMetric {background-color: #2196F3 !important; color: white !important; padding: 15px; border-radius: 10px; border: 2px solid #0D47A1;}
    .stMetric label {color: white !important;}
    .stMetric div {color: white !important;}
    .sidebar .sidebar-content {background-color: #f0f0f0;}
    </style>
""", unsafe_allow_html=True)

if tab == "Home & Inputs":
    st.title("🏠 Smart Screen Time Recommendation System")
    st.markdown("**Welcome!** Enter your details to get personalized insights based on the Indian Kids ScreenTime dataset. This tool promotes healthy digital habits.")
    
    with st.form("user_form"):
        st.subheader("📝 Your Details")
        col1, col2 = st.columns(2)
        with col1:
            age = st.slider("Your Age:", 5, 60, 10, help="Select your age for tailored comparisons.")
            gender = st.selectbox("Gender:", ["Male", "Female"], help="Helps provide gender-specific advice.")
            screen_time = st.number_input("Average Daily Screen Time (hrs):", min_value=0.0, max_value=24.0, value=4.0, step=0.5, help="Total hours on devices daily.")
        with col2:
            study_time = st.number_input("Average Daily Study Time (hrs):", min_value=0.0, max_value=24.0, value=2.0, step=0.5, help="Time spent on learning activities.")
            sleep_time = st.number_input("Average Daily Sleep Time (hrs):", min_value=0.0, max_value=24.0, value=8.0, step=0.5, help="Hours of sleep per night.")
            physical_activity = st.selectbox("Do you exercise or play sports daily?", ["yes", "no"], help="Physical activity balances screen time.")
        
        submitted = st.form_submit_button("🚀 Analyze & Get Recommendations")
    
    if submitted:
        total_time = screen_time + study_time + sleep_time
        if total_time > 24:
            st.error("⚠️ Total time exceeds 24 hours! Please adjust your inputs.")
        elif screen_time < 0 or study_time < 0 or sleep_time < 0:
            st.error("⚠️ Inputs cannot be negative.")
        else:
            st.success("✅ Inputs validated! Switching to Recommendations...")
            st.session_state['user_data'] = {
                'age': age, 'gender': gender, 'screen_time': screen_time,
                'study_time': study_time, 'sleep_time': sleep_time, 'physical_activity': physical_activity
            }
            st.session_state['tab'] = "Recommendations"
            st.rerun()

elif tab == "Dataset Dashboard":
    st.title("📊 Dataset Characteristics Dashboard")
    st.markdown("Explore key insights from the Indian Kids ScreenTime dataset. Use filters for deeper analysis.")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        age_filter = st.multiselect("Filter by Age Group:", df_original['Age_Group'].unique(), default=df_original['Age_Group'].unique())
    with col2:
        gender_filter = st.multiselect("Filter by Gender:", df_original['Gender'].unique(), default=df_original['Gender'].unique())
    
    filtered_df = df_original[(df_original['Age_Group'].isin(age_filter)) & (df_original['Gender'].isin(gender_filter))]
    
    # Metrics (now using original values for accuracy, with updated styling)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", len(filtered_df))
    with col2:
        st.metric("Avg Screen Time", f"{filtered_df['Avg_Daily_Screen_Time_hr'].mean():.2f} hrs")
    with col3:
        st.metric("Age Range", f"{filtered_df['Age'].min()} - {filtered_df['Age'].max()}")
    with col4:
        if 'Health_Impacts' in df_original.columns and filtered_df['Health_Impacts'].notna().any():
            corr = filtered_df['Avg_Daily_Screen_Time_hr'].corr(filtered_df['Health_Impacts'])
            st.metric("Health Correlation", f"{corr:.2f}" if not np.isnan(corr) else "N/A")
        else:
            st.metric("Health Data", "N/A")
    
    # Interactive Visualizations with Plotly (using original df)
    st.subheader("📈 Interactive Charts")
    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.histogram(filtered_df, x='Avg_Daily_Screen_Time_hr', nbins=20, title="Screen Time Distribution", color_discrete_sequence=['skyblue'])
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        group_avg = filtered_df.groupby('Age_Group')['Avg_Daily_Screen_Time_hr'].mean().reset_index()
        fig2 = px.bar(group_avg, x='Age_Group', y='Avg_Daily_Screen_Time_hr', title="Avg Screen Time by Age Group", color='Age_Group')
        st.plotly_chart(fig2, use_container_width=True)
    
    if 'Health_Impacts' in df_original.columns and filtered_df['Health_Impacts'].notna().any():
        fig3 = px.scatter(filtered_df, x='Avg_Daily_Screen_Time_hr', y='Health_Impacts', title="Screen Time vs Health Impact", trendline="ols")
        st.plotly_chart(fig3, use_container_width=True)

elif tab == "Recommendations":
    st.title("📋 Personalized Recommendations & Visual Report")
    if 'user_data' not in st.session_state:
        st.warning("⚠️ Please submit your details in the Home tab first.")
    else:
        user = st.session_state['user_data']
        age, gender, screen_time, study_time, sleep_time, physical_activity = user['age'], user['gender'], user['screen_time'], user['study_time'], user['sleep_time'], user['physical_activity']
        
        # Progress bar for analysis
        progress_bar = st.progress(0)
        progress_bar.progress(25)
        
        # Compute analysis once and store (using original averages)
        if 'analysis' not in st.session_state:
            # Age/Gender averages (from original df)
            avg_age_screen = avg_by_age.get(age, avg_by_age.mean())  # Fallback to overall mean if exact age not found
            avg_gender_screen = avg_by_gender.get(gender, avg_screen_time)
            
            # Usage level
            usage_level = "Low" if screen_time < 3 else "Moderate" if screen_time <= 6 else "High"
            
            # Health
            if 'Health_Impacts' in df_original.columns and df_original['Health_Impacts'].notna().any():
                correlation = df_original['Avg_Daily_Screen_Time_hr'].corr(df_original['Health_Impacts'])
                base_message = "More screen time generally worsens health." if correlation > 0.3 else "Screen time and health have a weak correlation."
            else:
                base_message = "Using general wellness rules."
            
            health_risk = "⚠️ Very High Risk" if screen_time > 7 else "⚠️ High Risk" if screen_time > 5 else "🟡 Moderate Risk" if screen_time > 3 else "🟢 Low Risk"
            
            # Insights
            insights = []
            if sleep_time < 7: insights.append("😴 Aim for 7–9 hours of sleep.")
            else: insights.append("✅ Healthy sleep duration.")
            if study_time < 2: insights.append("📘 Increase study time to at least 3 hours.")
            else: insights.append("🧠 Balanced study schedule.")
            if physical_activity == "no": insights.append("🏃 Add 30 mins of daily exercise.")
            else: insights.append("💪 Great physical activity!")
            
            # Recommendations
            recs = []
            if usage_level == "High":
                recs = ["- Reduce screen time by 30–60 mins/week.", "- Use 'Digital Wellbeing' apps.", "- No screens 1 hour before bed."]
            elif usage_level == "Moderate":
                recs = ["- Take breaks (20-20-20 rule).", "- Use screens productively."]
            else:
                recs = ["- Maintain balance.", "- Replace with hobbies."]
            if gender == "Male": recs.append("- Balance gaming with offline fun.")
            elif gender == "Female": recs.append("- Ensure breaks from social media.")
            
            st.session_state['analysis'] = {
                'avg_age_screen': avg_age_screen, 'avg_gender_screen': avg_gender_screen,
                'usage_level': usage_level, 'base_message': base_message, 'health_risk': health_risk,
                'insights': insights, 'recs': recs
            }
        
        analysis = st.session_state['analysis']
        progress_bar.progress(50)
        
        # Display Results
        st.subheader("👤 Your Profile Summary")
        st.write(f"**Age:** {age} | **Gender:** {gender} | **Usage Level:** {analysis['usage_level']}")
        st.write(f"**Screen Time:** {screen_time} hrs/day (Avg Age: {analysis['avg_age_screen']:.2f}, Gender: {analysis['avg_gender_screen']:.2f})")
        
        st.subheader("🩺 Health Insights")
        st.write(analysis['base_message'])
        st.write(analysis['health_risk'])
        
        st.subheader("💡 Lifestyle Analysis")
        for insight in analysis['insights']: st.write(insight)
        
        st.subheader("🎯 Personalized Recommendations")
        for rec in analysis['recs']: st.write(rec)
        
        progress_bar.progress(75)
        
        # Visual Report with Expanders
        st.subheader("📊 Visual Report")
        with st.expander("Screen Time Comparison"):
            fig1, ax1 = plt.subplots(figsize=(5, 3))
            ax1.bar(['Your Screen', 'Healthy Limit'], [screen_time, 4], color=['tomato', 'green'])
            ax1.set_title("Screen Time vs Healthy Limit")
            st.pyplot(fig1)
            st.caption("Green bar is the 4-hour recommended limit.")
        
        with st.expander("Health Risk Breakdown"):
            health_impacts = {
                "Eye Strain": min(100, screen_time * 12),
                "Sleep Issues": min(100, screen_time * 10),
                "Reduced Focus": min(100, screen_time * 8),
                "Anxiety Risk": min(100, screen_time * 6),
                "Physical Inactivity": 0 if physical_activity == 'yes' else 80,
            }
            fig2 = px.bar(x=list(health_impacts.values()), y=list(health_impacts.keys()), orientation='h', title="Estimated Health Risks", color=list(health_impacts.keys()))
            st.plotly_chart(fig2, use_container_width=True)
        
        with st.expander("Daily Time Balance"):
            fig3 = go.Figure(data=[go.Pie(labels=['Screen', 'Study', 'Sleep', 'Other'], 
                                          values=[screen_time, study_time, sleep_time, 24 - (screen_time + study_time + sleep_time)],
                                          marker_colors=['red', 'blue', 'green', 'gray'])])
            fig3.update_layout(title="Daily Time Distribution")
            st.plotly_chart(fig3, use_container_width=True)
        
        progress_bar.progress(100)
        progress_bar.empty()
        
        # Export Options
        st.subheader("📤 Export Report")
        if st.button("Download Summary as Text"):
            summary = f"Profile: Age {age}, Gender {gender}, Screen {screen_time} hrs\nHealth: {analysis['health_risk']}\nRecs: {'; '.join(analysis['recs'])}"
            st.download_button("Download", summary, file_name="report.txt")

elif tab == "About & Theory":
    st.title("ℹ️ About the System & Theory")
    with st.expander("Theory of Recommendation Systems"):
        st.write("A recommendation system is a technique used to provide personalized suggestions by analyzing user data, preferences, and behavior. It helps users make better decisions by filtering relevant information using content-based, collaborative, or hybrid approaches.")
    
    with st.expander("Dataset Overview"):
        st.write(f"The dataset has {len(df_original)} records on screen habits, health, and demographics for balanced digital use.The dataset contains information about users such as age, gender, average daily screen time, and health impacts. The data is cleaned and preprocessed to ensure accuracy before analysis and recommendation generation.")
    
    with st.expander("Algorithm Explanation"):
        st.write("1. Collect user inputs.")
        st.write("2. Compare to dataset.")
        st.write("3. Classify and predict risks.")
        st.write(" 4. Generate recs with interactive visuals.")
                 
    
    with st.expander("Limitations & Future Scope"):
        st.write("Limitations: Potential data bias, privacy.")
        st.write("Future: Advanced AI, real-time apps, multi-language support.")
    
    st.write("Designed to support balanced screen usage through insightful data analysis and personalized recommendations.")
    st.write("presented by Yogesh Yadav - yogeshyadavyy8736659@gmail.com")
