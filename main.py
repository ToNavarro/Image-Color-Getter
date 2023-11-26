from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import os
import numpy as np
from PIL import Image
from werkzeug.utils import secure_filename
from sklearn.cluster import KMeans

app = Flask(__name__)

# Set maximum file size to 16MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_top_colors(image_path, num_colors=10):
    image = Image.open(image_path)
    image = image.convert('RGB')

    # Resize image to a reasonable size for processing
    image = image.resize((100, 100))

    # Flatten the image array
    pixels = np.array(image).reshape((-1, 3))

    # Use K-Means clustering to find dominant colors
    kmeans = KMeans(n_clusters=num_colors)
    kmeans.fit(pixels)

    # Get the RGB values of the cluster centers
    dominant_colors = kmeans.cluster_centers_

    # Convert RGB values to integers
    dominant_colors = dominant_colors.astype(int)

    # Convert the dominant colors to a list of tuples
    dominant_colors = [tuple(color) for color in dominant_colors]

    return dominant_colors


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash("No file part")
            return redirect(url_for('index'))

        uploaded_file = request.files['file']

        # If the user does not select a file
        if uploaded_file.filename == '':
            flash("No selected file")
            return redirect(url_for('index'))

        # Validate file type
        if not allowed_file(uploaded_file.filename):
            flash("Invalid file type")
            return redirect(url_for('index'))

        # Validate file size
        if len(uploaded_file.read()) > app.config['MAX_CONTENT_LENGTH']:
            flash("File size exceeds the limit")
            return redirect(url_for('index'))

        # Rewind the file cursor
        uploaded_file.seek(0)

        # Save the file
        filename = secure_filename(uploaded_file.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(image_path)

        # Get the top colors
        top_colors = get_top_colors(image_path)
        return render_template('result.html', filename=filename, top_colors=top_colors)

    return render_template('index.html')


@app.route("/uploads/<filename>")
def uploaded_img(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
