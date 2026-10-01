import pandas as pd
import streamlit as st

from api_client import dispatch, dispatches, emergency_resources, emergencies, map_url, resources, resolve

st.title('Operator dashboard')
token = st.session_state.get('token')
if not token:
    st.warning('Sign in from the home page first.')
    st.stop()

if st.session_state.get('role') != 'operator':
    st.error('Operator access required.')
    st.stop()

try:
    all_resources = resources(token)
    available_resources = [item for item in all_resources if item['status'] == 'available']
    availability_columns = st.columns(4)
    availability_columns[0].metric('Total resources', len(all_resources))
    availability_columns[1].metric('Available', len(available_resources))
    availability_columns[2].metric('Dispatched', len(all_resources) - len(available_resources))
    availability_columns[3].metric('Ambulances', sum(item['type'] == 'ambulance' for item in all_resources))
    st.caption('Available means ready for a new task. Dispatched means currently assigned.')
    if all_resources:
        resource_table = pd.DataFrame(all_resources).rename(
            columns={'resource_id': 'Resource', 'type': 'Type', 'name': 'Name', 'status': 'Status'}
        )
        st.dataframe(resource_table[['Resource', 'Name', 'Type', 'Status']], use_container_width=True, hide_index=True)

    active = emergencies(token)
    st.metric('Active emergencies', len(active))
    if active:
        highest_priority = active[0]
        st.info(
            f"Priority order is highest first. Emergency #{highest_priority['emergency_id']} "
            f"is currently most important ({highest_priority['priority_score']:.0f}/100)."
        )
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
        selected_resource_id = None
        if selected_item['status'] == 'reported':
            candidates = emergency_resources(token, selected)
            if candidates:
                st.subheader('Available resources')
                candidate_table = pd.DataFrame(candidates)
                candidate_table['distance_km'] = candidate_table['distance_km'].round(2)
                st.dataframe(
                    candidate_table[['resource_id', 'name', 'type', 'distance_km']].rename(
                        columns={'distance_km': 'Distance (km)'}
                    ),
                    use_container_width=True,
                    hide_index=True,
                )
                st.caption(f"Best match: {candidates[0]['name']} ({candidates[0]['distance_km']:.2f} km away)")
                selected_resource_id = st.selectbox(
                    'Resource to dispatch',
                    [item['resource_id'] for item in candidates],
                    format_func=lambda resource_id: next(
                        f"{item['name']} - {item['distance_km']:.2f} km"
                        for item in candidates
                        if item['resource_id'] == resource_id
                    ),
                )
            else:
                required_type = 'fire truck' if selected_item['type'] == 'fire' else 'ambulance'
                available_types = sorted({item['type'] for item in available_resources})
                available_label = ', '.join(available_types) if available_types else 'none'
                st.warning(
                    f"This {selected_item['type']} emergency requires a {required_type}. "
                    f'Available resource types right now: {available_label}. '
                    'Add or release a compatible resource before dispatching.'
                )
        col1, col2 = st.columns(2)
        with col1:
            if st.button('Dispatch selected resource', disabled=selected_item['status'] != 'reported' or selected_resource_id is None):
                st.success(dispatch(token, selected, selected_resource_id))
                st.rerun()
        with col2:
            if st.button('Complete task and free resource', disabled=selected_item['status'] != 'assigned'):
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
            for item in all_resources
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
