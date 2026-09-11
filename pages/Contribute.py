import streamlit as st

st.title('Contribute')
st.set_page_config(
layout="wide"
)

st.sidebar.page_link('pages/Home.py', label='Home')
st.sidebar.page_link('pages/Search.py', label='Search')
st.sidebar.page_link('pages/Browse.py', label='Browse')
st.sidebar.page_link('pages/Contribute.py', label='Contribute')


st.markdown('''
OpenStemmata currently only accept submissions as GitHub pull requests on the [database repository](https://github.com/OpenStemmata/database).
If you want to contribute, please check the data preparation [guidelines](https://openstemmata.github.io/guidelines.html), as well as enhancements and submission suggestions on the repository [issues](https://github.com/OpenStemmata/database/issues).
Contributions can also take the form of corrections and addition to already submitted stemma records:
''')
st.markdown('+ There seems to be formatting issues on the followings records')
exp1 = st.expander('See')
for mes in st.session_state["data_warnings"]:
    exp1.warning(mes)
st.markdown('+ The followings records do not have witness metadata (datation, shelfmark, digitization links, etc.), feel free to add them !')
exp2 = st.expander('See')
for mes in st.session_state["missing_witnesses"]:
    exp2.warning(mes)