"""
Test cases for services
"""

import pytest
import tempfile
import os
import pandas as pd
from app.services.market_config_loader import MarketConfigLoader, MarketConfig
from app.services.user_service import UserService
from app.services.security_audit_service import SecurityAuditService
from app.services.excel_service import ExcelService

def test_market_config_loader():
    """Test MarketConfigLoader functionality"""
    # Create a temporary config directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test config file
        config_content = """
requireBuPrefix: false
requireXlsxSuffix: true
fileEncoding: UTF-8
worksheet:
  name: Sheet1
  dataRowRange:
    startRow: 2
    endRow: 100
  units:
    columnNum: 1
  metrics:
    columnNum: 3
"""
        config_file = os.path.join(temp_dir, "TEST.config.yml")
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        # Test loading config
        loader = MarketConfigLoader(temp_dir)
        loader.available_markets = ["TEST"]
        config = loader._load_config("TEST")
        
        assert config is not None
        assert config.get_worksheet_name() == "Sheet1"
        assert config.require_bu_prefix == False
        assert config.require_xlsx_suffix == True

def test_market_config():
    """Test MarketConfig functionality"""
    config_data = {
        'requireBuPrefix': True,
        'requireXlsxSuffix': False,
        'fileEncoding': 'UTF-8',
        'worksheet': {
            'name': 'TestSheet',
            'dataRowRange': {'startRow': 1, 'endRow': 50},
            'units': {'columnNum': 2},
            'metrics': {'columnNum': 4}
        }
    }
    
    config = MarketConfig(config_data)
    
    assert config.require_bu_prefix == True
    assert config.require_xlsx_suffix == False
    assert config.get_worksheet_name() == "TestSheet"
    assert config.get_data_row_range()['startRow'] == 1
    assert config.get_units_config()['columnNum'] == 2

def test_user_service():
    """Test UserService functionality"""
    user_service = UserService()
    
    # Test getting user ID
    user_id = user_service.get_user_id()
    assert user_id == "TestUserOne"
    
    # Test getting display name
    display_name = user_service.get_user_display_name()
    assert display_name == "Test User One"
    
    # Test getting admin user ID
    admin_id = user_service.get_admin_user_id()
    assert admin_id == "admin1"

def test_security_audit_service():
    """Test SecurityAuditService functionality"""
    audit_service = SecurityAuditService()
    
    # Test IP address extraction (without actual request)
    ip = audit_service._get_client_ip_address(None)
    assert ip == 'unknown'
    
    # Test logging methods (they should not raise exceptions)
    try:
        audit_service.log_security_event("TEST_EVENT", "test_user", "Test details")
        audit_service.log_file_upload("test_user", "test.xlsx", 1024, "SG")
        audit_service.log_data_access("test_user", "VIEW", "market=SG")
        audit_service.log_admin_operation("admin", "CREATE", "data_period")
        audit_service.log_suspicious_activity("SUSPICIOUS", "Test suspicious activity")
    except Exception as e:
        pytest.fail(f"Security audit logging failed: {e}")

def test_excel_service_pandas_methods():
    """Test ExcelService pandas-based methods"""
    # Create a test DataFrame
    test_data = {
        0: ['', 'Unit1', 'Unit2', 'Unit3'],  # Units column
        1: ['', '', '', ''],
        2: ['', 'Metric1', 'Metric2', 'Metric3'],  # Metrics column
        3: ['Jan_LYA', '100', '200', '300'],  # January LYA
        4: ['Feb_LYA', '110', '210', '310'],  # February LYA
    }
    df = pd.DataFrame(test_data)

    # Create test config
    config_data = {
        'worksheet': {
            'name': 'TestSheet',
            'dataRowRange': {'startRow': 2, 'endRow': 4},
            'units': {'columnNum': 1},
            'metrics': {'columnNum': 3},
            'lastYearActual': {
                'startColumn': 4,
                'endColumn': 5,
                'columns': [
                    {'name': 'Jan_LYA'},
                    {'name': 'Feb_LYA'}
                ]
            }
        }
    }
    config = MarketConfig(config_data)

    # Create ExcelService instance
    excel_service = ExcelService(None)

    # Test units extraction
    units = excel_service._extract_units_data_pandas(df, config, 1, 4)
    assert 'Unit1' in units
    assert 'Unit2' in units
    assert 'Unit3' in units

    # Test metrics extraction
    metrics = excel_service._extract_metrics_data_pandas(df, config, 1, 4)
    assert 'Metric1' in metrics
    assert 'Metric2' in metrics
    assert 'Metric3' in metrics

    # Test column data extraction
    column_data = excel_service._extract_column_data_pandas(df, config.get_last_year_actual_config(), 1, 4)
    assert 'Jan_LYA' in column_data
    assert 'Feb_LYA' in column_data
    assert '100' in column_data['Jan_LYA']
    assert '110' in column_data['Feb_LYA']
