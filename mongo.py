from pymongo import MongoClient
from gridfs import GridFS

client = MongoClient(os.environ['TODO_DB_1_PORT_27017_TCP_ADDR'], 27017)
db = client.appdb
fs = GridFS(db)

def get_movie(title):
    return db.appdb.find_one({"title": title})

def add_movie(title, poster_path):
    item_doc = {
        'title': title,
        'poster_path': poster_path
    }
    return db.appdb.insert_one(item_doc)

def update_movie(title, new_poster_path):
    return db.appdb.update_one({"title": title}, {"$set": {"poster_path": new_poster_path}})

def delete_movie(title):
    return db.appdb.delete_one({"title": title})

def get_movie_poster(title):
    doc = get_movie(title)
    if not doc:
        return None
    return fs.get(doc["_id"]).read()

def add_movie_poster(title, poster_data):
    doc = get_movie(title)
    if not doc:
        return None
    return fs.put(poster_data, filename=title)
