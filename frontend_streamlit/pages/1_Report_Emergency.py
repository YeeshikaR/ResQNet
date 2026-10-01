import pandas as pd
import streamlit as st

from api_client import emergencies, report, resolve

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
    location_mode = st.radio('Location format', ['Address', 'GPS coordinates'], horizontal=True)
    if location_mode == 'Address':
        location = st.text_input('Street address or landmark', placeholder='Example: Times Square, New York')
    else:
        st.caption('Enter decimal degrees from a map app. Latitude is -90 to 90; longitude is -180 to 180.')
        latitude = st.number_input('Latitude', min_value=-90.0, max_value=90.0, value=0.0, format='%.6f')
        longitude = st.number_input('Longitude', min_value=-180.0, max_value=180.0, value=0.0, format='%.6f')
        location = f'{latitude},{longitude}'
    submitted = st.form_submit_button('Submit report')

if submitted:
    try:
        if not location.strip():
            st.error('Enter a location before submitting the report.')
            st.stop()
        result = report(token, {'type': emergency_type, 'severity': severity, 'people_affected': people, 'address': location})
        st.success(f"Report #{result['emergency_id']} created with priority {result['priority_score']:.0f}/100.")
    except Exception as error:
        st.error(str(error))

st.subheader('My emergency reports')
try:
    own_reports = emergencies(token)
    if own_reports:
        active_reports = [item for item in own_reports if item['status'] != 'resolved']
        completed_reports = [item for item in own_reports if item['status'] == 'resolved']
        summary_columns = st.columns(3)
        summary_columns[0].metric('Total reports', len(own_reports))
        summary_columns[1].metric('Active', len(active_reports))
        summary_columns[2].metric('Completed', len(completed_reports))

        if active_reports:
            st.caption('Reported = waiting for an operator. Assigned = a resource is on the task.')
            active_table = pd.DataFrame(active_reports)
            st.dataframe(
                active_table[[
                    'emergency_id', 'type', 'severity', 'status', 'priority_score',
                    'assigned_resource_name', 'assigned_resource_type',
                    'assigned_resource_status',
                ]],
                use_container_width=True,
                hide_index=True,
            )
        if completed_reports:
            st.caption('Completed reports are kept as history. Their assigned resource is available again.')
            completed_table = pd.DataFrame(completed_reports)
            st.dataframe(
                completed_table[[
                    'emergency_id', 'type', 'severity', 'status', 'priority_score',
                    'assigned_resource_name', 'assigned_resource_type',
                    'assigned_resource_status',
                ]],
                use_container_width=True,
                hide_index=True,
            )
        assigned = [item for item in own_reports if item['status'] == 'assigned']
        if assigned:
            selected = st.selectbox('Task to mark complete', [item['emergency_id'] for item in assigned])
            st.caption('Marking the task complete changes the emergency to resolved and frees its resource.')
            if st.button('Mark my emergency complete'):
                st.success(resolve(token, selected))
                st.rerun()
        else:
            st.caption('You can mark an emergency complete after an operator assigns a resource.')
    else:
        st.info('No emergency reports yet.')
except Exception as error:
    st.error(str(error))
