#!/usr/bin/env python3
"""
Call Status Client
A service that polls the call status API and displays the status
"""

import requests
import json
import time
import os
import sys
from datetime import datetime


# Configuration
API_URL = os.environ.get('API_URL', 'http://localhost:5000/status')
POLL_INTERVAL = int(os.environ.get('POLL_INTERVAL', 60))  # Default: 60 seconds


def display_status(status_data):
    """Display the status information"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] Status Update:")
    print(f"  Status: {status_data.get('status', 'unknown')}")
    print(f"  Message: {status_data.get('message', 'No message')}")
    print(f"  Last Updated: {status_data.get('updated_at', 'unknown')}")
    print("-" * 50)


def fetch_status():
    """Fetch the current status from the API"""
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching status: {e}", file=sys.stderr)
        return None


def main():
    """Main loop that polls the API every minute"""
    print(f"Call Status Client started")
    print(f"Polling API at: {API_URL}")
    print(f"Poll interval: {POLL_INTERVAL} seconds")
    print("=" * 50)
    
    while True:
        status = fetch_status()
        if status:
            display_status(status)
        else:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] Failed to fetch status")
        
        # Wait for the next poll
        time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down client...")
        sys.exit(0)
