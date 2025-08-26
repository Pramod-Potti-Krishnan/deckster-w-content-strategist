#!/bin/bash
# Start script for Railway deployment - Diagram Microservice v2

# Railway provides PORT as an environment variable
# Default to 8001 if not set (for local development)
PORT=${PORT:-8001}

echo "Starting Diagram Microservice v2 on port $PORT..."
cd src/agents/diagram_microservice_v2
python main.py --host 0.0.0.0 --port $PORT