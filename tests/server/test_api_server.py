"""Tests for the Call Status API Server"""

import pytest
import json
import os
import tempfile
from unittest.mock import patch, mock_open
from datetime import datetime
import sys

# Add server directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../server'))

from api_server import app, ensure_status_file, read_status, write_status, DEFAULT_STATUS


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def temp_status_file():
    """Create a temporary status file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_file = f.name
    yield temp_file
    # Cleanup
    if os.path.exists(temp_file):
        os.remove(temp_file)


class TestHealthEndpoint:
    """Test the /health endpoint"""
    
    def test_health_check_returns_200(self, client):
        """Test that health check returns 200 status"""
        response = client.get('/health')
        assert response.status_code == 200
    
    def test_health_check_returns_healthy_status(self, client):
        """Test that health check returns healthy status in JSON"""
        response = client.get('/health')
        data = json.loads(response.data)
        assert data['status'] == 'healthy'


class TestGetStatusEndpoint:
    """Test the GET /status endpoint"""
    
    @patch('api_server.read_status')
    def test_get_status_returns_200(self, mock_read, client):
        """Test that GET /status returns 200 status"""
        mock_read.return_value = DEFAULT_STATUS
        response = client.get('/status')
        assert response.status_code == 200
    
    @patch('api_server.read_status')
    def test_get_status_returns_status_data(self, mock_read, client):
        """Test that GET /status returns status data"""
        test_status = {
            'status': 'busy',
            'message': 'On a call',
            'updated_at': '2026-01-05T00:00:00.000000'
        }
        mock_read.return_value = test_status
        response = client.get('/status')
        data = json.loads(response.data)
        assert data['status'] == 'busy'
        assert data['message'] == 'On a call'
        assert 'updated_at' in data


class TestPostStatusEndpoint:
    """Test the POST /status endpoint"""
    
    @patch('api_server.read_status')
    @patch('api_server.write_status')
    def test_post_status_returns_200(self, mock_write, mock_read, client):
        """Test that POST /status returns 200 status"""
        mock_read.return_value = DEFAULT_STATUS.copy()
        response = client.post('/status',
                              data=json.dumps({'status': 'busy'}),
                              content_type='application/json')
        assert response.status_code == 200
    
    @patch('api_server.read_status')
    @patch('api_server.write_status')
    def test_post_status_updates_status_field(self, mock_write, mock_read, client):
        """Test that POST /status updates the status field"""
        mock_read.return_value = DEFAULT_STATUS.copy()
        response = client.post('/status',
                              data=json.dumps({'status': 'busy'}),
                              content_type='application/json')
        data = json.loads(response.data)
        assert data['status'] == 'busy'
        mock_write.assert_called_once()
    
    @patch('api_server.read_status')
    @patch('api_server.write_status')
    def test_post_status_updates_message_field(self, mock_write, mock_read, client):
        """Test that POST /status updates the message field"""
        mock_read.return_value = DEFAULT_STATUS.copy()
        response = client.post('/status',
                              data=json.dumps({'message': 'In a meeting'}),
                              content_type='application/json')
        data = json.loads(response.data)
        assert data['message'] == 'In a meeting'
        mock_write.assert_called_once()
    
    @patch('api_server.read_status')
    @patch('api_server.write_status')
    def test_post_status_updates_both_fields(self, mock_write, mock_read, client):
        """Test that POST /status can update both status and message"""
        mock_read.return_value = DEFAULT_STATUS.copy()
        response = client.post('/status',
                              data=json.dumps({
                                  'status': 'busy',
                                  'message': 'On a call'
                              }),
                              content_type='application/json')
        data = json.loads(response.data)
        assert data['status'] == 'busy'
        assert data['message'] == 'On a call'
        mock_write.assert_called_once()
    
    def test_post_status_rejects_non_json(self, client):
        """Test that POST /status rejects non-JSON requests"""
        response = client.post('/status',
                              data='not json',
                              content_type='text/plain')
        # Flask returns 415 Unsupported Media Type for non-JSON content-type
        # or 400 Bad Request if request.json is None
        assert response.status_code in [400, 415]


class TestFileOperations:
    """Test file operation functions"""
    
    def test_ensure_status_file_creates_directory(self, temp_status_file):
        """Test that ensure_status_file creates the directory if it doesn't exist"""
        # Create a path with a new directory
        test_dir = tempfile.mkdtemp()
        test_file = os.path.join(test_dir, 'subdir', 'status.json')
        
        with patch('api_server.STATUS_FILE', test_file):
            ensure_status_file()
            assert os.path.exists(os.path.dirname(test_file))
        
        # Cleanup
        import shutil
        shutil.rmtree(test_dir)
    
    def test_ensure_status_file_creates_file_with_default_status(self, temp_status_file):
        """Test that ensure_status_file creates file with default status"""
        with patch('api_server.STATUS_FILE', temp_status_file):
            # Remove the file first
            if os.path.exists(temp_status_file):
                os.remove(temp_status_file)
            
            ensure_status_file()
            assert os.path.exists(temp_status_file)
            
            with open(temp_status_file, 'r') as f:
                data = json.load(f)
                assert data['status'] == 'available'
                assert data['message'] == 'Not on a call'
    
    def test_read_status_returns_data_from_file(self, temp_status_file):
        """Test that read_status returns data from the status file"""
        test_data = {
            'status': 'busy',
            'message': 'On a call',
            'updated_at': '2026-01-05T00:00:00.000000'
        }
        
        with open(temp_status_file, 'w') as f:
            json.dump(test_data, f)
        
        with patch('api_server.STATUS_FILE', temp_status_file):
            result = read_status()
            assert result['status'] == 'busy'
            assert result['message'] == 'On a call'
    
    def test_read_status_returns_default_on_json_error(self, temp_status_file):
        """Test that read_status returns default status on JSON decode error"""
        with open(temp_status_file, 'w') as f:
            f.write('invalid json{')
        
        with patch('api_server.STATUS_FILE', temp_status_file):
            result = read_status()
            assert result['status'] == DEFAULT_STATUS['status']
            assert result['message'] == DEFAULT_STATUS['message']
    
    def test_write_status_updates_file(self, temp_status_file):
        """Test that write_status updates the status file"""
        test_data = {
            'status': 'busy',
            'message': 'On a call'
        }
        
        with patch('api_server.STATUS_FILE', temp_status_file):
            write_status(test_data)
            
            with open(temp_status_file, 'r') as f:
                result = json.load(f)
                assert result['status'] == 'busy'
                assert result['message'] == 'On a call'
                assert 'updated_at' in result
    
    def test_write_status_adds_timestamp(self, temp_status_file):
        """Test that write_status adds an updated_at timestamp"""
        test_data = {
            'status': 'busy',
            'message': 'On a call'
        }
        
        with patch('api_server.STATUS_FILE', temp_status_file):
            write_status(test_data)
            
            with open(temp_status_file, 'r') as f:
                result = json.load(f)
                assert 'updated_at' in result
                # Verify it's a valid ISO format timestamp
                datetime.fromisoformat(result['updated_at'])
