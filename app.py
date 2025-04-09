from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import PyPDF2
import io
import tabula
import pandas as pd

app = Flask(__name__)
# Update CORS configuration to allow Vercel frontend
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:3000",
            "https://image-to-excel-one.vercel.app"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Swagger configuration
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "PDF Text Extraction API"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/')
def home():
    """
    Welcome endpoint
    ---
    tags:
      - General
    responses:
      200:
        description: Welcome message
        schema:
          type: object
          properties:
            message:
              type: string
            status:
              type: string
    """
    return jsonify({
        "message": "Welcome to PDF Text Extraction API",
        "status": "success"
    })

@app.route('/api/health')
def health_check():
    """
    Health check endpoint
    ---
    tags:
      - General
    responses:
      200:
        description: Health status
        schema:
          type: object
          properties:
            status:
              type: string
            service:
              type: string
    """
    return jsonify({
        "status": "healthy",
        "service": "PDF Text Extraction API"
    })

@app.route('/extract-text', methods=['POST'])
def extract_text():
    """
    Extract text and tables from PDF file
    ---
    tags:
      - PDF Operations
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: PDF file to extract text and tables from
    responses:
      200:
        description: Successfully extracted text and tables
        schema:
          type: object
          properties:
            text:
              type: string
            tables:
              type: array
              items:
                type: array
      400:
        description: Bad request
        schema:
          type: object
          properties:
            error:
              type: string
      500:
        description: Server error
        schema:
          type: object
          properties:
            error:
              type: string
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not file.filename.endswith('.pdf'):
            return jsonify({"error": "File must be a PDF"}), 400

        # Save the file temporarily to process with tabula
        temp_path = "temp.pdf"
        file.save(temp_path)
        
        # Extract tables using tabula
        tables = tabula.read_pdf(temp_path, pages='all', multiple_tables=True)
        
        # Convert tables to JSON-serializable format with headers
        tables_json = []
        for table in tables:
            table_data = {
                "headers": table.columns.tolist(),
                "data": table.values.tolist()
            }
            tables_json.append(table_data)
            
        # Read the file again for text extraction
        with open(temp_path, 'rb') as pdf_file:
            # Create PDF reader object
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text from all pages
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        
        # Clean up temporary file
        import os
        os.remove(temp_path)
        
        return jsonify({
            "text": text,
            "tables": tables_json
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)