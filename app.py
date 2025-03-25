from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import PyPDF2
import io

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

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
    Extract text from PDF file
    ---
    tags:
      - PDF Operations
    parameters:
      - in: formData
        name: file
        type: file
        required: true
        description: PDF file to extract text from
    responses:
      200:
        description: Successfully extracted text
        schema:
          type: object
          properties:
            text:
              type: string
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

        # Read the uploaded file
        content = file.read()
        pdf_file = io.BytesIO(content)
        
        # Create PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)