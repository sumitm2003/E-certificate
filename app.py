from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import io
import os

app = Flask(__name__)

# Load participant data
df = pd.read_csv("participants.csv", encoding='utf-8-sig')  # CSV columns: bib_no,name,distance

@app.route('/')
def home():
    return render_template("index.html")  # HTML form to input Bib No.

@app.route('/generate', methods=['POST'])
def generate_certificate():
    bib_no = request.form['bib_no'].strip()
    row = df[df['bib_no'].astype(str) == bib_no]

    if row.empty:
        return "❌ Bib Number Not Found. Please check your entry."

    name = row.iloc[0]['name']
    distance = row.iloc[0]['distance']

    # Load certificate background
    img = Image.open("certificate_template.jpg")
    draw = ImageDraw.Draw(img)

    # Load fonts from the fonts folder
    font_path = os.path.join("fonts", "DejaVuSans-Bold.ttf")
    font_large = ImageFont.truetype(font_path, 56)   # For Name
    font_medium = ImageFont.truetype(font_path, 40)  # For Distance

    # -------- Draw Name (centered) --------
    name_text = name.upper()
    name_bbox = draw.textbbox((0, 0), name_text, font=font_large)
    name_w = name_bbox[2] - name_bbox[0]
    name_x = (img.width - name_w) // 2
    name_y = 990
    draw.text((name_x, name_y), name_text, font=font_large, fill="black")

    # -------- Draw distance sentence (centered) --------
    sentence = f"Has Successfully Completed the {distance.upper()} "
    sentence_bbox = draw.textbbox((0, 0), sentence, font=font_medium)
    sentence_w = sentence_bbox[2] - sentence_bbox[0]
    sentence_x = (img.width - sentence_w) // 2
    sentence_y = 1100
    draw.text((sentence_x, sentence_y), sentence, font=font_medium, fill="black")

    # Return as downloadable image
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png', as_attachment=True, download_name=f"{name}_certificate.png")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
