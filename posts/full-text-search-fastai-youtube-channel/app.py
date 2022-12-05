# AUTOGENERATED! DO NOT EDIT! File to edit: _Deploy_Search_Engine_Streamlit.ipynb.

# %% auto 0
__all__ = ['db_path', 'cur', 'playlist', 'video', 'pl_sel', 'pl_to_id', 'all_options', 'container', 'get_query', 'search']

# %% _Deploy_Search_Engine_Streamlit.ipynb 1
import streamlit as st
import sqlite3

# %% _Deploy_Search_Engine_Streamlit.ipynb 3
db_path = '/mnt/m/datamatica/posts/full-text-search-fastai-youtube-channel/'

# %% _Deploy_Search_Engine_Streamlit.ipynb 5
import platform
print(f'platform.node(): {platform.node()}')

# %% _Deploy_Search_Engine_Streamlit.ipynb 6
try:
    db = sqlite3.connect(db_path + 'fastai_yt.db')
except:
    db = sqlite3.connect('fastai_yt.db')

cur = db.cursor()

# %% _Deploy_Search_Engine_Streamlit.ipynb 7
playlist = cur.execute('SELECT playlist_id, playlist_name FROM playlist').fetchall()
video = cur.execute('SELECT video_id, video_name FROM video').fetchall()
playlist = {p: n for p, n in playlist}
video = {p: n for p, n in video}
pl_sel = list(playlist.values())
pl_to_id = {v:k for k,v in playlist.items()}

# %% _Deploy_Search_Engine_Streamlit.ipynb 10
st.title('Full-Text Search fastai Youtube Playlists')

# https://discuss.streamlit.io/t/select-all-on-a-streamlit-multiselect/9799/2

all_options = st.checkbox(
    "Select all Playlists", #on_change=on_ch_checkbox, 
    key='sel_all', value=True
)

container = st.container()
if all_options:
    sel_options = container.multiselect(
        "Select one or more Playlist(s):", pl_sel, disabled=True)
else:
    sel_options = container.multiselect(
        "Select one or more Playlist(s):", pl_sel, pl_sel)

if all_options:
    options = list(playlist.values())
else: 
    options = sel_options

st.write('Selected playlist(s):', options)


# %% _Deploy_Search_Engine_Streamlit.ipynb 11
# q = st.text_input('Search Query', 'fastcore*')

# %% _Deploy_Search_Engine_Streamlit.ipynb 12
def get_query(q, limit):
    
    search_in = 'text'
    
    if not( len(options)==len(pl_sel) or len(options)==0 ):
        search_in = 'transcriptions_fts'
        q_pl = '(playlist_id: '
        for pl in options:
            end = ' OR ' if pl != options[-1] else ')'
            q_pl = q_pl + f'"{pl_to_id[pl]}"' + end
        
        q = f"(text: {q}) AND " + q_pl

    query = f"""
    SELECT *, HIGHLIGHT(transcriptions_fts, 3, '[', ']')
    FROM transcriptions_fts WHERE {search_in} MATCH '{q}' ORDER BY rank
    LIMIT "{limit}" 
    """
    return query


def search():
    get_query(q, 5)

with st.form("Input"):
    queryText = st.text_area("Search query: \ne.g. «fastc*», «fastcore OR paral*»", height=1, max_chars=None)
    limit_val = st.slider("Number of results:", min_value=5, max_value=20)
    btnResult = st.form_submit_button('Search')
    
if btnResult:
    if not queryText:
        st.text('Please enter a search query.')
    else:
        try:
            st.text('Search query generated:')
            # run query
            st.write(get_query(queryText, limit_val).replace('*', '\*'))
            res = cur.execute(get_query(q=queryText, limit=limit_val)).fetchall()
            st.text('Search results (click to go to YouTube):')

            res_md = (
                '  \n  '.join([
                '  \n  '.join([
                f"{i}.- Playlist: `{playlist[each[0]]}`, Video: `{video[each[1]]}`", 
                f"Caption: '...[{each[4].replace('[','**').replace(']','**')}](https://youtu.be/{each[1]}?t={str(int(each[2]))})...'", 
                '\n'
                ])
                for i, each in enumerate(res)
            ]))

            st.markdown(res_md)
        except:
            st.text('Invalid search query.')
