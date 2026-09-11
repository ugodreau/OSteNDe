from github import Github
from github import Auth
import requests
import streamlit as st
import yaml
import pandas as pd
import re
import os
import requests
import zipfile
import io
from pathlib import Path
from collections import Counter
import time
import networkx as nx
from networkx.drawing import nx_agraph
import utils as u


@st.cache_data(ttl=3600)    # caching repo content for 1 hour
def get_database_content():
    """
    Loads the content of the OpenStemmata database default (main) branch from
    a zipball archive (in order to minimize GitHub API calls).

    Returns
    -------
    file_dict: dict
        file dictionary containing all data files.
        The key of a file is 
        
        'data/<language>/<publication>/<type>' 
        
        where:
        * <language> is the ISO-639 language code of the corresponding text
        * <publication> is the identifier of the original publication containing
          the corresponding stemma as it appears in OpenStemmata/database file tree
        * <type> is one of
            - 'metadata.txt' metadata yaml file of the submission
            - 'stemma.png' png image of the stemma as it appears in original publication
            - 'stemma.gv' DOT language encoding of the stemma as a directed acyclic graph
            - '<publication>.tei.xml' XML-TEI formating of submission metadata
            - 'stemma.graphml' graphml encoding of the stemma
    """

    token = st.secrets.get("access_token", None)
    url = st.secrets.get("OpenSt_url", None)
    headers = {'Authorization': f'token {token}'} if token else {}
    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        # Extract files to memory
        files_dict = {}
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            for file_info in zip_ref.filelist:
                # Skip directories
                if file_info.is_dir():
                    continue
                
                # Remove the root folder from path (GitHub adds it)
                path_parts = file_info.filename.split('/', 1)
                if len(path_parts) > 1:
                    clean_path = path_parts[1]
                else:
                    clean_path = file_info.filename
                
                # Skip non-data files
                if not re.match('data/', clean_path):
                    continue

                # Read file content
                try:
                    content = zip_ref.read(file_info.filename)
                    files_dict[clean_path] = content
                except Exception as e:
                    st.warning(f"Could not read {clean_path}: {e}")
        

        return files_dict
        
    except Exception as e:
        st.error(f"Failed to download repository: {e}")
        return {}

def process_metadata(entry, file_path):
    """
    Resolve some inconsistencies in metadata formating in OpenStemmata
    """
    # publicationAuthors should be a list of {'publicationAuthor':<value>}
    if not 'publicationAuthors' in entry:
        if 'publicationAuthor' in entry:
            new_cell = [{'publicationAuthor' : entry['publicationAuthor']}]
        else:
            new_cell = [{'publicationAuthor' : ''}]
    elif type(entry['publicationAuthors']) == str:
        new_cell = [{'publicationAuthor' : entry['publicationAuthors']}]
    else:
        new_cell = entry['publicationAuthors']

    entry['publicationAuthors'] = new_cell

    # publicationPlaces should be a list of {'publicationPlace':<value>}
    if not 'publicationPlaces' in entry:
        if 'publicationPlace' in entry:
            new_cell = [{'publicationPlace' : entry['publicationPlace']}]
        else:
            new_cell = [{'publicationPlace' : ''}]
    elif type(entry['publicationPlaces']) == str:
        new_cell = [{'publicationPlace' : entry['publicationAuthors']}]
    else:
        new_cell = entry['publicationPlaces']

    entry['publicationPlaces'] = new_cell

    # contributors should be a list of {'contributor':<value>, 'contributorORCID':<value>}
    if not 'contributors' in entry:
        if 'contributorORCID' in entry:
            orcid = entry['contributorORCID']
        else:
            orcid = ''
        if 'contributor' in entry:
            new_cell = [{'contributor' : entry['contributor'], 'contributorORCID': orcid}]
        else:
            new_cell = [{'contributor' : '', 'contributorORCID': ''}]
    elif type(entry['contributors']) == str:
        new_cell = [{'contributor' : entry['contributors'], 'contributorORCID': ''}]
    else:
        new_cell = entry['contributors']

    entry['contributors'] = new_cell

    # workAuthors should be a list of {'workAuthor':<value>, 'workAuthorsViaf':<value>}
    if not 'workAuthors' in entry:
        if 'workAuthorViaf' in entry:
            viaf = entry['workAuthorViaf']
        else:
            viaf = ''
        if 'workAuthor' in entry:
            new_cell = [{'workAuthor' : entry['workAuthor'], 'workAuthorViaf': viaf}]
        new_cell = [{'workAuthor' : '', 'workAuthorViaf': ''}]
    elif type(entry['workAuthors']) == str:
        new_cell = [{'workAuthor' : entry['workAuthors'], 'workAuthorViaf': ''}]
    else:
        if all([('workAuthor' in k) for k in entry['workAuthors']]):
            new_cell = entry['workAuthors']
        else:
            new_cell = [{'workAuthor' : '', 'workAuthorViaf': ''}]
            st.session_state['data_warnings'].append(f"Missing workAuthor key: {file_path}")
    entry['workAuthors'] = new_cell

    if not 'note' in entry:
        entry['note'] = ''
    
    if 'wits' in entry:
        if entry['wits'] == "":
            entry['wits'] = []
            st.session_state['data_warnings'].append(f"wits format incorrect: {file_path}")
    else:
        entry['wits'] = []
        st.session_state['missing_witnesses'].append(f"{file_path}")


    return entry

@st.cache_data(ttl=3600)
def create_database():
    """
    Generate a pandas.DataFrame from the metadata of submissions

    Parameters
    ----------
    file_dict : dict
        file dictionary of repo content output by get_database_content

    Returns
    -------
    db: pandas.DataFrame
        table of all stemmata metadata, with one entry for each submission
    """
    file_dict = st.session_state['file_dict']
    df = pd.DataFrame()

    for file_path in file_dict.keys():

        # identify submission by its metadata file
        if re.search('metadata.txt$', file_path):
            content = file_dict[file_path]
            submission_path = re.findall('(.*)/metadata.txt', file_path)[0]
            
            # load metadata from yaml file 
            try:
                metadata = yaml.safe_load(content)
                metadata['submissionPath'] = submission_path
            except Exception as e:
                warning = f"Couldn't read file  (ignored): {file_path}\n{e}"
                st.session_state['data_warnings'].append(warning)
                continue

            line = process_metadata(metadata, file_path)
            # load stemma as nx.DiGraph object from .gv file
            try:
                stemma_file = file_dict[f"{submission_path}/stemma.gv"]
                line['stemmaGraph'] = load_tree(stemma_file)
            except  Exception as e:
                warning = f"Couldn't read {submission_path}/stemma.gv (ignored): {e}"
                st.session_state['data_warnings'].append(warning)
                line['stemmataGraph'] = None
                continue
            
            # load (if any) png image of original stemma
            if f"{submission_path}/stemma.png" in file_dict:
                line["stemmaImage"] = file_dict[f"{submission_path}/stemma.png"]
            else:
                line["stemmaImage"] = None

            
            df = pd.concat([df,pd.DataFrame([line])], ignore_index=True)

    return df


def load_tree(file):
    # removing comment lines generating errors in pygraphviz
    stemma_dot = re.sub("[ \t]*#(.*)", "", file.decode())

    # convert DOT file to nx.DiGraph object
    try:
        G = nx_agraph.from_agraph(pygraphviz.AGraph(str(stemma_dot)))
    except Exception as e:
        raise ValueError("Invalid dot file:\n{e}")
    
    # set node state: witness (True) / hypothetical (False)
    colors = nx.get_node_attributes(G, 'color')
    witnesses = {}
    for node in G.nodes():
        if node in colors.keys():
            if colors[node] == 'grey':
                witnesses[node] = False
            else:
                witnesses[node] = True
        else:
            witnesses[node] = True

    nx.set_node_attributes(G, witnesses, 'witness')
    return G


@st.cache_data(ttl=3600, show_spinner=False)
def compute_global_stats():
    """
    Compute various statistics on the whole OpenStemmata database
    """
    stats = {}

    file_dict = st.session_state['file_dict']
    db = st.session_state['database']
    OS_trees = db['stemmaGraph'].values.tolist()

    stats['Number of stemmata'] = len(db)
    stats['Stemmata by language'] = dict(Counter(db['workLangCode']))

    root_degrees = []
    wits_number = []
    patologies = []
    for t in OS_trees:
        if not t==None:
            if not t.nodes[u.tree_tools.root(t)]['witness'] and t.out_degree(u.tree_tools.root(t)) == 1:
                t.remove_node(u.tree_tools.root(t))
            root_degrees.append(u.tree_tools.degree(t, u.tree_tools.root(t)))

            wits_number.append(u.tree_tools.witness_nb(t))
    prop_bifid = Counter(root_degrees)[2] / len(db)
    stats['Proportion of bifid stemmata'] = f'{100 * prop_bifid} %'
    stats['Witness number distribution']= dict(Counter(wits_number))
    stats['All dates'] = db['workOrigDate']
    return stats

##### FOR TESTING ONLY ######

@st.cache_data(ttl=3600)
def get_database_content_temp():
    with open('OS_raw.pickle', 'rb') as f:
        files = pickle.load(f)
    return files