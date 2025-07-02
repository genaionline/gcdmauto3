"""
Database models for GCDM Auto application
"""

from flask_sqlalchemy import SQLAlchemy

# This will be initialized in app.py
db = SQLAlchemy()

from .excel_data import ExcelData
from .data_period import DataPeriod

__all__ = ['db', 'ExcelData', 'DataPeriod']
