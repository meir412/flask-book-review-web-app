# CS50 - Web Programming with Python and JavaScript

## Project 1

This website was designed for the second project in the Harvard cs50 web programming in Python and JS course.
The website is a book reviewing website, containing data about 5000 different books.
I'd be very happy to receive feedback, issues and collaborations, thanks for visiting!

### Development

* This website was built using HTML and Sass (compiled to CSS)
* The backend was built using python 3.7 and the flask framework.
* The web app is configured to work with a postgresql database using python modules psycopg2 and sqlalchemy
* In order to run locally, clone the repository and install python modules from `requirements.txt`.
* After that define an env variable named `DATABASE_URL` to point at your postgres db, and another env variable named `FLASK_APP` and set its value to `application.py`.
* You can now execute:
    ```console
    $ flask run
    ```
    in order to run the website on http://127.0.0.1:5000



### Usage

* See short video explanation here: https://youtu.be/uHMZgsUX538  

The website includes an authentication system and is only accesable to logged in users,
Anyone can provide credentials and register a new user in order to later log in with these
credentials. 

Once logged in, users arrive at the home page and can search for a book to review by its title, author or isbn number.
The website will redirect users to the results page containing all the books that matched the search.

Users can then click on any book in order to access it's details: title, author, year, isbn number. The website also uses the GoodReads API (www.goodreads.com) in order to display the number of reviews and the average rate that the book has received on GoodReads (if available).
On the book detail page users will also view all the reviews and ratings that have been submitted for this book on the website.
Users will also be able to submit their own review for the book, including a rate between 1 to 5 and a textual review (A user is only allowed to review each book once).

### API

Apart from the website there is also an API which can be accessed via `/api/<book isbn number>`, which returns a json with all the details about the book that can be found on the website. If the book isn't found in the websites database, a 404 error will be returned.