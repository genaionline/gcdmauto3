"""
Test cases for database models
"""

import pytest
from datetime import datetime
from app.models import db, ExcelData, DataPeriod

def test_excel_data_creation(app_context):
    """Test ExcelData model creation"""
    excel_data = ExcelData(
        market_name="SG",
        unit_name="Test Unit",
        metric_name="Test Metric",
        data_month="2025-Apr",
        batch_id="test_batch_123",
        user_id="test_user",
        worksheet_name="Sheet1"
    )
    
    assert excel_data.market_name == "SG"
    assert excel_data.unit_name == "Test Unit"
    assert excel_data.metric_name == "Test Metric"
    assert excel_data.data_month == "2025-Apr"
    assert excel_data.batch_id == "test_batch_123"
    assert excel_data.user_id == "test_user"
    assert excel_data.worksheet_name == "Sheet1"

def test_excel_data_monthly_methods(app_context):
    """Test ExcelData monthly data methods"""
    excel_data = ExcelData(
        market_name="SG",
        unit_name="Test Unit",
        metric_name="Test Metric",
        data_month="2025-Apr",
        batch_id="test_batch_123",
        user_id="test_user"
    )
    
    # Test setting and getting monthly data
    excel_data.set_monthly_lya("Jan", "100")
    excel_data.set_monthly_cya("Jan", "110")
    excel_data.set_monthly_cyt("Jan", "120")
    
    assert excel_data.get_monthly_lya("Jan") == "100"
    assert excel_data.get_monthly_cya("Jan") == "110"
    assert excel_data.get_monthly_cyt("Jan") == "120"

def test_data_period_creation(app_context):
    """Test DataPeriod model creation"""
    data_period = DataPeriod(
        market_name="SG",
        data_month="2025-Apr",
        active_idc="Y",
        update_by="admin"
    )
    
    assert data_period.market_name == "SG"
    assert data_period.data_month == "2025-Apr"
    assert data_period.active_idc == "Y"
    assert data_period.update_by == "admin"
    assert data_period.is_active == True

def test_data_period_activation(app_context):
    """Test DataPeriod activation/deactivation"""
    data_period = DataPeriod(
        market_name="SG",
        data_month="2025-Apr",
        active_idc="N",
        update_by="admin"
    )
    
    assert data_period.is_active == False
    
    data_period.activate("test_user")
    assert data_period.is_active == True
    assert data_period.update_by == "test_user"
    
    data_period.deactivate("admin")
    assert data_period.is_active == False
    assert data_period.update_by == "admin"
