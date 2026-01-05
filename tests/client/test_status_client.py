"""Tests for the Call Status Client"""

import pytest
import json
from unittest.mock import patch, MagicMock, call
from datetime import datetime
import sys
import os
import requests

# Add client directory to path to allow importing without package installation
# This allows tests to run directly without requiring 'pip install -e .'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../client'))

from status_client import fetch_status, display_status, API_URL, POLL_INTERVAL


class TestFetchStatus:
    """Test the fetch_status function"""
    
    @patch('status_client.requests.get')
    def test_fetch_status_returns_data_on_success(self, mock_get):
        """Test that fetch_status returns data on successful request"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'status': 'busy',
            'message': 'On a call',
            'updated_at': '2026-01-05T00:00:00.000000'
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = fetch_status()
        assert result is not None
        assert result['status'] == 'busy'
        assert result['message'] == 'On a call'
    
    @patch('status_client.requests.get')
    def test_fetch_status_calls_api_url(self, mock_get):
        """Test that fetch_status calls the correct API URL"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'status': 'available'}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        fetch_status()
        mock_get.assert_called_once_with(API_URL, timeout=10)
    
    @patch('status_client.requests.get')
    def test_fetch_status_returns_none_on_request_exception(self, mock_get):
        """Test that fetch_status returns None on request exception"""
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        result = fetch_status()
        assert result is None
    
    @patch('status_client.requests.get')
    def test_fetch_status_returns_none_on_timeout(self, mock_get):
        """Test that fetch_status returns None on timeout"""
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        
        result = fetch_status()
        assert result is None
    
    @patch('status_client.requests.get')
    def test_fetch_status_returns_none_on_http_error(self, mock_get):
        """Test that fetch_status returns None on HTTP error"""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        result = fetch_status()
        assert result is None


class TestDisplayStatus:
    """Test the display_status function"""
    
    @patch('builtins.print')
    def test_display_status_prints_status(self, mock_print):
        """Test that display_status prints the status"""
        status_data = {
            'status': 'busy',
            'message': 'On a call',
            'updated_at': '2026-01-05T00:00:00.000000'
        }
        
        display_status(status_data)
        
        # Check that print was called multiple times
        assert mock_print.call_count >= 4
        
        # Verify the content contains key information
        printed_text = ' '.join(str(call_args[0][0]) for call_args in mock_print.call_args_list)
        assert 'busy' in printed_text
        assert 'On a call' in printed_text
    
    @patch('builtins.print')
    def test_display_status_handles_missing_fields(self, mock_print):
        """Test that display_status handles missing fields gracefully"""
        status_data = {}
        
        display_status(status_data)
        
        # Check that print was called without errors
        assert mock_print.call_count >= 4
        
        # Verify it uses default values
        printed_text = ' '.join(str(call_args[0][0]) for call_args in mock_print.call_args_list)
        assert 'unknown' in printed_text or 'No message' in printed_text
    
    @patch('builtins.print')
    def test_display_status_shows_available_status(self, mock_print):
        """Test that display_status correctly shows available status"""
        status_data = {
            'status': 'available',
            'message': 'Not on a call',
            'updated_at': '2026-01-05T01:00:00.000000'
        }
        
        display_status(status_data)
        
        printed_text = ' '.join(str(call_args[0][0]) for call_args in mock_print.call_args_list)
        assert 'available' in printed_text
        assert 'Not on a call' in printed_text
    
    @patch('builtins.print')
    def test_display_status_includes_timestamp(self, mock_print):
        """Test that display_status includes a timestamp"""
        status_data = {
            'status': 'busy',
            'message': 'On a call',
            'updated_at': '2026-01-05T00:00:00.000000'
        }
        
        display_status(status_data)
        
        # Check that at least one print call contains a timestamp-like pattern
        printed_calls = [str(call_args[0][0]) for call_args in mock_print.call_args_list]
        has_timestamp = any('[' in text and ']' in text for text in printed_calls)
        assert has_timestamp


class TestConfiguration:
    """Test configuration settings"""
    
    def test_api_url_default_value(self):
        """Test that API_URL has a default value"""
        assert API_URL is not None
        assert 'http' in API_URL.lower()
        assert 'status' in API_URL.lower()
    
    def test_poll_interval_default_value(self):
        """Test that POLL_INTERVAL has a default value"""
        assert POLL_INTERVAL > 0
        assert isinstance(POLL_INTERVAL, int)
    
    @patch.dict(os.environ, {'API_URL': 'http://test.example.com/status'})
    def test_api_url_from_environment(self):
        """Test that API_URL can be set from environment variable"""
        # Need to reimport to pick up the environment variable
        import importlib
        import status_client
        importlib.reload(status_client)
        
        assert status_client.API_URL == 'http://test.example.com/status'
    
    @patch.dict(os.environ, {'POLL_INTERVAL': '120'})
    def test_poll_interval_from_environment(self):
        """Test that POLL_INTERVAL can be set from environment variable"""
        # Need to reimport to pick up the environment variable
        import importlib
        import status_client
        importlib.reload(status_client)
        
        assert status_client.POLL_INTERVAL == 120
