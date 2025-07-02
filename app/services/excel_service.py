"""
Excel Service - Python equivalent of Java ExcelService
"""

import os
import tempfile
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from werkzeug.datastructures import FileStorage
from .market_config_loader import MarketConfigLoader, MarketConfig

logger = logging.getLogger(__name__)

class ValidationResult:
    """Validation result data structure"""
    
    def __init__(self, is_valid: bool, message: str, level: str = 'INFO'):
        self.is_valid = is_valid
        self.message = message
        self.level = level  # INFO, WARNING, ERROR


class ExcelService:
    """Excel processing service"""
    
    def __init__(self, market_config_loader: MarketConfigLoader):
        self.market_config_loader = market_config_loader
    
    def process_excel_file(self, file: FileStorage, market: str) -> Dict[str, Any]:
        """Process uploaded Excel file using pandas"""
        if not file or not file.filename:
            raise ValueError("File is empty")

        filename = file.filename
        if not filename or len(filename) < 2:
            raise ValueError(f"Invalid file name: {filename}")

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            file.save(temp_file.name)
            temp_file_path = temp_file.name

        try:
            config = self.market_config_loader.get_config(market)
            if not config:
                raise ValueError(f"Configuration not found for market: {market}")

            result = {}
            validation_results = []

            # Get worksheet name from config
            worksheet_name = config.get_worksheet_name()

            # Load Excel file with pandas
            try:
                # Read all sheets to check if target sheet exists
                excel_file = pd.ExcelFile(temp_file_path)
                if worksheet_name not in excel_file.sheet_names:
                    raise ValueError(f"Worksheet not found: {worksheet_name}")

                # Read the specific worksheet
                df = pd.read_excel(temp_file_path, sheet_name=worksheet_name, header=None)

            except Exception as e:
                raise ValueError(f"Failed to read Excel file: {str(e)}")

            # Extract data using pandas DataFrame
            result['data'] = self._extract_data_pandas(df, config, worksheet_name)
            result['validationResults'] = validation_results

            return result

        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file_path)
            except OSError:
                pass
    
    def _extract_data_pandas(self, df: pd.DataFrame, config: MarketConfig, worksheet_name: str) -> Dict[str, Any]:
        """Extract data from pandas DataFrame based on configuration"""
        result = {}

        result['worksheetName'] = worksheet_name

        # Get data row range from config
        data_row_range = config.get_data_row_range()
        start_row = data_row_range.get('startRow', 2) - 1  # Convert to 0-based index
        end_row = data_row_range.get('endRow', len(df))

        # Extract units data
        units = self._extract_units_data_pandas(df, config, start_row, end_row)
        result['units'] = units

        # Extract metrics data
        metrics = self._extract_metrics_data_pandas(df, config, start_row, end_row)
        result['metrics'] = metrics

        # Extract year data
        last_year_actual = self._extract_column_data_pandas(df, config.get_last_year_actual_config(), start_row, end_row)
        current_year_actual = self._extract_column_data_pandas(df, config.get_current_year_actual_config(), start_row, end_row)
        current_year_target = self._extract_column_data_pandas(df, config.get_current_year_target_config(), start_row, end_row)

        result['lastYearActual'] = last_year_actual
        result['currentYearActual'] = current_year_actual
        result['currentYearTarget'] = current_year_target

        return result
    
    def _extract_units_data_pandas(self, df: pd.DataFrame, config: MarketConfig, start_row: int, end_row: int) -> List[str]:
        """Extract units data from pandas DataFrame"""
        units_config = config.get_units_config()
        column_num = units_config.get('columnNum', 1) - 1  # Convert to 0-based index

        units = []
        end_row = min(end_row, len(df))

        for row_idx in range(start_row, end_row):
            if row_idx < len(df) and column_num < len(df.columns):
                cell_value = df.iloc[row_idx, column_num]
                if pd.notna(cell_value) and str(cell_value).strip():
                    units.append(str(cell_value).strip())

        return units

    def _extract_metrics_data_pandas(self, df: pd.DataFrame, config: MarketConfig, start_row: int, end_row: int) -> List[str]:
        """Extract metrics data from pandas DataFrame"""
        metrics_config = config.get_metrics_config()
        column_num = metrics_config.get('columnNum', 3) - 1  # Convert to 0-based index

        metrics = []
        end_row = min(end_row, len(df))

        for row_idx in range(start_row, end_row):
            if row_idx < len(df) and column_num < len(df.columns):
                cell_value = df.iloc[row_idx, column_num]
                if pd.notna(cell_value) and str(cell_value).strip():
                    metrics.append(str(cell_value).strip())

        return metrics

    def _extract_column_data_pandas(self, df: pd.DataFrame, column_config: Dict[str, Any], start_row: int, end_row: int) -> Dict[str, List[str]]:
        """Extract data from specified columns using pandas"""
        if not column_config:
            return {}

        start_column = column_config.get('startColumn', 1) - 1  # Convert to 0-based index
        end_column = column_config.get('endColumn', 12) - 1
        columns_info = column_config.get('columns', [])

        result = {}
        end_row = min(end_row, len(df))

        # Extract data for each month column
        for i, column_info in enumerate(columns_info):
            column_name = column_info.get('name', f'Column_{i+1}')
            column_index = start_column + i

            if column_index <= end_column and column_index < len(df.columns):
                column_data = self._extract_single_column_data_pandas(df, column_index, start_row, end_row)
                result[column_name] = column_data

        return result

    def _extract_single_column_data_pandas(self, df: pd.DataFrame, column_index: int, start_row: int, end_row: int) -> List[str]:
        """Extract data from a single column using pandas"""
        data = []

        for row_idx in range(start_row, end_row):
            if row_idx < len(df) and column_index < len(df.columns):
                cell_value = df.iloc[row_idx, column_index]
                if pd.notna(cell_value):
                    data.append(str(cell_value).strip())
                else:
                    data.append('')
            else:
                data.append('')

        return data


# Global instance will be initialized in controllers
