"""
DataPeriod model - equivalent to Java DataPeriod entity
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from . import db

class DataPeriod(db.Model):
    __tablename__ = 'data_period'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    market_name = Column(String(255), nullable=False)
    data_month = Column(String(255), nullable=False)  # Format: 2025-Apr
    active_idc = Column(String(1), nullable=False)  # 'Y' or 'N'
    update_by = Column(String(255), nullable=False)
    update_time = Column(DateTime, nullable=False)
    
    def __init__(self, market_name, data_month, active_idc='Y', update_by='admin'):
        self.market_name = market_name
        self.data_month = data_month
        self.active_idc = active_idc
        self.update_by = update_by
        self.update_time = datetime.now()
    
    @property
    def is_active(self):
        """Check if this data period is active"""
        return self.active_idc == 'Y'
    
    def activate(self, updated_by='admin'):
        """Activate this data period"""
        self.active_idc = 'Y'
        self.update_by = updated_by
        self.update_time = datetime.now()
    
    def deactivate(self, updated_by='admin'):
        """Deactivate this data period"""
        self.active_idc = 'N'
        self.update_by = updated_by
        self.update_time = datetime.now()
    
    def __repr__(self):
        return f'<DataPeriod {self.market_name}-{self.data_month} ({self.active_idc})>'
