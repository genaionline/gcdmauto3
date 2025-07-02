"""
Test configuration and fixtures
"""

import pytest
import tempfile
import os
from app import app
from app.models import db

@pytest.fixture
def client():
    """Create a test client"""
    # Create a temporary database
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
    
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

@pytest.fixture
def app_context():
    """Create an application context"""
    with app.app_context():
        yield app
