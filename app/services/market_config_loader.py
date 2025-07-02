"""
Market Configuration Loader - Python equivalent of Java MarketConfigLoader
"""

import yaml
import os
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class MarketConfig:
    """Market configuration data structure"""
    
    def __init__(self, config_data: Dict[str, Any]):
        self.data = config_data
        self.require_bu_prefix = config_data.get('requireBuPrefix', False)
        self.require_xlsx_suffix = config_data.get('requireXlsxSuffix', True)
        self.file_encoding = config_data.get('fileEncoding', 'UTF-8')
        self.worksheet = config_data.get('worksheet', {})
        self.validation_rules = config_data.get('validationRules', {})
        self.data_transform_rules = config_data.get('dataTransformRules', {})
    
    def get_worksheet(self) -> Dict[str, Any]:
        """Get worksheet configuration"""
        return self.worksheet
    
    def get_worksheet_name(self) -> str:
        """Get worksheet name"""
        return self.worksheet.get('name', 'Sheet1')
    
    def get_data_row_range(self) -> Dict[str, int]:
        """Get data row range configuration"""
        return self.worksheet.get('dataRowRange', {})
    
    def get_data_column_range(self) -> Dict[str, int]:
        """Get data column range configuration"""
        return self.worksheet.get('dataColumnRange', {})
    
    def get_units_config(self) -> Dict[str, Any]:
        """Get units configuration"""
        return self.worksheet.get('units', {})
    
    def get_metrics_config(self) -> Dict[str, Any]:
        """Get metrics configuration"""
        return self.worksheet.get('metrics', {})
    
    def get_last_year_actual_config(self) -> Dict[str, Any]:
        """Get last year actual configuration"""
        return self.worksheet.get('lastYearActual', {})
    
    def get_current_year_actual_config(self) -> Dict[str, Any]:
        """Get current year actual configuration"""
        return self.worksheet.get('currentYearActual', {})
    
    def get_current_year_target_config(self) -> Dict[str, Any]:
        """Get current year target configuration"""
        return self.worksheet.get('currentYearTarget', {})


class MarketConfigLoader:
    """Market configuration loader service"""
    
    def __init__(self, config_path: str = 'config/market'):
        self.config_path = config_path
        self.market_configs: Dict[str, MarketConfig] = {}
        self.available_markets: List[str] = []
        self._load_available_markets()
        self._load_market_configs()
    
    def _load_available_markets(self):
        """Load available markets from all.markets.config.yml"""
        try:
            markets_file = os.path.join('config', 'all.markets.config.yml')
            if os.path.exists(markets_file):
                with open(markets_file, 'r', encoding='utf-8') as f:
                    markets_data = yaml.safe_load(f)
                    markets_list = markets_data.get('markets', [])
                    self.available_markets = [market.get('code') for market in markets_list if market.get('code')]
                    logger.info(f"Loaded {len(self.available_markets)} markets: {self.available_markets}")
            else:
                logger.error(f"Markets configuration file not found: {markets_file}")
        except Exception as e:
            logger.error(f"Failed to load available markets: {e}")
    
    def _load_market_configs(self):
        """Load all market configurations"""
        for market in self.available_markets:
            config = self._load_config(market)
            if config:
                self.market_configs[market] = config
    
    def _load_config(self, market: str) -> Optional[MarketConfig]:
        """Load configuration for a specific market"""
        try:
            config_file = os.path.join(self.config_path, f"{market}.config.yml")
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                    return MarketConfig(config_data)
            else:
                logger.warning(f"Configuration file not found for market: {market}")
                return None
        except Exception as e:
            logger.error(f"Failed to load configuration for market {market}: {e}")
            return None
    
    def get_available_markets(self) -> List[str]:
        """Get list of available markets"""
        return self.available_markets.copy()
    
    def get_config(self, market: str) -> Optional[MarketConfig]:
        """Get configuration for a specific market"""
        if market not in self.market_configs:
            config = self._load_config(market)
            if config:
                self.market_configs[market] = config
        return self.market_configs.get(market)
    
    def is_supported_market(self, market: str) -> bool:
        """Check if a market is supported"""
        return market in self.available_markets
    
    def get_config_content(self, market: str) -> str:
        """Get raw configuration content for a market"""
        try:
            config_file = os.path.join(self.config_path, f"{market}.config.yml")
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return f"Config file not found for market: {market}"
        except Exception as e:
            return f"Error reading config file: {e}"


# Global instance
market_config_loader = MarketConfigLoader()
