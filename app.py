from flask import Flask, request, render_template, send_file
import fitz
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def remove_blank_pages(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    page_numbers = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text().strip()

        if not text:
            page_numbers.append(page_num)

    for page_num in reversed(page_numbers):
        doc.delete_page(page_num)

    doc.save(output_pdf)
    doc.close()

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', message='No file part')
        
        file = request.files['file']
        
        if file.filename == '':
            return render_template('index.html', message='No selected file')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            output_filepath = os.path.join(app.config['OUTPUT_FOLDER'], 'output_' + filename)
            remove_blank_pages(filepath, output_filepath)
            
            return send_file(output_filepath, as_attachment=True)
    
    return render_template('index.html', message='Upload a PDF file')

if __name__ == '__main__':
    app.run(debug=True)

