#!/usr/bin/env python3
"""
Call Status API Server
A simple Flask API that stores and retrieves call status information
"""

from flask import Flask, jsonify, request
import json
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
STATUS_FILE = os.environ.get('STATUS_FILE', '/var/lib/call-status/status.json')
DEFAULT_STATUS = {
    'status': 'available',
    'message': 'Not on a call',
    'updated_at': datetime.now().isoformat()
}


def ensure_status_file():
    """Ensure the status file exists and is readable"""
    status_dir = os.path.dirname(STATUS_FILE)
    
    # Create directory if it doesn't exist
    if not os.path.exists(status_dir):
        os.makedirs(status_dir, exist_ok=True)
    
    # Create file with default status if it doesn't exist
    if not os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'w') as f:
            json.dump(DEFAULT_STATUS, f, indent=2)


def read_status():
    """Read the current status from the JSON file"""
    ensure_status_file()
    try:
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return DEFAULT_STATUS


def write_status(status_data):
    """Write status to the JSON file"""
    ensure_status_file()
    status_data['updated_at'] = datetime.now().isoformat()
    with open(STATUS_FILE, 'w') as f:
        json.dump(status_data, f, indent=2)


@app.route('/status', methods=['GET'])
def get_status():
    """GET endpoint to retrieve current status"""
    status = read_status()
    return jsonify(status), 200


@app.route('/status', methods=['POST'])
def update_status():
    """POST endpoint to update status"""
    if not request.json:
        return jsonify({'error': 'Request must be JSON'}), 400
    
    # Get current status
    current_status = read_status()
    
    # Update with new values
    if 'status' in request.json:
        current_status['status'] = request.json['status']
    if 'message' in request.json:
        current_status['message'] = request.json['message']
    
    # Write updated status
    write_status(current_status)
    
    return jsonify(current_status), 200


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    # Run on all interfaces on port 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
