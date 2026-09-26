import streamlit as st

from api_client import login, register

st.set_page_config(page_title='ResQNet', page_icon='R', layout='wide')

if 'token' not in st.session_state:
    st.session_state.token = None
if 'role' not in st.session_state:
    st.session_state.role = None

st.title('ResQNet')
st.caption('Emergency reporting and response coordination')

if st.session_state.token:
    st.success(f"Signed in as {st.session_state.role}. Use the pages in the sidebar to continue.")
    if st.button('Sign out'):
        st.session_state.clear()
        st.rerun()
else:
    login_tab, register_tab = st.tabs(['Sign in', 'Create account'])
    with login_tab:
        with st.form('login'):
            email = st.text_input('Email')
            password = st.text_input('Password', type='password')
            submitted = st.form_submit_button('Sign in')
        if submitted:
            try:
                result = login(email, password)
                st.session_state.token = result['access_token']
                st.session_state.role = result['role']
                st.success('Signed in. Open a page from the sidebar.')
                st.rerun()
            except Exception as error:
                st.error(str(error))
    with register_tab:
        with st.form('register'):
            name = st.text_input('Name')
            email = st.text_input('Registration email')
            password = st.text_input('Registration password', type='password')
            st.caption('Password must be 8 to 128 characters long.')
            submitted = st.form_submit_button('Create account')
        if submitted:
            try:
                register(name, email, password)
                st.success('Account created. Sign in from the first tab.')
            except Exception as error:
                st.error(str(error))
