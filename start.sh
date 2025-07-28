#!/bin/bash

echo "Starting Slide Generator Application..."

# Start backend in background
echo "Starting Flask backend..."
cd backend
python app.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 2

# Start frontend
echo "Starting frontend server..."
cd frontend
npm install
npm run dev &
FRONTEND_PID=$!
cd ..

echo "Application is starting..."
echo "Backend: http://localhost:5009"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user to stop
wait 