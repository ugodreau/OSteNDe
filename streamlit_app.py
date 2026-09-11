import streamlit as st
import pandas as pd
import get_data
import utils as u

# session state data_warnings gather all failed imports from OpenStemmata

if 'initialized' not in st.session_state:
    st.session_state['data_warnings'] = []
    st.session_state['missing_witnesses'] = []

with st.spinner(text="Importing data from GitHub..."):
    file_dict = get_data.get_database_content()

st.session_state['file_dict'] = file_dict

with st.spinner(text="Generating database..."):
    database = get_data.create_database()

st.session_state['database'] = database
st.session_state.initialized  = True

global_stats = get_data.compute_global_stats()

st.session_state['global_stats'] = global_stats

home = st.Page('pages/Home.py', title='Home')
search = st.Page('pages/Search.py', title='Search OpenStemmata')
browse = st.Page('pages/Browse.py', title='Browse')
display_entry  = st.Page('pages/Display_record.py', title="Stemma")
contribute  = st.Page('pages/Contribute.py', title="Contribute")

pg = st.navigation([home, search, browse, display_entry, contribute])
pg.run()