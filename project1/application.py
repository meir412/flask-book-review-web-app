import os

from flask import Flask
from flask import session
from flask import render_template
from flask import request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

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

    books = db.execute("SELECT * FROM books").fetchall()
    return render_template("index.html")


@app.route("/results", methods=['POST'])
def results():

    search = request.form['book_search']
    books = db.execute(f"""
        select * from books where author like '%{search}%'
        or title like '%{search}%' or isbn like '%{search}%';
    """).fetchall()

    if len(books) == 0:
        return render_template("error.html")

    else:
        return render_template("results.html", books=books, search=search)


@app.route("/books/<string:isbn>", methods = ['POST', 'GET'])
def bookDetail(isbn):

    book = db.execute(f"select * from books where isbn='{isbn}';").fetchone()

    reviews = db.execute(f"""
        select * from books join reviews
        on books.isbn = reviews.book
        where books.isbn='{isbn}';
    """).fetchall()

    if book is None:
        return render_template("error.html")

    if request.method == "GET":
        return render_template("book_detail.html", book=book, reviews=reviews)
    
    else:
        rate = request.form['rate']
        review = request.form['review']

        # TODO: once user functionality exists change 1 to <user.id> in query below
        db.execute(f"""
        INSERT INTO reviews (book, reviewer, rate, review)
        VALUES ('{isbn}', 1, {rate}, '{review}')
        """)

        db.commit()

        reviews = db.execute(f"""
            select * from books join reviews
            on books.isbn = reviews.book
            where books.isbn='{isbn}';
        """).fetchall()

        # TODO: don't render the form after insertion so user won't leave second review
        return render_template("book_detail.html", book=book, reviews=reviews)


@app.route("/api/<string:isbn>")
def apiBook(isbn):
    pass
    

@app.route("/login")
def logIn():
    pass
    
