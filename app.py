import requests
from flask import Flask, redirect, url_for, request, render_template, make_response
from PIL import Image
from pymongo import MongoClient
from gridfs import GridFS
import json
from io import BytesIO
import os
import ssl
import base64

app = Flask(__name__, template_folder='./')

client = MongoClient(os.environ['TODO_DB_1_PORT_27017_TCP_ADDR'], 27017)
db = client.appdb
fs = GridFS(db)

# Define the TMDB API endpoint and API key
api_key = "38f91b8617170eda47890d76bbdd4f58"
base_url = "https://api.tmdb.org/3/discover/movie?api_key="+api_key

def find_poster_in_mongo(title):
    print("Searching for movie:", title)
    movies = []
    for movie in db.appdb.find({'title': title}):
        image_data = fs.get(movie['poster_id']).read()
        image = Image.open(BytesIO(image_data))
        movie['poster'] = base64.b64encode(image.tobytes()).decode()
        movie['poster_url'] = 'data:image/png;base64,' + movie['poster']
        movies.append(movie)
    print("Found", len(movies), "movies")
    return movies

@app.route('/download/<path:poster_path>')
def download_poster(poster_path):
    poster_data = requests.get(f'https://image.tmdb.org/t/p/w500/{poster_path}').content
    response = make_response(poster_data)
    response.headers.set('Content-Type', 'image/jpeg')
    response.headers.set('Content-Disposition', 'attachment', filename='poster.jpg')
    return response   

def search_movie(movie_title):
    search_movie = 'https://api.themoviedb.org/3/search/movie'
    page_num = 1
    total_movies = []
    movie_titles = []

    while True:
        params = {
            "api_key": api_key,
            "query": movie_title,
            "page": page_num
        }

        response = requests.get(search_movie, params=params)
        data = response.json()
        movies_list = data.get("results")
        if not movies_list:
            break

        for movie in movies_list:
            if movie_title in movie.get("title"):
                title = movie.get("title")
                posters = find_poster_in_mongo(title)
                if posters:
                    movie['poster_url'] = posters[0]['poster_url']
                total_movies.append(movie)
                movie_titles.append(title)

        page_num += 1

    print(f'Movies found: {len(total_movies)}')
    return total_movies, movie_titles

@app.route("/")
def home():
    ssl.create_default_https_context = ssl._create_unverified_context
    response = requests.get(base_url)
    json_data = response.json()
    return render_template("index.html", data=json_data["results"])

@app.route("/search-movie-poster", methods=["POST"])
def search_movie_poster():
    # Get the movie title from the form data
    movie_title = request.form.get('movie_title')

    # Define the query parameters for the TMDB API request
    params = {
        "api_key": api_key,
        "query": movie_title
    }

    # Send a GET request to the TMDB API endpoint
    response = requests.get(base_url, params=params)

    # Parse the JSON response and extract the poster path
    data = response.json()
    if data["total_results"] == 0:
        return render_template("search_result.html", title=movie_title, poster_path=None)

    poster_path = data["results"][0]["poster_path"]

    # Download the poster image and save it to GridFS
    image_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
    response = requests.get(image_url)
    poster_data = response.content
    poster_id = fs.put(poster_data, filename=movie_title)

    # Save the movie title and poster ID to MongoDB
    item_doc = {
        'title': movie_title,
        'poster_id': poster_id
    }
    db.appdb.insert_one(item_doc)

    # Render the template with the movie title and poster path
    return render_template("search_result.html", title=movie_title, poster_path=poster_path)

@app.route('/find_movie', methods=['POST'])
def find_movie():
    movie_title = request.form.get('movie_title')
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_title}"
    response = requests.get(search_url)
    json_data = response.json()
    return render_template("index.html", data=json_data["results"])

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)