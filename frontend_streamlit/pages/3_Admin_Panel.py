import pandas as pd
import streamlit as st

from api_client import add_resource, release_resource, resources

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
    location_mode = st.radio('Location format', ['Address', 'GPS coordinates'], horizontal=True)
    if location_mode == 'Address':
        address = st.text_input('Resource address', placeholder='Example: Central Fire Station, Mumbai')
        resource_location = {'address': address}
    else:
        latitude = st.number_input('Latitude', min_value=-90.0, max_value=90.0, value=0.0, format='%.6f')
        longitude = st.number_input('Longitude', min_value=-180.0, max_value=180.0, value=0.0, format='%.6f')
        resource_location = {'latitude': latitude, 'longitude': longitude}
    submitted = st.form_submit_button('Add resource')
if submitted:
    try:
        add_resource(token, {'type': resource_type, 'name': name, **resource_location})
        st.success('Resource added.')
        st.rerun()
    except Exception as error:
        st.error(str(error))

try:
    data = resources(token)
    available = [item for item in data if item['status'] == 'available']
    status_columns = st.columns(3)
    status_columns[0].metric('Total resources', len(data))
    status_columns[1].metric('Available', len(available))
    status_columns[2].metric('Dispatched', len(data) - len(available))
    st.caption('Available resources can be assigned. Dispatched resources are currently busy.')
    st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    dispatched = [item for item in data if item['status'] == 'dispatched']
    if dispatched:
        st.subheader('Release a resource')
        selected_resource = st.selectbox(
            'Dispatched resource',
            [item['resource_id'] for item in dispatched],
            format_func=lambda resource_id: next(
                f"{item['name']} ({item['type']})"
                for item in dispatched
                if item['resource_id'] == resource_id
            ),
        )
        st.caption('Releasing also completes its assigned emergency.')
        if st.button('Release resource'):
            release_resource(token, selected_resource)
            st.success('Resource is available again.')
            st.rerun()
except Exception as error:
    st.error(str(error))
