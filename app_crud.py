from passwords_and_keys import mongo_db_password as mpw
from connect_to_mongoDB import db, collection, username

# check if user exists
users_dict = db.command("usersInfo")
users_list = users_dict['users']
#print(users_list)

if len(users_list) > 0:
    for user_dict in users_list:
        user_list_tup = user_dict.items()
        for user_data in user_list_tup:
            if user_data[0] == username and user_data[1] == username:
                print(f'User {username} already exists')
else:
    # create user with read/write permissions to 'posters' collection
    db.command("createUser", "user", pwd=mpw, roles=[{"role": "readWrite", "db": "TMDB_posters"}])
    print(f'User {username} created successfully')
