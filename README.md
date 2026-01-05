# call-status

A project designed to run on a Raspberry Pi Zero to show a status on if I'm on a call or not.

This application consists of two parts:

1. **Server (API)**: A Flask-based API that stores and serves call status information
2. **Client (Service)**: A service that polls the API every minute and displays the current status

## Features

### API Server
- **GET /status**: Retrieve the current call status
- **POST /status**: Update the call status
- **GET /health**: Health check endpoint
- Stores status in a JSON file
- Designed to run as a systemd service

### Client Service
- Polls the API every minute (configurable)
- Displays status updates with timestamps
- Designed to run as a systemd service
- Automatically restarts on failure

## Testing

This project includes automated tests with coverage reporting. The test suite enforces a minimum of 60% code coverage.

### Running Tests

To run the test suite locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests with coverage
pytest

# Run tests with verbose output
pytest -v

# Generate HTML coverage report
pytest --cov-report=html
open htmlcov/index.html
```

### Test Coverage

Current coverage: **84.81%** (exceeds 60% requirement)

- **Server tests**: 97.73% coverage
- **Client tests**: 68.57% coverage

### Continuous Integration

Tests run automatically on every pull request via GitHub Actions. The workflow:
- Installs dependencies
- Runs the test suite
- Validates minimum 60% coverage
- Generates coverage reports

## Installation

### Server Installation

1. Navigate to the server directory:
```bash
cd server
```

2. Run the deployment script as root:
```bash
sudo ./deploy.sh
```

This will:
- Install Python 3 and dependencies
- Create a virtual environment
- Install Flask and required packages
- Set up the systemd service
- Start the API server on port 5000

### Client Installation

1. Navigate to the client directory:
```bash
cd client
```

2. Run the deployment script as root:
```bash
sudo ./deploy.sh
```

You will be prompted to enter the API URL. If the server is running on the same Raspberry Pi, use `http://localhost:5000/status`.

This will:
- Install Python 3 and dependencies
- Create a virtual environment
- Install requests and required packages
- Set up the systemd service
- Start the client service

## Usage

### Updating Status

To update the call status, send a POST request to the API:

```bash
# Set status to "on call"
curl -X POST http://localhost:5000/status \
  -H "Content-Type: application/json" \
  -d '{"status": "busy", "message": "On a call"}'

# Set status to "available"
curl -X POST http://localhost:5000/status \
  -H "Content-Type: application/json" \
  -d '{"status": "available", "message": "Not on a call"}'
```

### Checking Status

To check the current status:

```bash
curl http://localhost:5000/status
```

Example response:
```json
{
  "status": "busy",
  "message": "On a call",
  "updated_at": "2026-01-05T00:00:00.000000"
}
```

### Managing Services

#### Server Service
```bash
# Check status
sudo systemctl status call-status-server

# View logs
sudo journalctl -u call-status-server -f

# Restart service
sudo systemctl restart call-status-server

# Stop service
sudo systemctl stop call-status-server
```

#### Client Service
```bash
# Check status
sudo systemctl status call-status-client

# View logs
sudo journalctl -u call-status-client -f

# Restart service
sudo systemctl restart call-status-client

# Stop service
sudo systemctl stop call-status-client
```

## Configuration

### Server Configuration

The server can be configured using environment variables in the systemd service file (`/etc/systemd/system/call-status-server.service`):

- `STATUS_FILE`: Path to the JSON file storing status (default: `/var/lib/call-status/status.json`)
- `PORT`: Port number for the API (default: `5000`)

### Client Configuration

The client can be configured using environment variables in the systemd service file (`/etc/systemd/system/call-status-client.service`):

- `API_URL`: URL of the API server (default: `http://localhost:5000/status`)
- `POLL_INTERVAL`: Polling interval in seconds (default: `60`)

After changing configuration, reload and restart the service:
```bash
sudo systemctl daemon-reload
sudo systemctl restart call-status-server  # or call-status-client
```

## File Structure

```
call-status/
├── client/
│   ├── status_client.py           # Client application
│   ├── requirements.txt            # Python dependencies
│   ├── call-status-client.service  # Systemd service file
│   └── deploy.sh                   # Deployment script
├── server/
│   ├── api_server.py               # API server application
│   ├── requirements.txt            # Python dependencies
│   ├── call-status-server.service  # Systemd service file
│   └── deploy.sh                   # Deployment script
└── README.md
```

## Requirements

- Raspberry Pi Zero (or any Linux system with systemd)
- Python 3.7 or higher
- Internet connection for initial setup

## License

See LICENSE file for details.
