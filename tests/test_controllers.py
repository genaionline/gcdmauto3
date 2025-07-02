"""
Test cases for controllers
"""

import pytest
from flask import url_for

def test_home_redirect(client):
    """Test home page redirects to upload"""
    response = client.get('/')
    assert response.status_code == 302
    assert '/excel/upload' in response.location

def test_excel_upload_get(client):
    """Test Excel upload page GET request"""
    response = client.get('/excel/upload')
    assert response.status_code == 200
    assert b'GCDM Excel File Upload' in response.data
    assert b'Select Market' in response.data
    assert b'Data Month' in response.data

def test_config_view_get(client):
    """Test config view page GET request"""
    response = client.get('/config/view')
    assert response.status_code == 200
    assert b'Configuration View' in response.data

def test_admin_datamonth_get(client):
    """Test admin data month page GET request"""
    response = client.get('/admin/datamonth')
    assert response.status_code == 200
    assert b'Data Month Management' in response.data
    assert b'Add New Data Month' in response.data

def test_view_all_market_results_get(client):
    """Test view all market results page GET request"""
    response = client.get('/excel/viewallmarketresults')
    assert response.status_code == 200
    assert b'All Market Results' in response.data
    assert b'Filter Data' in response.data

def test_excel_upload_post_missing_data(client):
    """Test Excel upload POST with missing data"""
    response = client.post('/excel/upload', data={})
    assert response.status_code == 302  # Redirect back to upload page

def test_admin_datamonth_post_missing_data(client):
    """Test admin data month POST with missing data"""
    response = client.post('/admin/datamonth', data={})
    assert response.status_code == 302  # Redirect back to admin page

def test_config_view_with_market(client):
    """Test config view with specific market parameter"""
    response = client.get('/config/view?market=SG')
    assert response.status_code == 200
    assert b'Configuration View' in response.data
