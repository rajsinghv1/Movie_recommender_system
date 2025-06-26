import streamlit as st
import pickle
import pandas as pd
import requests
from requests.exceptions import RequestException

# Load precomputed data
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title('Movie Recommender System')

def fetch_poster(movie_id):
    """Fetch the movie poster URL from TMDB or return a fallback placeholder."""
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=0fd4e51a9913a5c30d56c75ab04077b4&language=en-US"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if not poster_path:
            raise ValueError("Missing poster_path")
        return "https://image.tmdb.org/t/p/w500" + poster_path
    except (RequestException, ValueError) as e:
        st.warning(f"Failed to fetch poster for movie ID {movie_id}. Reason: {e}")
        return "https://via.placeholder.com/500x750?text=No+Poster"

def recommend(movie_name):
    """Return recommended movie titles and posters for the given movie."""
    index = movies[movies['title'] == movie_name].index[0]
    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters

# Streamlit UI
movie_list = movies['title'].values
selected_movie_name = st.selectbox('Select a movie you like:', movie_list)

if st.button('Show Recommendations'):
    names, posters = recommend(selected_movie_name)
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i])
