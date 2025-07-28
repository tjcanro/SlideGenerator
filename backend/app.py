import sys
import os
import json
import tempfile
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add the parent directory to Python path to find the generator module
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))
sys.path.append(str(current_dir))

logger.info(f"Current directory: {current_dir}")
logger.info(f"Parent directory: {parent_dir}")
logger.info(f"Python path: {sys.path}")

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:*'])

try:
    from inference import run_inference
    logger.info("Successfully imported inference")
except ImportError as e:
    logger.error(f"Failed to import inference: {e}")
    raise

@app.route('/generate', methods=['POST', 'OPTIONS'])
def generate():
    if request.method == 'OPTIONS':
        # Handle preflight request
        return '', 200
        
    logger.info("Received generate request")
    logger.info(f"Request headers: {dict(request.headers)}")
    logger.info(f"Content-Type: {request.content_type}")
    
    try:
        # Get the prompt as plain text from request body
        prompt = request.get_data(as_text=True)
        
        # If no data in body, check if it's JSON (for backward compatibility)
        if not prompt and request.is_json:
            data = request.get_json()
            prompt = data.get('prompt', '')
        
        logger.info(f"Received prompt: {prompt[:100]}..." if len(prompt) > 100 else f"Received prompt: {prompt}")
        
        if not prompt or len(prompt.strip()) < 10:
            return jsonify({'error': 'Prompt must be at least 10 characters long'}), 400
        
        # Generate the presentation using run_inference
        logger.info("Running inference to generate presentation...")
        pptx_path = run_inference(prompt.strip())
        logger.info(f"Generated presentation at: {pptx_path}")
        
        # Check if the file exists
        if not os.path.exists(pptx_path):
            raise FileNotFoundError(f"Generated file not found: {pptx_path}")
        
        return send_file(
            pptx_path, 
            as_attachment=True, 
            download_name='GeneratedDeck.pptx', 
            mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
    except Exception as e:
        logger.error(f"Error in generate endpoint: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    logger.info("Health check requested")
    inference_available = 'run_inference' in globals()
    presentation_gen_available = 'presentation_gen' in globals()
    
    return jsonify({
        'status': 'healthy', 
        'message': 'Slide Generator API is running',
        'modules': {
            'inference': inference_available,
            'presentation_gen': presentation_gen_available
        }
    })

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Slide Generator API',
        'endpoints': {
            '/health': 'GET - Health check',
            '/generate': 'POST - Generate presentation from prompt (plain text in body)'
        }
    })

if __name__ == '__main__':
    logger.info("Starting Flask app on port 5009")
    app.run(debug=True, port=5009, host='0.0.0.0')
