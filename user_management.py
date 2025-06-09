import sqlite3 as sql
import time
import random
import bcrypt
import data_handler as dh


def insertUser(username, password, DoB):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute(
        "INSERT INTO users (username,password,dateOfBirth) VALUES (?,?,?)",
        (username, password, DoB),
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
    
def login(username, password):
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

        return user
        
        

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


def listFeedback():
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    data = cur.execute("SELECT * FROM feedback").fetchall()
    con.close()
    f = open("templates/partials/success_feedback.html", "w")
    for row in data:
        f.write("<p>\n")
        f.write(f"{dh.make_web_safe(row[1])}\n")
        f.write("</p>\n")
    f.close()
