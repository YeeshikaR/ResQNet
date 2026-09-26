import pandas as pd
import streamlit as st

from api_client import dispatch, dispatches, emergencies, map_url, resolve

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
        st.dataframe(pd.DataFrame(active), use_container_width=True, hide_index=True)
        selected = st.selectbox('Emergency to dispatch', [item['emergency_id'] for item in active])
        col1, col2 = st.columns(2)
        with col1:
            if st.button('Dispatch best resource'):
                st.success(dispatch(token, selected))
                st.rerun()
        with col2:
            if st.button('Mark resolved'):
                st.success(resolve(token, selected))
                st.rerun()
    else:
        st.info('No active emergencies.')
    image_url = map_url(token)
    if image_url:
        st.image(image_url, caption='Emergency and resource locations')
    st.subheader('Dispatch history')
    history = dispatches(token)
    if history:
        st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)
except Exception as error:
    st.error(str(error))
