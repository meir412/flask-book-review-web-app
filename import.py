"""
This module is part of the Books web application developed for the second project in the "CS50's Web Programming with Python
and JavaScript" course.
This module creates tables in a preconfigured postgresql database and populates one of the tables with data from the
'books.csv' file.
This module should be executed once when initializing the web application. It could also be run in order to reset the
database and repopulate with the csv file data.
"""

import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# initiate db
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# delete existing tables if already created before
db.execute("DROP TABLE IF EXISTS reviews")
db.execute("DROP TABLE IF EXISTS users")
db.execute("DROP TABLE IF EXISTS books")

# create tables
db.execute("""
    CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL,
    password VARCHAR NOT NULL
    );
""")

db.execute("""
    CREATE TABLE books (
    isbn  VARCHAR PRIMARY KEY,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year INTEGER NOT NULL
    );
""")

db.execute("""
    CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    book  VARCHAR REFERENCES books (isbn),
    reviewer  INTEGER REFERENCES users,
    rate INTEGER NOT NULL,
    review VARCHAR NOT NULL
    );
""")

# read data from csv and insert into books table
with open('books.csv') as csv_file:

    reader = csv.DictReader(csv_file)

    for row in reader:
        isbn = f"'{row['isbn']}'"                 # parse properly in order to comply with postgres query syntax
        title = row['title'].replace("'", "''")
        title = f"'{title}'"
        author = row['author'].replace("'", "''")
        author = f"'{author}'"
        year = row['year']
        db.execute(f"""
        INSERT INTO books (isbn, title, author, year)
        VALUES ({isbn}, {title}, {author}, {year});
        """)

# commit commands to db
db.commit()
