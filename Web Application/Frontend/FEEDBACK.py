import streamlit as st

st.header(':violet[How Was Your Experience ?]',divider='violet',width='content')
st.write('''**:yellow[“Your feedback helps us improve the Screen Time Advisor tool and deliver better insights.This form takes less than 30 seconds.”]**''')
with st.container(gap='medium',border=True):
    sentiment_mapping = ["1", "2", "3", "4", "5"]
    st.write(':yellow[**“ How Would You Rate This Tool ? ”**]')
    selected = st.feedback("stars")
    if selected is not None:
        st.markdown(f"You selected {sentiment_mapping[selected]} star(s).")
    comment = st.text_area(''':yellow[**" Anything you'd like to share or suggest ? "**]''')
    if st.button(':violet[Submit Your Feedback !]'):
        st.toast('😍 Thank You ! for your valuable feedback')
       