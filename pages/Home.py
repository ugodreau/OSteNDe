import streamlit as st
from utils.misc import iso639_to_name
import pandas as pd
from random import randint

st.title('Welcome to OpenStemmata')
st.set_page_config(
layout="wide"
)

st.sidebar.page_link('pages/Home.py', label='Home')
st.sidebar.page_link('pages/Search.py', label='Search')
st.sidebar.page_link('pages/Browse.py', label='Browse')
st.sidebar.page_link('pages/Contribute.py', label='Contribute')

database = st.session_state['database']
stats = st.session_state['global_stats']
file_dict = st.session_state["file_dict"]

col_intro_1, col_intro_2 = st.columns(2)

im_cont = col_intro_1.container(border=False, height=400)
random_index = randint(0, len(database.index))
random_entry = database.loc[random_index]
path = random_entry['submissionPath']
try:
    orig_img = file_dict[f"{path}/stemma.png"]
    im_cont.image(orig_img, width="content")
except:
    im_cont.warning('No available picture of the stemma')

if col_intro_1.button("What is this stemma ?", key='rnd_button'):
    st.session_state['stemma_to_display'] = database.loc[random_index]
    st.switch_page('pages/Display_record.py')

col_intro_2.markdown(
f"""

## Who are we ?

*Open Stemmata* is an organisation aiming at creating an open source database of manuscript textual genealogies (i.e. _stemmata_), created in 2020. Currently, OpenStemmata gathers
**{stats['Number of stemmata']}** stemmata in **{len(stats["Stemmata by language"])}** languages. The backend of the database is a GitHub [repository](https://github.com/OpenStemmata/database),
gathering data in the form of XML-TEI headers and GraphML records of tree structures. 
The goal of the present application is to provide a searchable, user-friendly interface to OpenStemmata, please check our official [website](https://openstemmata.github.io/index.html).
"""
)

col1,col2 = st.columns(2)
lang_data = st.session_state['global_stats']['Stemmata by language']
lang_df = pd.DataFrame({iso639_to_name(l):n for l,n in lang_data.items()}, index=["Number of stemmata"]).transpose()

col1.subheader("Number of stemmata per language")
col1.table(lang_df.sort_values("Number of stemmata", ascending=False))


wit_nb_dict = st.session_state['global_stats']['Witness number distribution']
wit_nb_x, wit_nb_y = list(wit_nb_dict.keys()), list(wit_nb_dict.values())
wit_nb_df = pd.DataFrame({'Witness number':wit_nb_x,'Work number':wit_nb_y})

col2.subheader("Number of witnesses per stemma")
col2.bar_chart(wit_nb_df, x='Witness number', y=['Work number'])