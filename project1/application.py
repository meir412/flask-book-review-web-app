import os
import json

from flask import Flask
from flask import jsonify
from flask import session
from flask import render_template
from flask import redirect
from flask import request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
import requests

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():

    if session.get('username') is None:
        return redirect('/login')

    books = db.execute("SELECT * FROM books").fetchall()
    return render_template("index.html")

@app.route("/registration",methods=['GET','POST'])
def registration():

    logged_in = False
    if session.get("username") is not None:
        logged_in = True
        username = session['username']
        return render_template("error.html", logged_in=logged_in, username=username)

    if request.method == "GET":
        return render_template("registration.html")
    
    else:
        username = request.form['username']
        pass1 = request.form['password1']
        pass2 = request.form['password2']
        error_username = False
        error_password = False

        # check that user doesnt already exist
        user = db.execute(f"""
            select * from users where username = '{username}';
        """)
        
        if user.rowcount > 0:
            error_username = True
            return render_template("registration.html", username = username, error_username = error_username)

        # check the passwords match
        if pass1 != pass2:
            error_password = True
            return render_template("registration.html", username = username, error_password=error_password)

        db.execute(f"""
            INSERT INTO users (username, password)
            VALUES ('{username}','{pass1}')
        """)
        db.commit()
        session["username"] = username
        return redirect("/")

@app.route("/login", methods=['GET', 'POST'])
def login():

    logged_in = False
    if session.get("username") is not None:
        logged_in = True
        username = session['username']
        return render_template("error.html", logged_in=logged_in, username=username)

    if request.method == 'GET':
        return render_template("login.html")
    
    username = request.form['username']
    password = request.form['password']
    error_no_user = False
    error_wrong_pass = False

    user = db.execute(f"""
        SELECT * FROM users
        WHERE username='{username}'
    """)

    # check if username exists in db
    if user.rowcount == 0:
        error_no_user = True
        return render_template("login.html", error_no_user = error_no_user)
    
    user = user.fetchone()

    # check if password matches password in db
    if user['password'] != password:
        error_wrong_pass = True
        return render_template("login.html", error_wrong_pass=error_wrong_pass, username=username)
    
    # TODO: add username to session
    session["username"] = username
    return redirect("/")


@app.route("/logout")
def logout():

    if session.get('username') is not None:
        session.pop('username')

    return redirect('/login')


@app.route("/results", methods=['POST'])
def results():

    if session.get('username') is None:
        return redirect('/login')

    search = request.form['book_search']
    books = db.execute(f"""
        select * from books where author like '%{search}%'
        or title like '%{search}%' or isbn like '%{search}%';
    """).fetchall()

    if len(books) == 0:
        return render_template("error.html", no_result=True)

    else:
        return render_template("results.html", books=books, search=search)


@app.route("/books/<string:isbn>", methods = ['POST', 'GET'])
def bookDetail(isbn):

    if session.get('username') is None:
        return redirect('/login')

    user_id = db.execute(f"select id from users where username='{session['username']}'").fetchone().id
    book = db.execute(f"select * from books where isbn='{isbn}';").fetchone()
    
    if book is None:
        return render_template("error.html")

    goodreads_data = requests.get("https://www.goodreads.com/book/review_counts.json",
        params={"key": os.getenv("GOODREADS_KEY"), "isbns": book['isbn']})
    
    gr_review_count = None
    gr_average_rate = None

    # check if book actually exists on goodreads
    if goodreads_data.status_code == 200:
        gr_review_count = goodreads_data.json()['books'][0]['work_ratings_count']
        gr_average_rate = goodreads_data.json()['books'][0]['average_rating'] 
    
    

    reviews = db.execute(f"""
        select * from books join reviews
        on books.isbn = reviews.book
        where books.isbn='{isbn}';
    """).fetchall()

    already_reviewed = False

    for review in reviews:
        if review.reviewer == user_id:
            already_reviewed = True
            break


    if request.method == "GET":
        return render_template("book_detail.html", book=book, reviews=reviews, already_reviewed=already_reviewed, gr_review_count=gr_review_count, gr_average_rate=gr_average_rate)
    
    else:
        rate = request.form['rate']
        review = request.form['review']
        username = session['username']

        user = db.execute(f"select id from users where username='{username}';").fetchone().id

        db.execute(f"""
        INSERT INTO reviews (book, reviewer, rate, review)
        VALUES ('{isbn}', {user}, {rate}, '{review}')
        """)

        db.commit()

        reviews = db.execute(f"""
            select * from books join reviews
            on books.isbn = reviews.book
            where books.isbn='{isbn}';
        """).fetchall()

        # don't render the form after insertion so user won't leave second review
        already_reviewed = True
        return render_template("book_detail.html", book=book, reviews=reviews, already_reviewed=already_reviewed, gr_review_count=gr_review_count, gr_average_rate=gr_average_rate)


@app.route("/api/<string:isbn>")
def apiBook(isbn):

    book = db.execute(f"select * from books where isbn='{isbn}';").fetchone()
    
    if book is None:
        return jsonify({'errorCode' : 404, 'message' : 'Book not found on website'})

    else:
        goodreads_data = requests.get("https://www.goodreads.com/book/review_counts.json",
        params={"key": os.getenv("GOODREADS_KEY"), "isbns": book['isbn']})
    
        gr_review_count = None
        gr_average_rate = None

        # check if book actually exists on goodreads
        if goodreads_data.status_code == 200:
            gr_review_count = goodreads_data.json()['books'][0]['work_ratings_count']
            gr_average_rate = goodreads_data.json()['books'][0]['average_rating']

        book_properties = {"title": book['title'], "author": book['author'],
            "year": book['year'], "isbn": isbn, "review_count": gr_review_count,
            "average_score": gr_average_rate}

        return jsonify(book_properties) 

    