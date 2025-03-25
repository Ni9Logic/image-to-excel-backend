# PDF Text Extraction API

A Flask API for extracting text from PDF files.

## Setup Instructions

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

## API Endpoints

- `GET /`: Welcome message
  ```json
  {
    "message": "Welcome to PDF Text Extraction API",
    "status": "success"
  }
  ```

- `GET /api/health`: Health check endpoint
  ```json
  {
    "status": "healthy",
    "service": "PDF Text Extraction API"
  }
  ```

- `POST /extract-text`: Extract text from a PDF file
  - Content-Type: multipart/form-data
  - Body: file (PDF file)
  - Response:
    ```json
    {
      "text": "Extracted text from PDF..."
    }
    ```
  - Error Response:
    ```json
    {
      "error": "Error message"
    }
    ```

## Development

The application runs in debug mode by default. Any changes to the code will automatically reload the server.

## CORS

The API is configured to accept requests from `http://localhost:3000` for frontend development. 