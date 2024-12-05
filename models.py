from flask_sqlalchemy import SQLAlchemy
from flask import redirect

db = SQLAlchemy()

book_genre_table = db.Table(
    'book_genre',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    author = db.Column(db.String(80), unique=True, nullable=False)
    year = db.Column(db.Integer)
    genres = db.relationship('Genre', secondary=book_genre_table, backref='books')

    def __repr__(self):
        return f"Title: {self.title}, Author: {self.author}, Year: {self.year}"
    
    @staticmethod
    def get_all_books():
        return Book.query.order_by(Book.title).all()

    @staticmethod
    def add_new_book(title, author, year, genres):
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
            return redirect("/")
        except Exception as e:
            print(f"Error: {e}")
            return f"Error: {e}"

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return self.genre
    
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



# class Book:
#     def __init__(self, title, author, year, genres):
#         self.title = title
#         self.author = author
#         self.year = year
#         self.genres = genres
        
#     def __str__(self):
#         return f"Title: {self.title}, Author: {self.author}, Year: {self.year}, Genres: {self.genres}"
    
#     def __repr__(self):
#         return self.__str__()

#     def load_from_file_line(line):
#         info = [piece.strip() for piece in line.split(",")]
#         if len(info) < 4 or '[' not in line or ']' not in line:
#             raise ValueError('Invalid file line format.')
#         title = info[0]
#         author = info[1]
#         year = int(info[2])
#         genres = [genre.strip('[]') for genre in info[3:]]
#         return Book(title, author, year, genres)