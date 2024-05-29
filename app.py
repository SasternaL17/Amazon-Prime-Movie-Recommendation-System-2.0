import streamlit as st
import pickle
import pandas as pd
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential())
def fetch_posters(movie_id):
    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=f67221a3373eeb19c190a2cfeda5ddce&language=en-US'.format(movie_id))
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()
    poster_path = data.get('poster_path')
    if poster_path:
        return "https://image.tmdb.org/t/p/w780/" + poster_path
    else:
        return None  # Handle case where poster path is missing
    
    
def recommend(movie):
    if movie not in movies['title'].values:
        st.error(f"Movie '{movie}' not found in the database.")
        return [], []

    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        # Fetching posters from API
        poster_url = fetch_posters(movie_id)
        if poster_url:
            recommended_movies_posters.append(poster_url)
        else:
            recommended_movies_posters.append(None)  # Handle missing posters

    return recommended_movies, recommended_movies_posters

movies_dict = pickle.load(open('movie_dict.pkl','rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl','rb'))

st.title('Amazon Prime Movie Recommendation System 2.0')

selcted_movies_name = st.selectbox(
    'Select a Movie',movies['title'].values
)

if st.button('Suggest'):
    names, posters = recommend(selcted_movies_name)

    if names and posters:
        num_recommendations = min(len(names), 5)
        columns = st.columns(num_recommendations)

        for i in range(num_recommendations):
            with columns[i]:
                st.text(names[i])
                if posters[i]:
                    st.image(posters[i])
                else:
                    st.error("Poster not available")
    else:
        st.warning("No recommendations found.")