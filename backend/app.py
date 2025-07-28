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

# Try to import the presentation generator
try:
    from generator.presentation_gen import presentation_gen
    logger.info("Successfully imported presentation_gen")
except ImportError as e:
    logger.error(f"Failed to import presentation_gen: {e}")
    # Try alternative import paths
    try:
        from presentation_gen import presentation_gen
        logger.info("Successfully imported presentation_gen from root")
    except ImportError as e2:
        logger.error(f"Failed to import presentation_gen from root: {e2}")
        # Create a dummy function for testing
        def presentation_gen(xml_path):
            logger.warning("Using dummy presentation_gen function")
            # Return a dummy file path for testing
            return xml_path

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:*'])

def generate_xml_from_prompt(prompt):
    """
    Generate XML structure from a prompt.
    """
    logger.info(f"Generating XML from prompt: {prompt[:100]}...")
    
    # Simple parsing logic
    lines = prompt.split('\n')
    slides = []
    current_slide = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Look for slide indicators
        if line.startswith(('Slide:', 'Slide ', '1.', '2.', '3.', '4.', '5.')) or \
           (line.startswith(('Topic:', 'Title:')) and current_slide is None):
            if current_slide:
                slides.append(current_slide)
            
            # Extract title
            title = line.split(':', 1)[-1].strip() if ':' in line else line
            title = title.lstrip('1234567890. ').strip()
            current_slide = {
                'title': title,
                'content': []
            }
        elif current_slide and line:
            # Add content points
            if line.startswith(('-', '•', '*', '1.', '2.', '3.')):
                content = line.lstrip('-•*1234567890. ').strip()
                if content:
                    current_slide['content'].append(content)
            else:
                # Treat as content if it's not a slide indicator
                current_slide['content'].append(line)
    
    # Add the last slide
    if current_slide:
        slides.append(current_slide)
    
    # If no structured slides found, create a simple presentation
    if not slides:
        slides = [{
            'title': 'Presentation',
            'content': [prompt]
        }]
    
    logger.info(f"Generated {len(slides)} slides")
    
    # Generate XML
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n<presentation>\n'
    
    for slide in slides:
        xml_content += '    <slide>\n'
        xml_content += f'        <title>{slide["title"]}</title>\n'
        xml_content += '        <content>\n'
        for point in slide['content']:
            xml_content += f'            <point>{point}</point>\n'
        xml_content += '        </content>\n'
        xml_content += '    </slide>\n'
    
    xml_content += '</presentation>'
    
    return xml_content

@app.route('/generate', methods=['POST', 'OPTIONS'])
def generate():
    if request.method == 'OPTIONS':
        # Handle preflight request
        return '', 200
        
    logger.info("Received generate request")
    logger.info(f"Request headers: {dict(request.headers)}")
    logger.info(f"Request is JSON: {request.is_json}")
    
    try:
        # Check if it's a JSON request
        if request.is_json:
            data = request.get_json()
            logger.info(f"Request data: {data}")
            
            if 'prompt' not in data:
                return jsonify({'error': 'No prompt provided'}), 400
            
            prompt = data['prompt']
            if not prompt or len(prompt.strip()) < 10:
                return jsonify({'error': 'Prompt must be at least 10 characters long'}), 400
            
            # Generate XML from prompt
            xml_content = generate_xml_from_prompt(prompt)
            
            # Create temp directory if it doesn't exist
            temp_dir = Path(tempfile.gettempdir()) / 'slide_generator'
            temp_dir.mkdir(exist_ok=True)
            
            # Save the generated XML temporarily
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, dir=temp_dir)
            temp_file.write(xml_content)
            temp_file.close()
            temp_path = temp_file.name
            
            logger.info(f"Saved XML to: {temp_path}")
            
            # Check if the presentation_gen function exists and works
            try:
                # Generate the presentation
                pptx_path = presentation_gen(temp_path)
                logger.info(f"Generated presentation at: {pptx_path}")
                
                # Check if the file exists
                if not os.path.exists(pptx_path):
                    raise FileNotFoundError(f"Generated file not found: {pptx_path}")
                
                return send_file(pptx_path, as_attachment=True, download_name='GeneratedDeck.pptx', mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation')
            except Exception as gen_error:
                logger.error(f"Error generating presentation: {gen_error}")
                # For testing, return the XML file instead
                logger.warning("Returning XML file for testing purposes")
                return send_file(temp_path, as_attachment=True, download_name='GeneratedDeck.xml', mimetype='text/xml')
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except:
                        pass
                
    except Exception as e:
        logger.error(f"Error in generate endpoint: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    logger.info("Health check requested")
    return jsonify({'status': 'healthy', 'message': 'Slide Generator API is running'})

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Slide Generator API',
        'endpoints': {
            '/health': 'GET - Health check',
            '/generate': 'POST - Generate presentation from prompt'
        }
    })

if __name__ == '__main__':
    logger.info("Starting Flask app on port 5009")
    app.run(debug=True, port=5009, host='0.0.0.0')
