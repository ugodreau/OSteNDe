import streamlit as st
from utils.misc import iso639_to_name


def display_stemma(entry, record_container):
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
        'Publciation Date' : entry['publicationDate'],
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
    
    