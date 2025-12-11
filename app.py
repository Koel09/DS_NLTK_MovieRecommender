from flask import Flask, request, render_template
import requests
import pickle
import os

app = Flask(__name__)

# -------------------------------------------------------------
# Load or download pickle and index files directly from GitHub (RAW URLs)
# -------------------------------------------------------------

def load_or_download(url, filename):
    if not os.path.exists(filename):
        print(f"Downloading {filename} from GitHub...")
        response = requests.get(url)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            f.write(response.content)

    with open(filename, 'rb') as f:
        return pickle.load(f)


MOVIES_URL = "https://raw.githubusercontent.com/Koel09/DS_NLTK_MovieRecommender/main/model/movies_tfidf.pkl"
SIMILARITY_URL = "https://raw.githubusercontent.com/Koel09/DS_NLTK_MovieRecommender/main/model/similarity_tfidf.pkl"
TFIDF_URL = "https://raw.githubusercontent.com/Koel09/DS_NLTK_MovieRecommender/main/model/tfidf.pkl"

print("Loading models from GitHub...")

movies = load_or_download(MOVIES_URL, 'model/movies_tfidf.pkl')
similarity = load_or_download(SIMILARITY_URL, 'model/similarity_tfidf.pkl')
tfidf = load_or_download(TFIDF_URL, 'model/tfidf.pkl')

print("Models loaded successfully ✅")

def download_index_html():
    index_url = "https://raw.githubusercontent.com/Koel09/DS_NLTK_MovieRecommender/main/templates/index.html"
    if not os.path.exists("templates"):
        os.makedirs("templates")
    response = requests.get(index_url)
    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write(response.text)

# ---------------------------------------------------
# Fetch movie poster logic
# ---------------------------------------------------

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=390e76286265f7638bb6b19d86474639&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    full_path = "https://image.tmdb.org/t/p/w500/" + data['poster_path']
    return full_path


# ---------------------------------------------------
# Recommendation logic
# ---------------------------------------------------


def movie_recommend(movie_title, top_n=10):
    if movie_title not in movies['title'].values:
        return []

    idx = movies[movies['title'] == movie_title].index[0] # get the index of the selected movie

    # get pairwise similarity scores of all movies with the selected movie in descending order
    distances = sorted(
        list(enumerate(similarity[idx])),
        key=lambda x: x[1],
        reverse=True
    )

    # get top 10 recommendation (excl selected movie) along with titles and posters
    movie_titles = [movies.iloc[i[0]]['title'] for i in distances[1:top_n + 1]]
    movie_posters = [fetch_poster(movies.iloc[i[0]]['id']) for i in distances[1:top_n + 1]]
    return movie_titles, movie_posters


# ---------------------------------------------------
# Flask routes home page
# ---------------------------------------------------

@app.route('/')
def home():

    movie_list = sorted(movies['title'].tolist())
    download_index_html()

    return render_template(
        'index.html',
        movie_list=movie_list
    )

@app.route('/recommend', methods=['POST'])
def recommend():

    movie_list = sorted(movies['title'].tolist())

    movie_title = request.form['selected_movie']
    recommended_movie_titles, recommended_movie_posters = movie_recommend(movie_title)

    return render_template(
        'index.html',
        movie_list=movie_list,
        recommended_movie_titles=recommended_movie_titles,
        recommended_movie_posters=recommended_movie_posters
    )

if __name__ == '__main__':
    app.run(debug=True)