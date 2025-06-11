import sqlite3 as sql
import time
import random
import bcrypt
import data_handler as dh


def insert_recipe(name, cooktime, diff,region,desc,user_id, ingredients, steps):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute(
        "INSERT INTO recipies (r_name,r_time,r_difficulty, r_region, r_description, user_id, r_ingredients, r_steps) VALUES (?,?,?,?,?,?,?,?)",
        (name, cooktime, diff, region, desc, user_id, ingredients, steps),
    )
    con.commit()
    con.close()

def saveUserSecret(username, user_secret):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute(
        "UPDATE users SET user_secret = ? WHERE username= ?",
        (user_secret, username),
    )
    con.commit()
    con.close()

def getUserSecret(username):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute(
        "SELECT user_secret FROM users WHERE username= ?",
        (username,)
    )
    user = cur.fetchone()
    con.close()
    return user[0]

def retrieveUsers(username, password):
    con = sql.connect("database_files/database.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    
    cur.execute(f"SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()

    if user == None:
        con.close()
        return False
    else:
        hashed_password = user["password"]
        encoded_password = password.encode()
        isLoggedIn = bcrypt.checkpw(encoded_password, hashed_password)
        con.close()

        return isLoggedIn
        
        

        # cur.execute(f"SELECT * FROM users WHERE password = ?", (password,))
        # # Plain text log of visitor count as requested by Unsecure PWA management
        # with open("visitor_log.txt", "r") as file:
        #     number = int(file.read().strip())
        #     number += 1
        # with open("visitor_log.txt", "w") as file:
        #     file.write(str(number))
        # # Simulate response time of heavy app for testing purposes
        # time.sleep(random.randint(80, 90) / 1000)
        # if cur.fetchone() == None:
        #     con.close()
        #     return False
        # else:
        #     con.close()
        #     return True


def insertFeedback(feedback):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute(f"INSERT INTO feedback (feedback) VALUES (?)", (feedback,))
    con.commit()
    con.close()


def list_recipe(user_id):
    con = sql.connect("database_files/database.db")
    con.row_factory=sql.Row
    cur = con.cursor()
    data = cur.execute("SELECT * FROM recipies WHERE user_id = ?", (user_id,)).fetchall()
    con.close()
    print(data)
    return data 

def view_recipe(r_id, user_id):
    con = sql.connect("database_files/database.db")
    con.row_factory=sql.Row
    cur = con.cursor()
    data = cur.execute("SELECT * FROM recipies LEFT JOIN favourites ON recipies.r_id=favourites.r_id AND favourites.user_id = ? WHERE recipies.r_id = ? ", (user_id, r_id,)).fetchone()

    con.close()
    print(data)
    return data 


def search_recipe(query):
    con = sql.connect("database_files/database.db")
    con.row_factory=sql.Row
    cur = con.cursor()
    data = cur.execute("SELECT * FROM recipies WHERE r_name LIKE ? OR r_ingredients LIKE ? OR r_region LIKE ? OR r_steps LIKE ?", (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%" ))
    data = data.fetchall()
    con.close()
    print(data)
    return data 

def favourite(user_id, r_id):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute(f"SELECT * FROM favourites WHERE user_id = ? AND r_id = ?", (user_id, r_id,))
    f = cur.fetchone()

    if f == None:
        cur.execute("INSERT INTO favourites (user_id, r_id) VALUES (?,?)", (user_id, r_id))
        con.commit()

    con.close()

def list_favourites(user_id):
    con = sql.connect("database_files/database.db")
    con.row_factory=sql.Row
    cur = con.cursor()
    data = cur.execute("SELECT * FROM favourites INNER JOIN recipies ON favourites.r_id = recipies.r_id WHERE favourites.user_id = ?", (user_id,)).fetchall()
    con.close()
    return data 

def remove_favourite(f_id):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute("DELETE FROM favourites WHERE f_id = ?", (f_id,))
    con.commit()
    con.close()

def view_recipe(r_id, user_id):
    con = sql.connect("database_files/database.db")
    con.row_factory=sql.Row
    cur = con.cursor()
    data = cur.execute("SELECT * FROM recipies LEFT JOIN favourites ON recipies.r_id=favourites.r_id AND favourites.user_id = ? WHERE recipies.r_id = ? ", (user_id, r_id,)).fetchone()

    con.close()
    print(data)
    return data 

def count_favourites(r_id):
    con = sql.connect("database_files/database.db")
    con.row_factory=sql.Row
    cur = con.cursor()
    data = cur.execute("SELECT COUNT (favourites.f_id) AS num_favourites FROM favourites WHERE favourites.r_id = ?", (r_id)).fetchone()
    con.close()
    return data[0]

def topten_recipe():
    con = sql.connect("database_files/database.db")
    con.row_factory=sql.Row
    cur = con.cursor()
    data = cur.execute("SELECT recipies.r_id, recipies.r_name, COUNT(favourites.f_id) AS num_favourites FROM recipies INNER JOIN favourites ON recipies.r_id=favourites.r_id  GROUP BY recipies.r_id ORDER BY num_favourites DESC").fetchall()
    con.close()
    print(data)
    return data  

def delete_recipe(r_id, user_id):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    recipe = cur.execute("SELECT * FROM recipies WHERE r_id = ? AND user_id = ?", (r_id,user_id)).fetchone()
    if recipe:
        cur.execute("DELETE FROM recipies WHERE r_id = ? AND user_id = ?", (r_id,user_id))
        con.commit()
        cur.execute("DELETE FROM favourites WHERE r_id = ?", (r_id))
        con.commit()
    con.close()  



