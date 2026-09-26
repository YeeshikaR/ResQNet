import streamlit as st

from api_client import report

st.title('Report an emergency')
token = st.session_state.get('token')
if not token:
    st.warning('Sign in from the home page first.')
    st.stop()

if st.session_state.get('role') != 'citizen':
    st.info('Emergency reporting is available to citizen accounts.')
    st.stop()

with st.form('emergency_form'):
    emergency_type = st.selectbox('Emergency type', ['fire', 'medical', 'accident'])
    severity = st.select_slider('Severity', options=['low', 'medium', 'high', 'critical'], value='medium')
    people = st.number_input('People affected', min_value=1, max_value=10000, value=1)
    address = st.text_input('Address or coordinates', placeholder='Example: 40.7128,-74.0060')
    submitted = st.form_submit_button('Submit report')

if submitted:
    try:
        result = report(token, {'type': emergency_type, 'severity': severity, 'people_affected': people, 'address': address})
        st.success(f"Report #{result['emergency_id']} created with priority {result['priority_score']:.0f}/100.")
    except Exception as error:
        st.error(str(error))
