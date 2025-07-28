# Slide Generator

A web application that generates PowerPoint presentations from XML files.

## Project Structure

- `backend/` - Flask API server
- `frontend/` - Web interface
- `generator/` - PowerPoint generation logic

## Setup Instructions

### Backend Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Flask server:**
   ```bash
   cd backend
   python app.py
   ```
   The backend will run on `http://localhost:5009`

### Frontend Setup

1. **Install Node.js dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Build CSS (if needed):**
   ```bash
   npm run build:css
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```
   The frontend will run on `http://localhost:3000`

## Usage

1. Open your browser and go to `http://localhost:3000`
2. Upload an XML file with slide data
3. Click "Generate Presentation" to create a PowerPoint file
4. The generated file will be automatically downloaded

## XML Format

The application expects XML files in this format:

```xml
<slides>
  <slide>
    <title>Slide Title</title>
    <content>
      <point>First bullet point</point>
      <point>Second bullet point</point>
    </content>
  </slide>
</slides>
```

## Development

- Backend: Flask with CORS enabled
- Frontend: Vanilla JavaScript with Tailwind CSS
- PowerPoint generation: python-pptx library 