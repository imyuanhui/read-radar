from flask import Flask, render_template, redirect, request, send_from_directory, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from models import db, Book, Genre
import os
import plotly.graph_objects as go

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

def draw_radar_chart(labels, values):
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=labels,
        fill='toself',
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(values) + 1] if values else [0, 1]
            ),
        ),
        showlegend=False
    )

    return fig

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

@app.route("/download", methods=["GET", "POST"])
def download_file():
    if request.method == "POST":
        filename = request.form["filename"].strip()
        if "." in filename:
            filename = filename.split(".")[0]
        filename = filename.strip()

        if not filename:
            filename = "readradar_myBooks.txt"
        try:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename}.txt")
            Book.export_books(filepath)
            return send_from_directory(app.config['UPLOAD_FOLDER'], f"{filename}.txt", as_attachment=True)
        except Exception as e:
            return f"Error: {e}"
    return render_template("download_form.html")
        
@app.route("/delete/<int:id>")
def delete(id:int):
    try:
        Book.delete_book(id)
        return redirect("/")
    except Exception as e:
        return f"Error: {e}"

@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id:int):
    book_to_update = Book.find_book_by_id(id)
    if book_to_update:
        if request.method == "POST":
            data = request.form
            genres = [genre.strip() for genre in data['genres'].split(",")]
            try:
                result = Book.update_book(
                    id,
                    new_title=data.get('title'),
                    new_author=data.get('author'),
                    new_year=data.get('year'),
                    new_genres=genres
                )
                if isinstance(result, str) and result.startswith("Error"):
                    return result, 400
                return redirect("/")
            except Exception as e:
                return f"Error: {e}", 500
        else:
            return render_template("update.html", book=book_to_update)

@app.route("/preferences")
def preferences():
    try:
        top3_authors = Book.top_authors(3)
        # Analyse genre distribution
        top6_genres = Genre.genre_distribution(6)
        chart = draw_radar_chart([g[0] for g in top6_genres], [g[1] for g in top6_genres])
        return render_template("preferences.html", authors=top3_authors, chart=chart.to_html())
    except Exception as e:
        return f"Error: {e}"

@app.route("/recommend/<int:id>")
def recommend(id:int):
    try:
        book = Book.find_book_by_id(id)
        return render_template("recommendation.html", similar_books = Book.find_similar_books(id), book=book)
    except Exception as e:
        return f"Error: {e}"

if __name__ in "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)