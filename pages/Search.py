import streamlit as st
from unidecode import unidecode
import pandas as pd
from functools import reduce
import time

# Fields where search queries are applied
SEARCHABLE_FIELDS = [
    'workTitle',
    'workAuthors',
    'workGenre',
    'workLangCode',
    'publicationTitle',
    'publicationPlaces',
    'publicationAuthors',
    'workOrigPlace',
    'contributors']

def search_format(text):
    return unidecode(text).lower()


# Cannot be cached due to Streamlit bug (see streamlit issue #10957)
def searchable_database(db):
    """
    Makes the metadata database searchable by concatenating list fields
    and applying lowercase and unicode to ascii to all text fields
    """

    sdb = pd.DataFrame(db)
    f1 = lambda x:';'.join([c['contributor'] for c in x])
    sdb['contributors'] = db['contributors'].map(f1)

    f2 = lambda x:';'.join([c['publicationPlace'] for c in x])
    sdb['publicationPlaces'] = db['publicationPlaces'].map(f2)

    f3 = lambda x:';'.join([c['publicationAuthor'] for c in x])
    sdb['publicationAuthors'] = db['publicationAuthors'].map(f3)

    f4 = lambda x:';'.join([c['workAuthor'] for c in x])
    sdb['workAuthors'] = db['workAuthors'].map(f4)

    sdb[SEARCHABLE_FIELDS] = sdb[SEARCHABLE_FIELDS].map(search_format)

    return sdb


def search_match(s_query, s_db):
    """
    Returns all database index values matching query among SEARCHABLE_FIELDS

    Parameters
    ----------
    s_query : str
        String to be searched in database.
        Should be preformatted by search_format to make it case and
        diacritics-insensitive
    s_db : pandas.DataFrame
        Database to be searched
        Should contains at least SEARCHABLE_FIELDS and be preformatted
        using searchable_database (idem as s_query)

    Returns
    -------
    array
        dataframe indices matching search query
    """
    filters = [s_db[field].str.contains(s_query) for field in SEARCHABLE_FIELDS]
    cond = reduce(lambda x,y:x|y, filters)

    return s_db[cond].index.values

def display_search_results(results, db, results_container):
    """
    Display the result of the search engine. Results are displayed in two
    tabs, one to access individual stemma record, one showing a table
    of results exportable to .csv
    """
    if len(results) == 0:
        results_container.header("No results =/")
    else:
        results_container.header(f'Results: {len(results)}')
        tab1, tab2 = results_container.tabs(["Stemmata", "Table"])

        climit = tab1.container(height=500, border=False) # Using parent dummy container to limit size of displayed list
        c = climit.container(height="stretch")

        for i in results:
            e = db.loc[i]
            auth_names = '; '.join([auth['publicationAuthor'] for auth in e['publicationAuthors']])
            page = e["publicationPage"]
            work_title = e["workTitle"]
            pub_title = e["publicationTitle"]
            
            cc = c.container(gap=None)
            col1, col2, col3 = cc.columns([3,3,1])

            ccc = col1.container(gap=None)
            ccc.markdown(f"**{pub_title}** (_p._ {page})")
            ccc.markdown(f'_{auth_names}_')

            col2.markdown(f"**_{work_title.lstrip()}_**")
            if col3.button("details", key=i):
                st.session_state['stemma_to_display'] = e
                st.switch_page('pages/Display_record.py')
            cc.divider()
        
        displayed_db = db.drop(columns = ['stemmaGraph', 'stemmaImage']).map(str)
        tab2.write(displayed_db.loc[results])

st.set_page_config(
page_title="Search",
layout="wide"
)

st.title('Search OpenStemmata')

st.sidebar.page_link('pages/Home.py', label='Home')
st.sidebar.page_link('pages/Search.py', label='Search')
st.sidebar.page_link('pages/Browse.py', label='Browse')
st.sidebar.page_link('pages/Contribute.py', label='Contribute')

# loading data files
database = st.session_state['database']
s_database = searchable_database(database)
files = st.session_state['file_dict']

# defining page layout
text_search = st.text_input("Search (work title, scholar, shelfmark...)", value="")
results_container = st.container(border=False)


# search bar
if text_search:
    s_query = search_format(text_search)
    st.session_state['current_search_query'] = s_query
    results = list(set(search_match(s_query, s_database)))
    display_search_results(results, database, results_container)
# keep current search results displayed
else:  
    if 'current_search_query' in st.session_state:
        s_query = st.session_state['current_search_query']
        results = list(set(search_match(s_query, s_database)))
        display_search_results(results, database, results_container)
