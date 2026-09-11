import streamlit as st
from unidecode import unidecode
import pandas as pd
from functools import reduce
import time
from utils.misc import convert_dates
import altair as alt
from utils.misc import iso639_to_name


@st.cache_data(ttl=3600) 
def get_browse_data(db):
    tl_items = []
    for i, row in db.iterrows():
        date = row['workOrigDate']
        date = date if date not in [' ', float('nan'), None, ''] else 'unknown'
        date = date.replace('c.', '')
        date = date.replace('?', '')
        date = date.replace('AD', '')
        date = date.replace('ca.', '')
        date = date.replace(' ', '')
        date = convert_dates(date)
        match date:
            case 'unknown':
                continue
            case (start, end):
                midyear = (start+end)/2
            case y:
                midyear = y
        
        tl_items.append({"id": i, 
            "midyear":midyear, 
            "datation":row['workOrigDate'], 
            "title":row['workTitle'], 
            "author":row['workAuthor'],
            "genre":row['workGenre'],
            "language":iso639_to_name(row['workLangCode'])})
        

    return pd.DataFrame(tl_items)


def display_browse_results(database, filtered, result_container):
    for _,row in filtered.iterrows():
        
        cc = result_container.container(gap=None)
        col1, col2, col3, col4 = cc.columns([3,3,2,1])

        col1.markdown(f"**{row['title'].lstrip()}**")
        if not pd.isna(row['author']):
            col2.markdown(f"_{row['author']}_")
        else:
            col2.markdown(f"_unknown_")
        col3.markdown(f"{row['datation']}")
        if col4.button("details", key=row['id']):
            st.session_state['stemma_to_display'] = database.loc[row['id']]
            st.switch_page('pages/Display_record.py')
        cc.divider()


database = st.session_state['database']
df = get_browse_data(database)


st.title('Browse')
st.set_page_config(
layout="wide"
)

st.sidebar.page_link('pages/Home.py', label='Home')
st.sidebar.page_link('pages/Search.py', label='Search')
st.sidebar.page_link('pages/Browse.py', label='Browse')
st.sidebar.page_link('pages/Contribute.py', label='Contribute')

st.header('By work date')

st.markdown('Select a window on the timeline')
# render timeline

brush = alt.selection_interval(encodings=["x"], name="year_brush")
zoom = alt.selection_interval(bind="scales", encodings=["x"], translate=False, name="zoom")

chart = (
    alt.Chart(df)
    .mark_tick(thickness=2, size=100)
    .encode(
        x=alt.X("midyear:Q", scale=alt.Scale(domain=[-2000, 2000]), title="Year"),
        color=alt.condition(brush, alt.value("steelblue"), alt.value("lightgray")),
        tooltip=["midyear", "title"],
    )
    .add_params(brush, zoom)
    .properties(height=200)
)

event = st.altair_chart(chart, use_container_width=True, on_select="rerun", key="brush_chart")
brushed = event["selection"].get("year_brush", {}).get("midyear")
year_min, year_max = brushed if brushed else (0, 0)
filtered_time = df[df["midyear"].between(year_min, year_max)].sort_values("midyear")

if len(filtered_time) > 0:
    st.markdown("""
    <style>
    .st-key-scrollbox_time {
        max-height: 500px;   /* the limit */
        overflow-y: auto;    /* scroll once content exceeds it */
        border: 1px solid rgba(49, 51, 63, 0.2);
        border-radius: 0.5rem;
        padding: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

    results_container_time = st.container(key="scrollbox_time", border=True)
    display_browse_results(database, filtered_time, results_container_time)

st.header("By genre")

genres = set(df['genre'].tolist())
selected_genre = st.multiselect(
    "Work genre",
    options=genres,
    default=[],
)
filtered_genre = df[df["genre"].isin(selected_genre)]

if len(filtered_genre) >0:
    st.markdown("""
    <style>
    .st-key-scrollbox_genre {
        max-height: 500px;   /* the limit */
        overflow-y: auto;    /* scroll once content exceeds it */
        border: 1px solid rgba(49, 51, 63, 0.2);
        border-radius: 0.5rem;
        padding: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    results_container_genre = st.container(key="scrollbox_genre", border=True)
    display_browse_results(database, filtered_genre, results_container_genre)

st.header("By language")

languages = set(df['language'].tolist())
selected_languages = st.multiselect(
    "Work language",
    options=languages,
    default=[],
)
filtered_languages = df[df["language"].isin(selected_languages)]

if len(filtered_languages) >0:
    st.markdown("""
    <style>
    .st-key-scrollbox_lang {
        max-height: 500px;   /* the limit */
        overflow-y: auto;    /* scroll once content exceeds it */
        border: 1px solid rgba(49, 51, 63, 0.2);
        border-radius: 0.5rem;
        padding: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    results_container_language = st.container(key="scrollbox_lang", border=True)
    display_browse_results(database, filtered_languages, results_container_language)
