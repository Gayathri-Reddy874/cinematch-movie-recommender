import os
import streamlit as st
import pandas as pd
import pickle
import requests

# ─────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CineMatch — Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0a0f;
    color: #e8e6e1;
}

/* ── Main container ── */
.main .block-container {
    padding: 2rem 4rem 4rem 4rem;
    max-width: 1400px;
}

/* ── Hero Header ── */
.hero-wrap {
    text-align: center;
    padding: 3.5rem 0 2rem 0;
    position: relative;
}
.hero-wrap::before {
    content: "";
    position: absolute;
    top: 0; left: 50%;
    transform: translateX(-50%);
    width: 600px; height: 300px;
    background: radial-gradient(ellipse at center, rgba(229,57,53,0.18) 0%, transparent 70%);
    pointer-events: none;
}
.hero-badge {
    display: inline-block;
    background: rgba(229,57,53,0.15);
    border: 1px solid rgba(229,57,53,0.4);
    color: #e53935;
    font-size: 0.72rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    padding: 0.3rem 0.9rem;
    border-radius: 100px;
    margin-bottom: 1.2rem;
}
.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: clamp(3.5rem, 8vw, 6.5rem);
    letter-spacing: 0.05em;
    line-height: 1;
    color: #f5f3ef;
    margin: 0 0 0.6rem 0;
}
.hero-title span { color: #e53935; }
.hero-sub {
    color: #7a7875;
    font-size: 1rem;
    font-weight: 300;
    letter-spacing: 0.02em;
    margin-bottom: 2.5rem;
}

/* ── Divider ── */
.divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.07);
    margin: 2rem 0;
}

/* ── Search section ── */
.search-label {
    font-size: 0.75rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #7a7875;
    margin-bottom: 0.4rem;
}

/* ── Streamlit selectbox & button overrides ── */
div[data-baseweb="select"] > div {
    background-color: #16161f !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    color: #e8e6e1 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.55rem 1rem !important;
    min-height: 52px !important;
    transition: border-color 0.2s;
}
div[data-baseweb="select"] > div:hover {
    border-color: rgba(229,57,53,0.5) !important;
}
div[data-baseweb="select"] svg { fill: #7a7875 !important; }

/* dropdown list */
div[data-baseweb="popover"] * {
    background-color: #16161f !important;
    color: #e8e6e1 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Recommend button ── */
.stButton > button {
    background: linear-gradient(135deg, #e53935 0%, #b71c1c 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.75rem 2.5rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 24px rgba(229,57,53,0.3) !important;
    width: 100% !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(229,57,53,0.45) !important;
}
.stButton > button:active {
    transform: translateY(0px) !important;
}

/* ── Section heading ── */
.section-heading {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.8rem;
    letter-spacing: 0.06em;
    color: #f5f3ef;
    margin: 2.5rem 0 1.2rem 0;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.section-heading::after {
    content: "";
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.07);
    margin-left: 0.5rem;
}

/* ── Movie card ── */
.movie-card {
    background: #16161f;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    overflow: hidden;
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    cursor: default;
    height: 100%;
}
.movie-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 16px 48px rgba(0,0,0,0.6);
    border-color: rgba(229,57,53,0.35);
}
.movie-card img {
    width: 100%;
    aspect-ratio: 2/3;
    object-fit: cover;
    display: block;
}
.movie-card-body {
    padding: 0.85rem 1rem 1rem 1rem;
}
.movie-card-rank {
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #e53935;
    margin-bottom: 0.25rem;
}
.movie-card-title {
    font-size: 0.95rem;
    font-weight: 500;
    color: #f0ede8;
    line-height: 1.35;
    margin: 0;
}

/* ── Selected movie banner ── */
.selected-banner {
    background: linear-gradient(135deg, rgba(229,57,53,0.12) 0%, rgba(183,28,28,0.06) 100%);
    border: 1px solid rgba(229,57,53,0.25);
    border-radius: 12px;
    padding: 1rem 1.4rem;
    margin: 1.2rem 0;
    display: flex;
    align-items: center;
    gap: 0.7rem;
    font-size: 0.9rem;
    color: #c5c2bc;
}
.selected-banner .movie-icon { font-size: 1.4rem; }
.selected-banner .movie-name {
    color: #f5f3ef;
    font-weight: 500;
}

/* ── Footer ── */
.footer {
    text-align: center;
    color: #3a3835;
    font-size: 0.78rem;
    letter-spacing: 0.08em;
    margin-top: 4rem;
    padding-top: 1.5rem;
    border-top: 1px solid rgba(255,255,255,0.05);
}

/* ── Spinner text ── */
.stSpinner > div { border-top-color: #e53935 !important; }

/* hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# OMDb API — secure key loading
# ─────────────────────────────────────────────
# Resolution order:
#   1. Streamlit secrets (.streamlit/secrets.toml) — used for Streamlit Community Cloud
#   2. Environment variable OMDB_API_KEY — used for local dev / other hosts
# The app never hardcodes a real key, so it's safe to make this repo public.

def get_api_key():
    try:
        return st.secrets["OMDB_API_KEY"]
    except (KeyError, FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        pass
    return os.environ.get("OMDB_API_KEY")

API_KEY = get_api_key()

if not API_KEY:
    st.error(
        "⚠️ OMDb API key not found. Add it to `.streamlit/secrets.toml` "
        "as `OMDB_API_KEY = \"your_key_here\"`, or set the `OMDB_API_KEY` "
        "environment variable before running the app. Get a free key at "
        "https://www.omdbapi.com/apikey.aspx"
    )
    st.stop()

def fetch_poster(movie_title):
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={API_KEY}"
    try:
        data = requests.get(url, timeout=5).json()
        if data.get('Poster') and data['Poster'] != "N/A":
            return data['Poster']
    except Exception:
        pass
    return "https://via.placeholder.com/500x750/16161f/e53935?text=No+Poster"

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return pd.DataFrame(movies_dict), similarity

movies, similarity = load_data()

# ─────────────────────────────────────────────
# RECOMMEND FUNCTION  (unchanged logic)
# ─────────────────────────────────────────────
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(
        list(enumerate(distances)), reverse=True, key=lambda x: x[1]
    )[1:6]

    recommended_movies, recommended_posters = [], []
    for i in movies_list:
        title = movies.iloc[i[0]].title
        recommended_movies.append(title)
        recommended_posters.append(fetch_poster(title))
    return recommended_movies, recommended_posters

# ─────────────────────────────────────────────
# UI LAYOUT
# ─────────────────────────────────────────────

# ── Hero ──
st.markdown("""
<div class="hero-wrap">
    <div class="hero-badge">✦ AI-Powered Discovery</div>
    <h1 class="hero-title">CINE<span>MATCH</span></h1>
    <p class="hero-sub">Pick a film you love — we'll find five more worth your time.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Search row ──
col_select, col_btn = st.columns([5, 1.2], gap="medium")

with col_select:
    st.markdown('<p class="search-label">🎞 Select a Movie</p>', unsafe_allow_html=True)
    selected_movie = st.selectbox(
        label="",
        options=movies['title'].values,
        label_visibility="collapsed"
    )

with col_btn:
    st.markdown('<p class="search-label">&nbsp;</p>', unsafe_allow_html=True)
    recommend_clicked = st.button("✦ Find Movies")

# ── Selected movie tag ──
if selected_movie:
    st.markdown(f"""
    <div class="selected-banner">
        <span class="movie-icon">🎬</span>
        <span>Currently selected: <span class="movie-name">{selected_movie}</span></span>
    </div>
    """, unsafe_allow_html=True)

# ── Results ──
if recommend_clicked:
    with st.spinner("Finding your next obsession…"):
        names, posters = recommend(selected_movie)

    st.markdown('<div class="section-heading">✦ Recommended For You</div>', unsafe_allow_html=True)

    cols = st.columns(5, gap="medium")
    rank_labels = ["Top Pick", "2nd Pick", "3rd Pick", "4th Pick", "5th Pick"]

    for i, col in enumerate(cols):
        with col:
            st.markdown(f"""
            <div class="movie-card">
                <img src="{posters[i]}" alt="{names[i]}" />
                <div class="movie-card-body">
                    <div class="movie-card-rank">{rank_labels[i]}</div>
                    <p class="movie-card-title">{names[i]}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ── Footer ──
st.markdown("""
<div class="footer">
    CINEMATCH &nbsp;·&nbsp; Content-Based Recommendation Engine &nbsp;·&nbsp; TMDB Dataset
</div>
""", unsafe_allow_html=True)
