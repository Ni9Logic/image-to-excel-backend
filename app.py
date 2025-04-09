from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import PyPDF2
import tabula
import logging
import io

app = Flask(__name__)
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

        # Read file into memory
        file_content = file.read()
        
        # Extract tables using tabula with in-memory file
        tables = tabula.read_pdf(io.BytesIO(file_content), pages='all', multiple_tables=True)
        
        # Convert tables to JSON-serializable format with headers
        tables_json = []
        for table in tables:
            table_data = {
                "headers": table.columns.tolist(),
                "data": table.values.tolist()
            }
            tables_json.append(table_data)
            
        # Extract text using PyPDF2 with in-memory file
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return jsonify({
            "text": text,
            "tables": tables_json
        })

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            "error": "Failed to process PDF file",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)