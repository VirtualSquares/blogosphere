from flask import Flask, render_template, request, redirect, flash, session
from pymongo.mongo_client import MongoClient
from passlib.hash import sha256_crypt
from bson import ObjectId
import datetime, os
from dotenv import load_dotenv
app_path = os.path.join(os.path.dirname(__file__), '.')
dotenv_path = os.path.join(app_path, '.env')
load_dotenv(dotenv_path)
app = Flask(__name__)
## app.config.update(SECRET_KEY = os.environ.get("APP_SECRET_KEY"))
app.secret_key = os.environ["APP_SECRET_KEY"]

uri = os.environ["MONGO_DB_URL"]

client = MongoClient(uri)

db = client.blogosphere

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        hash = sha256_crypt.hash(request.form["password"])
        if db.users.count_documents({"username": request.form["username"]}) == 0:
            db.users.insert_one({"username": request.form["username"], "password": hash, "email": request.form["email"]})
            flash("User registered succesfully, please log in!")
            return redirect("/login")
        else:
            flash("That username is already taken!")
            return redirect("/register")

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        user = db.users.find_one({"username": request.form["username"]})
        if user is None:
            flash("User not found!")
            return redirect("/login")
        else:
            if sha256_crypt.verify(request.form["password"], user["password"]) == True:
                session["username"] = request.form["username"]
                flash("User logged in succesfully, start blogging!")
                return redirect("/main")
            else:
                flash("Login unsuccesful, please try again!")
                return redirect("/login")

@app.route("/forgot") 
def forgot():
    return render_template("forgot-password.html")

@app.route("/browse", methods = ["GET", "POST"])
def browse():
    if request.method == "GET":
        previousblogs = db.blogs.find()
        previousblogs = list(previousblogs)
        return render_template("browse.html", previousblogs = previousblogs)
    if request.method == "POST":
        return redirect("/browse")

@app.route("/update/<blog_id>", methods = ["GET", "POST"])
def update(blog_id):
    blog = db.blogs.find_one({"_id":ObjectId(blog_id)})
    if request.method == "POST":
        user = db.users.find_one({"username":session["username"]})
        db.blogs.update_one({"_id":ObjectId(blog_id)},{"$set":{"Title": request.form["title"], "Blog": request.form["blogcontent"], "Updated at": datetime.datetime.now(), "ID": str(user["_id"])}})
        return redirect("/main")
    return render_template("update_blog.html", blog = blog)

@app.route("/view/<blog_id>", methods = ["GET", "POST"])
def view(blog_id):
    if request.method == "GET":
        blog = db.blogs.find_one({"_id":ObjectId(blog_id)})
        commentlist = db.comments.find({"blog_id": blog_id})
        return render_template("view.html", blog = blog, commentlist = list(commentlist))
    if request.method == "POST":
        db.comments.insert_one({"Comment": request.form["commentarea"], "blog_id": blog_id})
        return redirect("/view/" + str(blog_id))

@app.route("/main", methods = ["GET", "POST"])
def main():
    if request.method == "GET":
        if "username" not in session:
            return redirect("/login")
        user = db.users.find_one({"username":session["username"]})
        previousblogs = db.blogs.find({"ID":str(user["_id"])})
        previousblogs = list(previousblogs)
        return render_template("blog-main.html", previousblogs = previousblogs)
    if request.method == "POST":
        user = db.users.find_one({"username":session["username"]})
        db.blogs.insert_one({"Title": request.form["title"], "Blog": request.form["blogcontent"], "Created at": datetime.datetime.now(), "Updated at": datetime.datetime.now(), "ID": str(user["_id"])})
        return redirect("/main")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
    
if __name__ == "__main__":
    app.run(debug = True)
