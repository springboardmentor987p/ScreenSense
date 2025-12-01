import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Screen-Time Dashboard",layout="wide")

with st.container(gap=None):
    st.title(":rainbow[Indian Kids Screen Time Insights Dashboard]")
    st.divider()

st.subheader(''':orange[“Navigate the Power BI report for detailed trends and patterns”]''',divider='orange',width='content')
st.info("This dashboard is interactive — use filters, buttons, and drill-through options inside the dashboard.",width=700)
with st.container(border=True):
    components.html("""<iframe 
        src="https://app.powerbi.com/view?r=eyJrIjoiMDEzYjMwNmItY2Y5Ni00NjU4LThjNzctYmExODIyMDI4NzNhIiwidCI6ImE2ZTczYTQ5LWI2YjItNGY3Yi04ZDNiLTE3ZWQ1ZTg3ZDdhZSJ9"
        width="100%" 
        height="800px"
        style="border:none;"
        allowfullscreen="true">
    </iframe>""",height=550,)

st.subheader(':green[Care to give us your feedback,Click the Button Below]',divider='rainbow',width='content')
with st.container(border=True,width=220):
    st.page_link("FEEDBACK.py", label='''🌟 :yellow[Go to Feedback Page]''')

st.markdown("---")
with st.container(gap='small'):
    st.caption('''© 2025 Screen-Time Advisor • Designed for "digital wellness" • Dashboard created using Microsoft Power BI''')
    

