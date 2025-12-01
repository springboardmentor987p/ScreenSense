import streamlit as st

st.set_page_config(page_title="Home",layout="wide")

st.title(':orange[IND]I:green[AN] :rainbow[KIDS SCREEN TIME ANALYSIS]',width='stretch')
st.markdown("")

#EDUCATIONAL SECTION
st.subheader(":orange[Why Screen Time Matters In One's Life]",divider='rainbow',width='content')
with st.container(border=True):
    st.markdown("""
    **Screen time** plays a major role in children's daily lives. From completing homework to watching videos 
    and staying connected with friends, digital devices can support creativity, communication, and learning.

    However, :red[**too much screen time**] —especially recreational use—can affect sleep, mood, focus, posture, and overall well-being.  
    
    Finding the :green[**right balance**] is key to promoting healthy habits while still enjoying the benefits of technology.""")
    #FULL ARTICLE LINK
    st.markdown("**Interested in understanding healthy screen habits?**")
    st.link_button(':yellow[Click to read the Full Article]',url='https://en.wikipedia.org/wiki/Screen_time',icon='📜')
st.markdown("")

#PROJECT INTRO SECTION
st.subheader(":orange[Welcome the Screen Time Advisor]",divider='rainbow',width='content')
with st.container(border=True):
    st.write("""**The :yellow[Screen Time Advisor] helps analyze children's digital habits and provides
    :yellow[personalized recommendations] based on their age, gender, device usage, educational time,
    and recreational screen time.**""")
    st.write("""**A simple,:yellow[data science-backed tool] designed to help parents understand and improve their child's 
    screen-time habits. Our goal is to make digital wellness easy, clear, and personalized.**""")
st.markdown("")

#ABOUT PROJECT SECTION
st.subheader(":green[Into The Project]",divider='rainbow',width='content')
with st.container(border=True):
    st.write("""
    This tool uses real-world data to analyze your child's screen-time patterns and compares them with children 
    of similar **age**, **gender**, and **device usage**.  
    In just a few seconds, you’ll receive:
    - Personalized recommendations  
    - Health impact insights  
    - Risk level classification  
    - Device suitability guidance  
    - A detailed full analysis report  
    
    All designed to help you make informed decisions about your child's digital habits.\n
    :violet[“Understanding your child’s digital world starts with awareness”] """)
st.markdown("")

# CALL TO NAVIGATE
st.subheader(":green[Want Personalised Recommendations For Your Kid ? :family_man_woman_boy:]",divider='rainbow',width='content')
with st.container(border=True,width=310):
    st.page_link('RECOMMENDATIONS.py',label=" ⚙️ :yellow[Press to Go to Screen Time Advisor]",)



# Optional footer
st.markdown("---")
st.caption('''© 2025 Screen-Time Advisor • Designed for "digital wellness"''')
