import requests
from flask import Flask, redirect, url_for, request, render_template
from PIL import Image
from pymongo import MongoClient
import json
from io import BytesIO
import os
import urllib.request as request
import ssl

app = Flask(__name__, template_folder='./')

client = MongoClient(os.environ['TODO_DB_1_PORT_27017_TCP_ADDR'], 27017)
db = client.appdb

# Define the TMDB API endpoint and API key
api_key = "USE YOUR API KEY HERE"
base_url = "https://api.tmdb.org/3/discover/movie?api_key="+api_key

@app.route("/")
def home():
    ssl.create_default_https_context = ssl._create_unverified_context
    response = requests.get(base_url)
    json_data = response.json()
    return render_template("index.html", data=json_data["results"])

@app.route("/search-movie-poster", methods=["POST"])
def search_movie_poster():
    # Get the movie title from the form data
    movie_title = request.form['movie_title']

    # Define the query parameters for the TMDB API request
    params = {
        "api_key": api_key,
        "query": movie_title
    }

    # Send a GET request to the TMDB API endpoint
    response = requests.get(base_url, params=params)

    # Parse the JSON response and extract the poster path
    data = response.json()
    poster_path = data["results"][0]["poster_path"]

    # Download the poster image and save it to a file folder
    image_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    file_path = os.path.join(os.getcwd(), f"{movie_title}.jpg")
    image.save(file_path)

    # Save the movie title and poster path to MongoDB
    item_doc = {
        'title': movie_title,
        'poster_path': poster_path
    }
    db.appdb.insert_one(item_doc)

    # Render the template with the movie title and poster path
    return render_template("search_result.html", title=movie_title, poster_path=poster_path)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
