import streamlit as st

st.markdown("""<style>body {
        zoom: 1.0;   /* 110% zoom */
    }</style>""", unsafe_allow_html=True)

# Navigation
nav = st.navigation([
    st.Page("HOME.py", title=''' 🏠 Home'''),
    st.Page("RECOMMENDATIONS.py", title=" ⚙️ Screen Time Advisor"),
    st.Page("DASHBOARD.py",title="📄 Dashboard"),
    st.Page("FEEDBACK.py", title="🌟 Feedback"),
])

# Run selected page
nav.run()

