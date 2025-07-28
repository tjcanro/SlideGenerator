import sys
import os
import json
import tempfile
# Add the parent directory to Python path to find the generator module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, send_file, jsonify
from generator import presentation_gen
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'])

def generate_xml_from_prompt(prompt):
    """
    Generate XML structure from a prompt.
    This is a simple implementation that creates a basic presentation structure.
    In a real application, you might want to use AI/ML to parse the prompt more intelligently.
    """
    # Simple parsing logic - you can enhance this based on your needs
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

@app.route('/generate', methods=['POST'])
def generate():
    try:
        # Check if it's a JSON request (new prompt-based approach)
        if request.is_json:
            data = request.get_json()
            if 'prompt' not in data:
                return jsonify({'error': 'No prompt provided'}), 400
            
            prompt = data['prompt']
            if not prompt or len(prompt.strip()) < 10:
                return jsonify({'error': 'Prompt must be at least 10 characters long'}), 400
            
            # Generate XML from prompt
            xml_content = generate_xml_from_prompt(prompt)
            
            # Save the generated XML temporarily
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
                f.write(xml_content)
                temp_path = f.name
            
        else:
            # Fallback for file upload (legacy support)
            if 'xml_file' not in request.files:
                return jsonify({'error': 'No file uploaded'}), 400
            
            xml_file = request.files['xml_file']
            if xml_file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            # Save the uploaded file temporarily
            temp_path = os.path.join('generator', 'temp_upload.xml')
            xml_file.save(temp_path)
        
        try:
            # Generate the presentation
            pptx_path = presentation_gen(temp_path)
            return send_file(pptx_path, as_attachment=True, download_name='GeneratedDeck.pptx')
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'message': 'Slide Generator API is running'})

if __name__ == '__main__':
    app.run(debug=True, port=5009)
