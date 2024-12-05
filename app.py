from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from models import db, Book, Genre
import os

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["UPLOAD_FOLDER"] = "uploads"  # Folder for uploaded files
app.config["ALLOWED_EXTENSIONS"] = {"txt"}  # Allowed file extensions
db.init_app(app)

# Check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route("/", methods=['POST', 'GET'])
def home():
    # Add a new record
    if request.method == 'POST':
        data = request.form
        genres = [genre.strip() for genre in data['genres'].split(",")]
        Book.add_new_book(data['title'], data['author'], data['year'], genres)
        
    # Get all records
    if request.method == 'GET':
        books = Book.get_all_books()
        return render_template("index.html", books=books)

    return render_template("index.html")

@app.route("/upload", methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Save the file temporarily
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        try:
            with open(filename, 'r') as f:
                for line in f.readlines():
                    info = [piece.strip() for piece in line.split(",")]
                    if len(info) < 4 or '[' not in line or ']' not in line:
                        raise ValueError('Invalid file line format.')
                    title = info[0]
                    author = info[1]
                    year = int(info[2])
                    genres = [genre.strip('[]') for genre in info[3:]]
                    try:
                        Book.add_new_book(title, author, year, genres)
                    except ValueError as e:
                        print('Skip invalid line:', e)
        except Exception as e:
            print(f"Error: {e}")

    return redirect("/")

if __name__ in "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)