# ReadRadar

ReadRadar is a Flask-based web application that allows users to manage their personal book records. Users can add, update, delete, and view book records, upload book files for bulk import, download their book list, analyze reading preferences, and find similar books based on their library.

---

## Table of Contents

- [Release Version](#release-version)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Usage](#usage)

---

## Release Version

- **Version**: 1.0.0
- **Release Date**: December 7, 2024

---

## 🚀 Tech Stacks

### Backend

- **Flask**: Lightweight web framework for building the application.
- **Flask-SQLAlchemy**: ORM for managing database models and queries.
- **SQLite**: Database for storing book and genre information.

### Frontend

- **HTML/CSS**: For structuring and styling the user interface.
- **Jinja2**: Flask’s templating engine to dynamically render HTML.

### Tools & Libraries

- **Matplotlib**: For generating radar charts to visualize genre preferences.
- **Werkzeug**: For secure handling of uploaded files.

---

## Features

- **CRUD Operations:** Add, update, delete, and list books.
- **Bulk Import & Export:** Upload text files for adding multiple books and download book data.
- **Recommendation System:** Get book recommendations based on the selected book's author and genres.
- **Reading Preferences Analysis:** Visualize top authors and genre distribution using radar charts.
- **Genre Management:** Automatically handle genres when adding or updating books.

---

## Getting Started

### Prerequisites

Ensure you have the following installed:

- Python 3.7+
- Flask
- SQLite (included in Python standard library)

### Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/your-username/readradar.git
   cd readradar
   ```

2. Set up a virtual environment (optional but recommended):

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:

   ```bash
   python app.py
   ```

5. Access the application at http://127.0.0.1:5000

---

## Project Structure

    ```php
    ReadRadar/
    │
    ├── app.py                # Main application file
    ├── models.py             # Database models for Book and Genre
    ├── utils.py              # Utility functions for file handling and charts
    ├── templates/            # HTML templates for Flask routes
    |   |—— base.html         # Base template
    │   ├── index.html        # Homepage template
    │   ├── update.html       # Update book form template
    │   ├── preferences.html  # Reading preferences analysis page
    │   ├── recommendation.html # Book recommendation page
    │   └── download_form.html # File download form
    ├── static/               # Static files (CSS, images)
    │   |── styles.css        # Application styling
    |   └── images/           # Directory storing images
    ├── uploads/              # Folder for storing cached uploaded files
    └── requirements.txt      # Python dependencies
    ```

---

## Usage

### Navigate to homepage

- Click the icon "ReadRadar" on the left top to redirect to homepage.

### Adding Books

- Use the form on the homepage to add books.
- Enter the title, author, publication year, and genres separated by commas.
- Click "Add a New Record" button to add books manually.

### Updating Books

- Click the "Edit" button next to a book to modify its details.
- Update fields as needed and save changes.

### Deleting Books

- Click the "Delete" button to remove a book permanently.

### Bulk Import

- Upload a text file with book data in the format:
  `css
Title, Author, Year, [Genre1, Genre2, ...]
`
- Use the "Import Records From File" button to import the file.

### Export Books

- Click the button "Export All Records" to redirect to the download page.
- Enter filename and click "Export Books" to export the book list to a text file.

### View Preferences

- Click the button "My Reading Preferences" to view your top authors and genres, including a radar chart.

### Recommendations

- Click the "Find Similar Books" button next to a book to get suggestions based on its author and genres.
