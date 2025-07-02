"""
ExcelData model - equivalent to Java ExcelData entity
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from . import db

class ExcelData(db.Model):
    __tablename__ = 'excel_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    market_name = Column(String(255), nullable=False)
    unit_name = Column(String(255), nullable=False)
    metric_name = Column(String(255), nullable=False)
    data_month = Column(String(255), nullable=False)  # Format: 2025-Apr
    
    # Last Year Actual (12 months)
    jan_lya = Column(String(255))
    feb_lya = Column(String(255))
    mar_lya = Column(String(255))
    apr_lya = Column(String(255))
    may_lya = Column(String(255))
    jun_lya = Column(String(255))
    jul_lya = Column(String(255))
    aug_lya = Column(String(255))
    sep_lya = Column(String(255))
    oct_lya = Column(String(255))
    nov_lya = Column(String(255))
    dec_lya = Column(String(255))
    
    # Current Year Actual (12 months)
    jan_cya = Column(String(255))
    feb_cya = Column(String(255))
    mar_cya = Column(String(255))
    apr_cya = Column(String(255))
    may_cya = Column(String(255))
    jun_cya = Column(String(255))
    jul_cya = Column(String(255))
    aug_cya = Column(String(255))
    sep_cya = Column(String(255))
    oct_cya = Column(String(255))
    nov_cya = Column(String(255))
    dec_cya = Column(String(255))
    
    # Current Year Target (12 months)
    jan_cyt = Column(String(255))
    feb_cyt = Column(String(255))
    mar_cyt = Column(String(255))
    apr_cyt = Column(String(255))
    may_cyt = Column(String(255))
    jun_cyt = Column(String(255))
    jul_cyt = Column(String(255))
    aug_cyt = Column(String(255))
    sep_cyt = Column(String(255))
    oct_cyt = Column(String(255))
    nov_cyt = Column(String(255))
    dec_cyt = Column(String(255))
    
    upload_timestamp = Column(DateTime, nullable=False)
    worksheet_name = Column(String(255))
    batch_id = Column(String(255), nullable=False)
    user_id = Column(String(255), nullable=False)
    created_time = Column(DateTime, nullable=False)
    updated_time = Column(DateTime, nullable=False)
    
    def __init__(self, market_name, unit_name, metric_name, data_month, 
                 batch_id, user_id, worksheet_name=None, upload_timestamp=None):
        self.market_name = market_name
        self.unit_name = unit_name
        self.metric_name = metric_name
        self.data_month = data_month
        self.batch_id = batch_id
        self.user_id = user_id
        self.worksheet_name = worksheet_name
        self.upload_timestamp = upload_timestamp or datetime.now()
        self.created_time = datetime.now()
        self.updated_time = datetime.now()
    
    def get_monthly_lya(self, month_name):
        """Get Last Year Actual value for a specific month"""
        month_attr = f"{month_name.lower()}_lya"
        return getattr(self, month_attr, None)
    
    def get_monthly_cya(self, month_name):
        """Get Current Year Actual value for a specific month"""
        month_attr = f"{month_name.lower()}_cya"
        return getattr(self, month_attr, None)
    
    def get_monthly_cyt(self, month_name):
        """Get Current Year Target value for a specific month"""
        month_attr = f"{month_name.lower()}_cyt"
        return getattr(self, month_attr, None)
    
    def set_monthly_lya(self, month_name, value):
        """Set Last Year Actual value for a specific month"""
        month_attr = f"{month_name.lower()}_lya"
        setattr(self, month_attr, value)
    
    def set_monthly_cya(self, month_name, value):
        """Set Current Year Actual value for a specific month"""
        month_attr = f"{month_name.lower()}_cya"
        setattr(self, month_attr, value)
    
    def set_monthly_cyt(self, month_name, value):
        """Set Current Year Target value for a specific month"""
        month_attr = f"{month_name.lower()}_cyt"
        setattr(self, month_attr, value)
    
    def __repr__(self):
        return f'<ExcelData {self.market_name}-{self.unit_name}-{self.metric_name}>'
