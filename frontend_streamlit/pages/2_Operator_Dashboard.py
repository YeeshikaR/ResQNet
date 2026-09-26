import pandas as pd
import streamlit as st

from api_client import dispatch, dispatches, emergencies, map_url, resources, resolve

st.title('Operator dashboard')
token = st.session_state.get('token')
if not token:
    st.warning('Sign in from the home page first.')
    st.stop()

if st.session_state.get('role') not in {'operator', 'admin'}:
    st.error('Operator access required.')
    st.stop()

try:
    active = emergencies(token)
    st.metric('Active emergencies', len(active))
    if active:
        display_columns = {
            'emergency_id': 'Emergency',
            'reported_by_name': 'Reported by',
            'type': 'Type',
            'severity': 'Severity',
            'people_affected': 'People',
            'priority_score': 'Priority',
            'status': 'Status',
            'assigned_resource_name': 'Assigned resource',
            'assigned_resource_type': 'Resource type',
            'assigned_resource_status': 'Resource status',
            'distance_km': 'Distance (km)',
            'latitude': 'Latitude',
            'longitude': 'Longitude',
        }
        table = pd.DataFrame(active).rename(columns=display_columns)
        st.dataframe(
            table[[column for column in display_columns.values() if column in table]],
            use_container_width=True,
            hide_index=True,
        )
        selected = st.selectbox('Emergency to dispatch', [item['emergency_id'] for item in active])
        selected_item = next(item for item in active if item['emergency_id'] == selected)
        col1, col2 = st.columns(2)
        with col1:
            if st.button('Dispatch best resource'):
                st.success(dispatch(token, selected))
                st.rerun()
        with col2:
            if st.button('Complete task', disabled=selected_item['status'] != 'assigned'):
                st.success(resolve(token, selected))
                st.rerun()
        if selected_item['status'] != 'assigned':
            st.caption('Dispatch this emergency before completing the task.')
    else:
        st.info('No active emergencies.')
    image_url = map_url(token)
    if image_url:
        st.image(image_url, caption='Emergency and resource locations')
    else:
        locations = [
            {'latitude': item['latitude'], 'longitude': item['longitude']}
            for item in active
        ]
        locations.extend(
            {'latitude': item['latitude'], 'longitude': item['longitude']}
            for item in resources(token)
        )
        if locations:
            st.map(pd.DataFrame(locations), latitude='latitude', longitude='longitude', size=80)
        else:
            st.info('Add resources or report an emergency to populate the map.')
    st.subheader('Dispatch history')
    history = dispatches(token)
    if history:
        st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)
except Exception as error:
    st.error(str(error))
