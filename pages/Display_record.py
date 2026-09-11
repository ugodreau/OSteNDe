import streamlit as st
from utils.misc import iso639_to_name
import pydot
from streamlit_agraph import agraph, Node, Edge, Config


def display_stemma_record(entry, record_container):
    file_dict = st.session_state["file_dict"]
    path = entry["submissionPath"]

    # formating list fields
    pub_title = entry["publicationTitle"]
    pub_authors = entry['publicationAuthors']
    pub_authors = '; '.join([c['publicationAuthor'] for c in pub_authors])
    pub_places = entry['publicationPlaces']
    pub_places = '; '.join([c['publicationPlace'] for c in pub_places])
    work_authors = entry['workAuthors']
    work_authors = '; '.join([c['workAuthor'] for c in work_authors])

    language_name = iso639_to_name(entry['workLangCode'])
    language = f"{language_name} (```{entry['workLangCode']}```)"

    c = record_container.container(border=True)
    c.header(f"{pub_title}", anchor='stemma_record', divider="red")

    col1, col2 = c.columns(2)
    im_cont = col1.container(border=False, height=350)

    # original scan of stemma
    try:
        orig_img = file_dict[f"{path}/stemma.png"]
        im_cont.write('Original image of the stemma \n')
        im_cont.image(orig_img, width="content")
    except:
        im_cont.warning('No available picture of the stemma')
    
    col2.subheader('Publication informations')
    col2.table({
        'Title' : pub_title, 
        'Authors' : pub_authors,
        'Publcation Series': entry['publicationSeries'],
        'Publication Type' : entry['publicationType'],
        'Publication Date' : entry['publicationDate'],
        'Publication Place': pub_places})

    col3,col4 = c.columns(2)
    col3.subheader('Work informations')
    col3.table({
        'Work title' : entry['workTitle'],
        'Work authors' : work_authors,
        'Work language' : language,
        'Work Genre' : entry['workGenre'],
        'Origin place of work' : entry['workOrigPlace'],
        'Date of work' : entry['workOrigDate']
    })

    col4.subheader('Stemmatic informations')
    col4.table({
        'Type of stemma' : entry['stemmaType'],
        'Stemma drawn in publication' : entry['drawnStemma'],
        'Type of the root' : entry['rootType'],
        'All witnesses in _recensio_' : entry['completeWits'],
        'Contaminated tradition' : entry['contam']

    })


def display_witness_informations(entry, wits_container):
    c = record_container.container(border=True)
    c.header(f"Witness informations", anchor='stemma_record', divider="red")

    file_dict = st.session_state["file_dict"]
    path = entry["submissionPath"]
    dotfile = file_dict[f"{path}/stemma.gv"].decode("utf-8")
    
    col1, col2 = c.columns(2)
    col1.graphviz_chart(dotfile)
    witness_list = entry['wits']

    if len(witness_list) == 0:
        col2.warning("No witness information to display =/")
    else:
        wit_sigla = col2.selectbox("Witness", [w['witSigla'] for w in witness_list], index=0)
        wit = {w['witSigla']:w for w in witness_list}[wit_sigla]
        col2.table({
        'Sigla' : wit['witSigla'],
        'Signature' : wit['witSignature'],
        'Production date' : wit['witOrigDate'],
        'Production place' : wit['witOrigPlace'],
        'Link to digitization' : entry['witDigit'] if 'witDigit' in entry else "",
        'Notes' : entry['witNotes'] if 'witNotes' in entry else ""
    })

st.title('Stemma')

st.sidebar.page_link('pages/Home.py', label='Home')
st.sidebar.page_link('pages/Search.py', label='Search')
st.sidebar.page_link('pages/Browse.py', label='Browse')
st.sidebar.page_link('pages/Contribute.py', label='Contribute')


record_container = st.container(border=False)
if 'stemma_to_display' in st.session_state:
    display_stemma_record(st.session_state['stemma_to_display'], record_container)

        

wit_container = st.container(border=False)

display_witness_informations(st.session_state['stemma_to_display'], wit_container)


