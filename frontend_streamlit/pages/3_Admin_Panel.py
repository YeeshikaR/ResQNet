import pandas as pd
import streamlit as st

from api_client import add_resource, resources

st.title('Resource administration')
token = st.session_state.get('token')
if not token:
    st.warning('Sign in from the home page first.')
    st.stop()

if st.session_state.get('role') != 'admin':
    st.error('Administrator access required.')
    st.stop()

with st.form('resource_form'):
    resource_type = st.selectbox('Resource type', ['ambulance', 'fire_truck'])
    name = st.text_input('Resource name')
    latitude = st.number_input('Latitude', min_value=-90.0, max_value=90.0, format='%.6f')
    longitude = st.number_input('Longitude', min_value=-180.0, max_value=180.0, format='%.6f')
    submitted = st.form_submit_button('Add resource')
if submitted:
    try:
        add_resource(token, {'type': resource_type, 'name': name, 'latitude': latitude, 'longitude': longitude})
        st.success('Resource added.')
        st.rerun()
    except Exception as error:
        st.error(str(error))

try:
    data = resources(token)
    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
except Exception as error:
    st.error(str(error))
