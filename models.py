from flask_sqlalchemy import SQLAlchemy
from flask import redirect
from sqlalchemy import func
import logging
import re

logging.basicConfig(level=logging.ERROR, filename='app.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

db = SQLAlchemy()

# Association table for the many-to-many relationship between books and genres
book_genre_table = db.Table(
    'book_genre',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)

class Book(db.Model):
    """
    Model representing a book, with fields for title, author, year, and a many-to-many relationship with genres.
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    author = db.Column(db.String(80), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    genres = db.relationship('Genre', secondary=book_genre_table, backref='books')

    def __repr__(self):
        return f"Title: {self.title}, Author: {self.author}, Year: {self.year}"
    
    @staticmethod
    def get_all_books():
        # return Book.query.order_by(Book.title).paginate(page=page, per_page=per_page, error_out=False)
        return Book.query.order_by(Book.title).all()
    
    @staticmethod
    def find_book_by_title(t):
        return Book.query.filter_by(title=t).first()
    
    @staticmethod
    def find_book_by_id(id):
        return Book.query.filter_by(id=id).first()

    @staticmethod
    def add_new_book(title, author, year, genres):
        """
        Add a new book to the database, including its genres.
        If a genre does not exist, it will be created.
        """
        if Book.find_book_by_title(title):
            return f"Book {title} already in the database."
        
        new_book = Book(title=title, author=author, year=year)

        # Fetch existing genres in one query
        existing_genres = {g.genre: g for g in Genre.query.filter(Genre.genre.in_(genres)).all()}

        for g in genres:
            if g in existing_genres:
                new_book.genres.append(existing_genres[g])
            else:
                new_genre = Genre.add_new_genre(g)
                new_book.genres.append(new_genre)
            
        try:
            db.session.add(new_book)
            db.session.commit()
            return new_book
        except Exception as e:
            db.session.rollback()
            logger.error(f'Database error: {e}')
            return f"Error: {e}"
    
    @staticmethod
    def import_new_book(line):
        """
        Import a book from a line in a text file.
        The line should be in the format: title, author, year, [genre1, genre2, ...].
        """
        match = re.match(r'^(.+),\s*(.+),\s*(\d{4}),\s*\[(.+)]$', line.strip())
        if not match:
            raise ValueError('Invalid file line format.')
        
        title, author, year, genres_str = match.groups()
        genres = [g.strip() for g in genres_str.split(",")]

        return Book.add_new_book(title, author, int(year), genres)
        # info = [piece.strip() for piece in line.split(",")]
        # if len(info) < 4 or '[' not in line or ']' not in line:
        #     raise ValueError('Invalid file line format.')
        # title = info[0]
        # author = info[1]
        # year = int(info[2])
        # genres = [genre.strip('[]') for genre in info[3:]]
        # return Book.add_new_book(title, author, year, genres)
    
    @staticmethod
    def delete_book(id):
        book = Book.query.get_or_404(id)
        try:
            db.session.delete(book)
            db.session.commit()
        except Exception as e:
            logger.error(f'Database error: {e}')
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
            logger.error(f'Database error: {e}')
            return f"Error: {e}"
    
    @staticmethod
    def export_books(filepath):
        """Export all books to a text file in a specified format."""
        with open(filepath, 'w') as f:
            for book in Book.get_all_books():
                line = f"{book.title}, {book.author}, {book.year}, {[str(g) for g in book.genres]}\n"
                f.write(line)
    
    @staticmethod
    def top_authors(limit):
        """Get the top authors based on the number of books in the database."""
        authors = db.session.query(Book.author, func.count(Book.id).label("count")).group_by(Book.author).order_by(func.count(Book.id).desc()).limit(limit).all()
        top_authors = [(author, count) for author, count in authors]
        return top_authors
    
    @staticmethod
    def find_similar_books(id):
        """
        Find books similar to a given book based on the author and shared genres.
        """
        target = Book.find_book_by_id(id)
        if not target:
            return f"Book not found in the database.", 404
        
        # Fetch books by same author or matching genres
        similar_books = Book.query.filter(
            (Book.author == target.author) | 
            (Book.genres.any(Genre.id.in_([g.id for g in target.genres])))
        ).filter(Book.id != target.id).all()
        
        # Sort based on similarity score (author match = highest priority)
        sorted_books = sorted(
            similar_books,
            key=lambda book: (
                0 if book.author == target.author else 1 + (len(target.genres) - len(set(target.genres) & set(book.genres))) / len(target.genres)
            )
        )
        return sorted_books[:5]

class Genre(db.Model):
    """
    Model representing a genre, with a unique genre name and its relationship with books.
    """
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
            logger.error(f'Database error: {e}')
            return f"Error: {e}"
    
    @staticmethod
    def genre_distribution(limit):
        """Get the genre distribution of books, sorted by popularity."""
        genres = db.session.query(Genre.genre, func.count(book_genre_table.c.book_id).label("count")).join(book_genre_table, Genre.id == book_genre_table.c.genre_id).group_by(Genre.genre).order_by(func.count(book_genre_table.c.book_id).desc()).limit(limit).all()
        return genres