from datetime import date
from flask import Flask, render_template, request, flash, redirect, url_for
from data_models import db, Author, Book

from sqlalchemy import select

import os

app = Flask(__name__)

app.secret_key = "andres_supergeheimer_key"

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
db.init_app(app)

@app.route("/", methods=["GET"])
def index():
    sort_by = request.args.get("sort", "")
    order = request.args.get("order", "asc")
    search_query = request.args.get("search", "").strip()

    # Zulässige Sortierfelder
    if sort_by not in ("title", "author", "rating"):
        sort_by = ""

    # Zulässige Sortierrichtungen
    if order not in ("asc", "desc"):
        order = "asc"

    stmt = select(Book)

    # Stichwortsuche
    if search_query:
        stmt = stmt.where(
            Book.title.like(f"%{search_query}%")
        )

    # Sortierung
    if sort_by == "author":
        stmt = stmt.join(Book.author).order_by(
            Author.name.desc() if order == "desc" else Author.name.asc(),
            Book.title.asc()
        )

    elif sort_by == "rating":
        # Nicht bewertete Bücher (NULL) immer ans Ende
        stmt = stmt.order_by(
            Book.rating.is_(None).asc(),
            Book.rating.desc() if order == "desc" else Book.rating.asc(),
            Book.title.asc()
        )

    elif sort_by == "title":
        stmt = stmt.order_by(
            Book.title.desc() if order == "desc" else Book.title.asc()
        )

    else:
        # Standard-Sortierung: Titel aufsteigend
        stmt = stmt.order_by(Book.title.asc())

    books = db.session.execute(stmt).scalars().all()

    return render_template(
        "home.html",
        books=books,
        sort_by=sort_by,
        order=order,
        search_query=search_query
    )

@app.route("/add_author", methods =["GET"])
def open_add_author_form():
    return render_template("add_author.html")

@app.route("/add_author", methods =["POST"])
def add_author():
    data = request.form
    name = data.get("name")
    birth_date = data.get("birthdate")
    date_of_death = data.get("date_of_death")
    print(f"{name}, {birth_date}, {date_of_death}")
    new_author = Author(
        name=name,
        birth_date=date.fromisoformat(birth_date) if birth_date else None,
        date_of_death=date.fromisoformat(date_of_death) if date_of_death else None
    )
    db.session.add(new_author)
    db.session.commit()
    flash(f"Autor {name} wurde erfolgreich hinzugefügt!", "success")

    return redirect(url_for("add_author"))

@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        data = request.form

        isbn = data.get("isbn")
        title = data.get("title")
        publication_year = data.get("publication_year")
        author_id = data.get("author_id")

        new_book = Book(
            isbn=isbn,
            title=title,
            publication_year=publication_year,
            author_id=author_id
        )

        db.session.add(new_book)
        db.session.commit()

        flash(f"Book '{title}' was successfully added!", "success")

        return redirect(url_for("add_book"))

    authors = Author.query.all()

    return render_template("add_book.html", authors=authors)

@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    book = db.session.get(Book, book_id)

    if book is None:
        flash("Buch wurde nicht gefunden.")
        return redirect(url_for("index"))

    author = book.author
    title = book.title

    db.session.delete(book)
    db.session.commit()

    # Autor löschen, falls keine weiteren Bücher vorhanden sind
    if author and not author.books:
        db.session.delete(author)
        db.session.commit()
        flash(f'Buch "{title}" wurde samt Autor erfolgreich gelöscht.')
    else:
        flash(f'Buch "{title}" wurde erfolgreich gelöscht.')

    return redirect(url_for("index"))

@app.route("/book/<int:book_id>")
def book_detail(book_id):
    book = db.session.get(Book, book_id)

    if book is None:
        flash("Buch wurde nicht gefunden.")
        return redirect(url_for("index"))

    return render_template("book_detail.html", book=book)

@app.route("/author/<int:author_id>")
def author_detail(author_id):
    author = db.session.get(Author, author_id)

    if author is None:
        flash("Autor wurde nicht gefunden.")
        return redirect(url_for("index"))

    return render_template("author_detail.html", author=author)

@app.route("/author/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id):
    author = db.session.get(Author, author_id)

    if author is None:
        flash("Autor wurde nicht gefunden.")
        return redirect(url_for("index"))

    author_name = author.name

    db.session.delete(author)
    db.session.commit()

    flash(f'Autor "{author_name}" und seine Bücher wurden erfolgreich gelöscht.')

    return redirect(url_for("index"))

@app.route("/book/<int:book_id>/rate", methods=["POST"])
def rate_book(book_id):
    book = db.session.get(Book, book_id)

    if book is None:
        flash("Buch wurde nicht gefunden.")
        return redirect(url_for("index"))

    rating = request.form.get("rating", type=int)

    if rating is None or not 1 <= rating <= 10:
        flash("Bitte eine Bewertung zwischen 1 und 10 auswählen.")
        return redirect(url_for("book_detail", book_id=book_id))

    book.rating = rating
    db.session.commit()

    flash(f'Bewertung für "{book.title}" wurde gespeichert.')

    return redirect(url_for("book_detail", book_id=book_id))

# with app.app_context():
#   db.create_all()

if __name__ == '__main__':
    app.run(debug=True)


