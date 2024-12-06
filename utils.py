import os
from flask import current_app
import plotly.graph_objects as go

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def cleanup_upload_folder():
    """Remove all files from the upload folder."""
    files = os.listdir(current_app.config["UPLOAD_FOLDER"])
    for f in files:
        os.remove(os.path.join(current_app.config["UPLOAD_FOLDER"], f))

def draw_radar_chart(labels, values):
    """Generate a radar chart."""
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
