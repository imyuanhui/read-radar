from flask_sqlalchemy import SQLAlchemy
from flask import redirect
from sqlalchemy import func

db = SQLAlchemy()

book_genre_table = db.Table(
    'book_genre',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    author = db.Column(db.String(80), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    genres = db.relationship('Genre', secondary=book_genre_table, backref='books')

    def __repr__(self):
        return f"Title: {self.title}, Author: {self.author}, Year: {self.year}"
    
    @staticmethod
    def get_all_books():
        return Book.query.order_by(Book.title).all()
    
    @staticmethod
    def find_book_by_title(t):
        return Book.query.filter_by(title=t).first()
    
    @staticmethod
    def find_book_by_id(id):
        return Book.query.filter_by(id=id).first()

    @staticmethod
    def add_new_book(title, author, year, genres):
        # Check if the book is already existed in the database
        existing_book = Book.find_book_by_title(title)
        if existing_book:
            return f"Book {title} already in the database."
        else:
            new_book = Book(title=title, author=author, year=year)
            # Add genres to the book
            for g in genres:
                existing_genre = Genre.find_genre(g)
                if existing_genre:
                    new_book.genres.append(existing_genre)
                else:
                    new_genre = Genre.add_new_genre(g)
                    new_book.genres.append(new_genre)
            
            try:
                db.session.add(new_book)
                db.session.commit()
            except Exception as e:
                print(f"Error: {e}")
                return f"Error: {e}"
    
    @staticmethod
    def import_new_book(line):
        info = [piece.strip() for piece in line.split(",")]
        if len(info) < 4 or '[' not in line or ']' not in line:
            raise ValueError('Invalid file line format.')
        title = info[0]
        author = info[1]
        year = int(info[2])
        genres = [genre.strip('[]') for genre in info[3:]]
        return Book.add_new_book(title, author, year, genres)
    
    @staticmethod
    def delete_book(id):
        book = Book.query.get_or_404(id)
        try:
            db.session.delete(book)
            db.session.commit()
        except Exception as e:
            return f"Error: {e}"
    
    @staticmethod
    def update_book(id, new_title=None, new_author=None, new_year=None, new_genres=None):
        book = Book.query.get_or_404(id)
        book.title = new_title if new_title else book.title
        book.author = new_author if new_author else book.author
        book.year = new_year if new_year else book.year
        
        if new_genres is not None:
            book.genres.clear()

            for g in new_genres:
                existing_genre = Genre.find_genre(g)
                if existing_genre:
                    book.genres.append(existing_genre)
                else:
                    new_genre = Genre.add_new_genre(g)
                    book.genres.append(new_genre)
        try:
            db.session.commit()
        except Exception as e:
            return f"Error: {e}"
    
    @staticmethod
    def export_books(filepath):
        with open(filepath, 'w') as f:
            for book in Book.get_all_books():
                line = f"{book.title}, {book.author}, {book.year}, {[str(g) for g in book.genres]}\n"
                f.write(line)
    
    @staticmethod
    def top_authors(limit):
        authors = db.session.query(Book.author, func.count(Book.id).label("count")).group_by(Book.author).order_by(func.count(Book.id).desc()).limit(limit).all()
        top_authors = [(author, count) for author, count in authors]
        return top_authors

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"{self.genre}"
    
    @staticmethod
    def get_all_genres():
        return Genre.query.order_by('genre').all()
    
    @staticmethod
    def find_genre(g):
        return Genre.query.filter_by(genre=g).first()
    
    @staticmethod
    def add_new_genre(g):
        new_genre = Genre(genre=g)
        try:
            db.session.add(new_genre)
            db.session.commit()
            return new_genre
        except Exception as e:
            print(f"Error: {e}")
            return f"Error: {e}"
    
    @staticmethod
    def genre_distribution(limit):
        genres = db.session.query(Genre.genre, func.count(book_genre_table.c.book_id).label("count")).join(book_genre_table, Genre.id == book_genre_table.c.genre_id).group_by(Genre.genre).order_by(func.count(book_genre_table.c.book_id).desc()).limit(limit).all()
        return genres