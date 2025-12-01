import streamlit as st
import requests
import time
st.set_page_config(page_title="Screen-Time Advisor",layout="wide")

with st.container(gap=None): 
    st.title(':rainbow[Welcome To The Screen Time Advisor]')
    st.divider()

# INTRO
st.subheader(":orange[Into The Tool !!!]",divider='rainbow',width='content')
with st.container(gap=None,border=True):
    st.markdown("""**The Screen Time Advisor helps you analyze your child's digital habits using real data.Simply provide a few details, and you'll receive a :yellow[personalized screen-time assessment]
    health insights, and recommendations tailored to your child's age and device usage.**""")
st.markdown("")

# INSTRUCTIONS 
st.subheader(":orange[How to Use This Tool]",divider='rainbow',width='content')
with st.container(border=True):
    st.write("""
    **Follow these simple steps to get your personalized screen-time analysis:**
    1. **Enter your child's age** (between 8–18 years).  
    2. **Select your child's gender**.  
    3. **Choose the primary device** your child uses (Smartphone, Laptop, Tablet, or TV).  
    4. **Enter the daily educational screen time** (in hours).  
    5. **Enter the daily recreational screen time** (in hours).  
    6. Click :green[**Generate Report**] to get detailed insights based on real user data.
    """)

#WIDGETS
st.header(":rainbow[Enter Your Child's Screen Time Details]",divider='rainbow',width='content')

with st.container(border=True):

    #AGE WIDGET 
    age = st.slider("Select Age", min_value=8, max_value=18, value=12)

    #GENDER PILLS WIDGET 
    gender = st.pills("Select Gender",
        options=["Male", "Female"],
        selection_mode="single")

    #DEVICE PILLS WIDGET
    device = st.pills("Primary Device Used",
        options=["Smartphone", "Laptop", "TV", "Tablet"],
        selection_mode="single")

    # EDUCATIONAL SCREEN TIME WIDGET
    edu_time = st.number_input("Educational Screen Time (in hours)",
        min_value=0.0, max_value=16.0, step=0.25)

    #RECREATIONAL SCREEN TIME WIDGET
    rec_time = st.number_input("Recreational Screen Time (in hours)",
        min_value=0.0, max_value=16.0, step=0.25)


#API CALLING
inputs={"age":age,
        "gender":gender,
        "device":device,
        "edu_time":edu_time,
        "rec_time":rec_time}

url='http://127.0.0.1:8000'
def get_recommendations(payload):
    apiendpoint=f'{url}/Recommendations'
    response=requests.post(apiendpoint,json=payload)
    return response

if st.button(":green[Generate Report]"):
    spinner=st.spinner("Generating Personalised Report...",show_time=True)
    with spinner:
        time.sleep(3)

        res = get_recommendations(inputs)
        
        if res.status_code == 200:
            result_list = res.json()["Result"]   # list of strings
            with st.container(gap='small',border=True):
                # Section header
                st.subheader(":orange[Your Child's Detailed Report :]",divider='orange',width='content')

                # Clean rendering loop
                for line in result_list:
                    if line.startswith("Entered") or line.startswith("Total"):
                        st.markdown(f'**{line}**')
                    elif 'exceeded' in line:
                            st.markdown(f'**:red[{line}]**')
                    elif 'within' in line:
                            st.markdown(f'**:green[{line}]**')
                    elif 'overall' in line and 'above' in line:
                           st.markdown(f'**:red[{line}]**')
                    elif 'overall' in line and 'below' in line:
                           st.markdown(f'**:green[{line}]**') 
                    elif 'aged' in line and 'above' in line:
                         st.markdown(f'**:red[{line}]**')
                    elif 'aged' in line and 'below' in line:
                        st.markdown(f'**:green[{line}]**')   
                    elif 'educational screen time' in line and 'above' in line:
                         st.markdown(f'**:orange[{line}]**')     
                    elif 'educational screen time' in line and 'below' in line:
                         st.markdown(f'**:green[{line}]**') 
                    elif 'recreational screen time' in line and 'above' in line:
                         st.markdown(f'**:red[{line}]**')     
                    elif 'recreational screen time' in line and 'below' in line:
                         st.markdown(f'**:green[{line}]**')
                    elif 'Educational to Recreational ratio' in line:
                         st.markdown(f'**:yellow[{line}]**') 
                    elif 'spend more' in line and 'educational activities' in line:
                         st.markdown(f'**:green[{line}]**')
                    elif 'higher' in line and 'recreational usage' in line:
                         st.markdown(f'**:green[{line}]**')           
                    elif 'Most common health impacts' in line:
                         st.markdown(f'**:orange[{line}]**')
                    elif 'spend more' in line and 'educational activities' in line:
                         st.markdown(f'**:green[{line}]**')
                    elif ('Exceeding limit' in line) and ('Poor Sleep' in line or 'Eye Strain' in line or 'Anxiety'in line or 'Obesity Risk' in line):     
                         st.markdown(f'**:red[{line}]**')
                    elif ('Poor Sleep' in line) or ('Eye Strain' in line) or ('Anxiety'in line) or ('Obesity Risk' in line):     
                         st.markdown(f'**:orange[{line}]**')
                    elif "Risk Level Assessment : Healthy(No Risk)" in line:
                         st.markdown(f'**:green-badge[{line}]**')
                    elif "Risk Level Assessment : Mild Risk"in line:
                         st.markdown(f'**:yellow-badge[{line}]**')
                    elif "Risk Level Assessment : High Risk"in line:
                        st.markdown(f'**:orange-badge[{line}]**')
                    elif "Risk Level Assessment : Severe Risk" in line:
                        st.markdown(f'**:red-badge[{line}]**',width='stretch')
                    else:
                        st.markdown(f':green[{line}]')    
                st.divider()
                # DOWNLOAD BUTTON IF REPORT EXISTS
                report_text = "\n".join(result_list)
                st.download_button(label='Download Screen Assessment Report',type='primary',data=report_text,file_name="screen_time_report.txt",mime="text/plain")
                st.markdown("")
                st.info("Note : This report is generated using data model and community-based averages, not proper medical evaluation. " 
                        "Consult a doctor for professional health advice.")
     
        else:
            st.error(f"Backend error: {res.status_code}")
            st.write(res.text)

st.subheader(':green[Want To See a Detailed Screen Time Dashboard,Click the Button Below]',divider='rainbow',width='content')
with st.container(border=True,width=190):
    st.page_link("DASHBOARD.py", label='''📄 :yellow[Go to Dashboard]''')


# Optional footer
st.markdown("---")
with st.container(gap='small'):
    st.caption('''© 2025 Screen-Time Advisor • Designed for "digital wellness"''')
    st.caption('''This analysis is generated using insights from the "Indian Kids Screentime 2025" Dataset''')
    with st.container(border=True,width=250,gap=None):    
        st.page_link('https://www.kaggle.com/datasets/ankushpanday2/indian-kids-screentime-2025',label=':grey[Click to go to the dataset used]',width='content')

