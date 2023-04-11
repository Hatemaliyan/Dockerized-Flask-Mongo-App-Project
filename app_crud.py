from app import app, render_template
from mongo import get_movie, add_movie, update_movie, delete_movie, get_movie_poster, add_movie_poster

@app.route("/movie/<title>")
def get_movie_route(title):
    movie = get_movie(title)
    if not movie:
        return "Movie not found", 404
    poster = get_movie_poster(title)
    return render_template("movie.html", title=title, poster=poster)

@app.route("/movie", methods=["POST"])
def add_movie_route():
    title = request.form['title']
    poster_path = request.form['poster_path']
    result = add_movie(title, poster_path)
    if not result.inserted_id:
        return "Failed to add movie", 500
    poster_data = request.files['poster']
    add_movie_poster(title, poster_data.read())
    return "Movie added successfully"

@app.route("/movie/<title>", methods=["PUT"])
def update_movie_route(title):
    new_poster_path = request.form['poster_path']
    result = update_movie(title, new_poster_path)
    if not result.modified_count:
        return "Failed to update movie", 500
    poster_data = request.files['poster']
    add_movie_poster(title, poster_data.read())
    return "Movie updated successfully"

@app.route("/movie/<title>", methods=["DELETE"])
def delete_movie_route(title):
    result = delete_movie(title)
    if not result.deleted_count:
        return "Failed to delete movie", 500
    fs.delete(fs.find_one({"filename": title})._id)
    return "Movie deleted successfully"
