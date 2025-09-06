import matplotlib
matplotlib.use("Agg")  # fix lỗi Tkinter khi chạy Flask
import matplotlib.pyplot as plt

from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import os
from werkzeug.utils import secure_filename
from PIL import Image
import shutil

# Import các hàm của bạn
from steganography.extract import extract_text
from analysis.rs_analysis import rs_analysis

# ----------------------
# Config
# ----------------------
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = "stego-secret-key"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER


# ----------------------
# Routes
# ----------------------
@app.route("/")
def index():
    return render_template("index.html")

# ---- Giải mã tin ----
@app.route("/extract", methods=["POST"])
def extract_route():
    if "image" not in request.files or request.files["image"].filename == "":
        flash("Chưa chọn ảnh stego.")
        return redirect(url_for("index"))

    image_file = request.files["image"]
    filename = secure_filename(image_file.filename)
    input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    
    # FIX: Save file without modification
    image_file.seek(0)
    with open(input_path, 'wb') as f:
        shutil.copyfileobj(image_file, f)

    try:
        message = extract_text(input_path)
    except Exception as e:
        flash(f"Lỗi khi giải mã: {e}")
        return redirect(url_for("index"))

    return render_template("result_extract.html", message=message)


# ---- Phân tích RS ----
@app.route("/analysis", methods=["POST"])
def analysis_route():
    if "image" not in request.files or request.files["image"].filename == "":
        flash("Chưa chọn ảnh.")
        return redirect(url_for("index"))

    image_file = request.files["image"]
    filename = secure_filename(image_file.filename)
    input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    
    # FIX: Save file exactly as uploaded, no modification
    print("=== DEBUG FILE SAVE ===")
    image_file.seek(0)
    uploaded_size = len(image_file.read())
    print(f"Uploaded file size: {uploaded_size} bytes")
    
    image_file.seek(0)
    with open(input_path, 'wb') as f:
        shutil.copyfileobj(image_file, f)
    
    saved_size = os.path.getsize(input_path)
    print(f"Saved file size: {saved_size} bytes")
    print(f"Sizes match: {uploaded_size == saved_size}")
    
    # Additional check: verify image loads correctly
    try:
        test_img = Image.open(input_path)
        print(f"Image format: {test_img.format}, mode: {test_img.mode}, size: {test_img.size}")
        pixels = list(test_img.getdata())
        print(f"First 5 pixels: {pixels[:5]}")
    except Exception as e:
        print(f"Image load error: {e}")

    plot_name = f"rs_plot_{filename.split('.')[0]}.png"
    plot_path = os.path.join(app.config["OUTPUT_FOLDER"], plot_name)

    try:
        from analysis.rs_analysis import rs_analysis
        result = rs_analysis(input_path, plot_path)
    except Exception as e:
        flash(f"Lỗi khi phân tích: {e}")
        return redirect(url_for("index"))

    return render_template(
        "result_analysis.html",
        R=result["R"],
        S=result["S"],
        R_ratio=result["R_ratio"],
        S_ratio=result["S_ratio"],
        conclusion=result["conclusion"],
        plot=plot_name,
        encoded_percent=result.get("encoded_percent", 0)
    )


# ----------------------
# File serving
# ----------------------
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/outputs/<path:filename>")
def output_file(filename):
    return send_from_directory(app.config["OUTPUT_FOLDER"], filename)

# ----------------------
# Main
# ----------------------
if __name__ == "__main__":
    app.run(debug=True)