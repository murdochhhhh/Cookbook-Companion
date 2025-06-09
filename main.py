from flask import Flask, session
from flask_session import Session
from flask import render_template
from flask import request
from flask import redirect
from flask_csp.csp import csp_header
import user_management as dbHandler
import recipe_management as rHandler
import bcrypt  
from flask_wtf import CSRFProtect
import pyotp 
import pyqrcode
import os
import base64
from io import BytesIO

# Code snippet for logging a message
# app.logger.critical("message")

app = Flask(__name__)
app.secret_key = "382tghekjfhku4g"
csrf = CSRFProtect(app)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/success.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
@csp_header({
        "base-uri": "self",
        "default-src": "'self' 'unsafe-inline'",
        "script-src": "'self'",
        "img-src": "*",
        "media-src": "'self'",
        "font-src": "self",
        "object-src": "'self'",
        "child-src": "'self'",
        "connect-src": "'self'",
        "worker-src": "'self'",
        "report-uri": "/csp_report",
        "frame-ancestors": "'none'",
        "form-action": "'self'",
        "frame-src": "'none'",
    })
def addFeedback():
    # if request.method == "GET" and request.args.get("url"):
    #     url = request.args.get("url", "")
    #     return redirect(url, code=302)
    
    if not session.get("isLoggedIn"):
        return redirect("/index.html", code=302)

    username = session.get("username")

    if request.method == "POST":
        feedback = request.form["feedback"]
        dbHandler.insertFeedback(feedback)
        dbHandler.listFeedback()
        return render_template("/success.html", state=True, value=username)
    else:
        dbHandler.listFeedback()
        return render_template("/success.html", state=True, value=username)


@app.route("/signup.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
def signup():
    # if request.method == "GET" and request.args.get("url"):
    #     url = request.args.get("url", "")
    #     return redirect(url, code=302)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        encoded_password = password.encode()
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(encoded_password, salt)
        DoB = request.form["dob"]
        dbHandler.insertUser(username, hashed_password, DoB)
        return render_template("/index.html")
    else:
        return render_template("/signup.html")


@app.route("/index.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
@app.route("/", methods=["POST", "GET"])
def home():
    # if request.method == "GET" and request.args.get("url"):
    #     url = request.args.get("url", "")
        # return redirect(url, code=302)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = dbHandler.login(username, password)

        if user:
            user_secret = dbHandler.getUserSecret(username)
            session['user_id'] = user[0]

            if user_secret:
                session["user_secret"] = user_secret
                return redirect("/prompt_two_fa.html", code=302)


            else:
                #allow normal login(no 2fa)
                session['isLoggedIn'] = True
                session['username'] = username
        
                dbHandler.listFeedback()
                return redirect("/dashboard.html", code=302)
                # return render_template("/success.html", value=username, state=isLoggedIn)
        else:
            return render_template("/index.html")
    else:
        return render_template("/index.html")

@app.route("/prompt_two_fa.html", methods=["POST", "GET"])
def prompt_two_fa():
    if not session.get("username"):
        return redirect ("/", code=302)

    if request.method == "POST":
        twofa_code = request.form["twofa_code"]
        user_secret = session.get("user_secret")
        totp = pyotp.TOTP(user_secret)
        if totp.verify(twofa_code):
            session["isLoggedIn"] = True
            session['two_fa'] = True
            return redirect("/dashboard.html", code=302)
        else:
            return redirect("/prompt_two_fa.html", code=302)

    return render_template("/prompt_two_fa.html")
    


@app.route("/setup_2fa.html", methods=["POST", "GET"])
def setup_2fa():
    if not session.get("isLoggedIn"):
        return redirect ("/", code=302)

    username = session.get("username")

    if request.method == "POST":
        twofa_code = request.form["twofa_code"]
        user_secret = session.get("user_secret")
        totp = pyotp.TOTP(user_secret)
        if totp.verify(twofa_code):
            # save the user secret to database
            dbHandler.saveUserSecret(username, user_secret)
            return redirect("/dashboard.html", code=302)
        else:
            return redirect("/setup_2fa.html", code=302)
    
    user_secret = pyotp.random_base32(32)
    session['user_secret'] = user_secret
    totp = pyotp.TOTP(user_secret)

    otp_uri = totp.provisioning_uri(name=username,issuer_name="Cookbook Companion")
    qr_code = pyqrcode.create(otp_uri)
    stream = BytesIO()
    qr_code.png(stream, scale=5)
    qr_code_b64 = base64.b64encode(stream.getvalue()).decode('utf-8')

    return render_template("/setup_2fa.html", qr_code_b64=qr_code_b64, value=username)


@app.route("/logout", methods=["POST", "GET"])
def logout():
    session['isLoggedIn'] = False
    session['two_fa'] = False 
    return redirect("/", code=302)

@app.route("/create.html", methods=["POST", "GET", "PUT", "PATCH", "DELETE"])
@csp_header({
        "base-uri": "self",
        "default-src": "'self' 'unsafe-inline'",
        "script-src": "'self'",
        "img-src": "*",
        "media-src": "'self'",
        "font-src": "self",
        "object-src": "'self'",
        "child-src": "'self'",
        "connect-src": "'self'",
        "worker-src": "'self'",
        "report-uri": "/csp_report",
        "frame-ancestors": "'none'",
        "form-action": "'self'",
        "frame-src": "'none'",
    })

def create_recipe():
    # if request.method == "GET" and request.args.get("url"):
    #     url = request.args.get("url", "")
    #     return redirect(url, code=302)
    
    if not session.get("isLoggedIn"):
        return redirect("/index.html", code=302)

    username = session.get("username")

    if request.method == "POST":
        name = request.form["name"]
        cook_time = request.form["cooktime"]
        difficulty = request.form["diff"]
        region = request.form["region"]
        description = request.form["desc"]
        user_id = session.get("user_id")
        ingredients = request.form["ingredients"]
        steps = request.form["steps"]
        rHandler.insert_recipe(name, cook_time, difficulty, region, description, user_id, ingredients, steps)
        return redirect("/dashboard.html", code=302)
    else:
        # dbHandler.listFeedback()
        return render_template("/recipies/create.html", state=True, value=username)

@app.route("/dashboard.html", methods=["GET"])
@csp_header({
        "base-uri": "self",
        "default-src": "'self' 'unsafe-inline'",
        "script-src": "'self'",
        "img-src": "*",
        "media-src": "'self'",
        "font-src": "self",
        "object-src": "'self'",
        "child-src": "'self'",
        "connect-src": "'self'",
        "worker-src": "'self'",
        "report-uri": "/csp_report",
        "frame-ancestors": "'none'",
        "form-action": "'self'",
        "frame-src": "'none'",
    })

def dashboard():
    if not session.get("isLoggedIn"):
        return redirect("/index.html", code=302)
    
    user_id = session.get("user_id")
    recipies = rHandler.list_recipe(user_id)
    favourites = rHandler.list_favourites(user_id)
    return render_template("/dashboard.html", state=True, favourites=favourites, recipies=recipies)

@app.route("/search.html", methods=["POST", "GET"])
@csp_header({
        "base-uri": "self",
        "default-src": "'self' 'unsafe-inline'",
        "script-src": "'self'",
        "img-src": "*",
        "media-src": "'self'",
        "font-src": "self",
        "object-src": "'self'",
        "child-src": "'self'",
        "connect-src": "'self'",
        "worker-src": "'self'",
        "report-uri": "/csp_report",
        "frame-ancestors": "'none'",
        "form-action": "'self'",
        "frame-src": "'none'",
    })

def search_recipe():
    # if request.method == "GET" and request.args.get("url"):
    #     url = request.args.get("url", "")
    #     return redirect(url, code=302)
    
    if not session.get("isLoggedIn"):
        return redirect("/index.html", code=302)

    # username = session.get("username")

    if request.method == "POST":
        query = request.form["query"]     
        recipies = rHandler.search_recipe(query)   
        return render_template("/recipies/search.html", state=True, recipies=recipies)
    else:
        # dbHandler.listFeedback()
        return render_template("/recipies/search.html", state=True)

@app.route("/view.html", methods=["GET"])
@csp_header({
        "base-uri": "self",
        "default-src": "'self' 'unsafe-inline'",
        "script-src": "'self'",
        "img-src": "*",
        "media-src": "'self'",
        "font-src": "self",
        "object-src": "'self'",
        "child-src": "'self'",
        "connect-src": "'self'",
        "worker-src": "'self'",
        "report-uri": "/csp_report",
        "frame-ancestors": "'none'",
        "form-action": "'self'",
        "frame-src": "'none'",
    })
def view():
    if not session.get("isLoggedIn"):
        return redirect("/index.html", code=302)
    
    r_id = (request.args.get('r_id'))
    user_id = session.get("user_id")
    recipe = rHandler.view_recipe(r_id, user_id)
    num_favourites = rHandler.count_favourites(r_id)
    return render_template("/recipies/view.html", state=True, recipe=recipe, num_favourites=num_favourites)

@app.route("/favourite.html", methods=["GET"])
def favourite():
    if not session.get("isLoggedIn"):
        return redirect("/index.html", code=302)
    
    user_id = session.get("user_id")
    r_id = (request.args.get('r_id'))
    # f = rHandler.check_favorite(user_id, r_id)
    rHandler.favourite(user_id,r_id)
    return redirect("/view.html?r_id=" + r_id, code=302)

@app.route("/remove_favourite.html", methods=["POST"])
def remove_favourite():
    if not session.get("isLoggedIn"):
        return redirect("/index.html", code=302)
    
    f_id = request.form['f_id']
    rHandler.remove_favourite(f_id)
    return redirect("/dashboard.html", code=302)

@app.route("/topten.html", methods=["GET"])
@csp_header({
        "base-uri": "self",
        "default-src": "'self' 'unsafe-inline'",
        "script-src": "'self'",
        "img-src": "*",
        "media-src": "'self'",
        "font-src": "self",
        "object-src": "'self'",
        "child-src": "'self'",
        "connect-src": "'self'",
        "worker-src": "'self'",
        "report-uri": "/csp_report",
        "frame-ancestors": "'none'",
        "form-action": "'self'",
        "frame-src": "'none'",
    })

def topten():
    if not session.get("isLoggedIn"):
        return redirect("/index.html", code=302)
    
    recipies = rHandler.topten_recipe()
    return render_template("recipies/topten.html", state=True, recipies=recipies)

@app.route("/delete_recipe.html", methods=["POST"])
def delete_recipie():
    if not session.get("isLoggedIn"):
        return redirect("/index.html", code=302)
    
    user_id = session.get("user_id")
    r_id = request.form['r_id']
    rHandler.delete_recipe(r_id, user_id)
    return redirect("/dashboard.html", code=302)

if __name__ == "__main__":
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
    app.run(debug=True, host="0.0.0.0", port=5001)
