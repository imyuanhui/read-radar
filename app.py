from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from models import db, Book, Genre
import os

app = Flask(__name__)

# Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["ALLOWED_EXTENSIONS"] = {"txt"}

db.init_app(app)

# Utility functions
def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def cleanup_upload_folder():
    """Remove all files from the upload folder."""
    files = os.listdir(app.config["UPLOAD_FOLDER"])
    for f in files:
        os.remove(os.path.join(app.config["UPLOAD_FOLDER"], f))

# Routes
@app.route("/", methods=['POST', 'GET'])
def home():
    if request.method == 'POST':
        # Handle adding a new book
        data = request.form
        genres = [genre.strip() for genre in data['genres'].split(",")]
        try:
            Book.add_new_book(data['title'], data['author'], data['year'], genres)
            return redirect("/")
        except Exception as e:
            return f"Error: {e}"
        
    # Handle displaying all books
    if request.method == 'GET':
        cleanup_upload_folder() # clear cached files
        books = Book.get_all_books()
        return render_template("index.html", books=books)

@app.route("/upload", methods=['POST'])
def upload_file():
    if "file" not in request.files:
        return "No file uploaded", 400
    
    file = request.files["file"]

    if file.filename == "":
        return "No selected file", 400
    
    if file and not allowed_file(file.filename):
        return "File type not allowed", 400
    
    try:
        # Save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)  # Ensure upload folder exists
        file.save(filepath)

        with open(filepath, "r") as f:
            for line in f.readlines():
                try:
                    Book.import_new_book(line)
                except ValueError as e:
                    print("Skip invalid line:", e)
                except Exception as e:
                    print(f"Error processing line: {e}")
        return redirect('/')
    except Exception as e:
        return f"Error: {e}", 500

if __name__ in "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)