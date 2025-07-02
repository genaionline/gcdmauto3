"""
Excel Data Service - Python equivalent of Java ExcelDataService
"""

import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.models import db, ExcelData

logger = logging.getLogger(__name__)

class ExcelDataService:
    """Excel data management service"""
    
    def save_excel_data(self, market: str, units: List[str], metrics: List[str], 
                       last_year_actual: Dict[str, List[str]], 
                       current_year_actual: Dict[str, List[str]], 
                       current_year_target: Dict[str, List[str]], 
                       data_period: str, batch_id: str, user_id: str, 
                       worksheet_name: str, upload_timestamp: datetime) -> None:
        """Save Excel data to database"""
        try:
            logger.info(f"Saving Excel data for market: {market} with batch: {batch_id}")
            
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            
            # Save new data - one record per unit/metric combination
            for i, unit in enumerate(units):
                metric = metrics[i] if i < len(metrics) else ""
                
                # Create a single ExcelData record for this unit/metric
                excel_data = ExcelData(
                    market_name=market,
                    unit_name=unit,
                    metric_name=metric,
                    data_month=data_period,
                    batch_id=batch_id,
                    user_id=user_id,
                    worksheet_name=worksheet_name,
                    upload_timestamp=upload_timestamp
                )
                
                # Set monthly data for each type
                for month in months:
                    # Last Year Actual
                    lya_key = f"{month}_LYA"
                    if lya_key in last_year_actual and i < len(last_year_actual[lya_key]):
                        excel_data.set_monthly_lya(month, last_year_actual[lya_key][i])
                    
                    # Current Year Actual
                    cya_key = f"{month}_CYA"
                    if cya_key in current_year_actual and i < len(current_year_actual[cya_key]):
                        excel_data.set_monthly_cya(month, current_year_actual[cya_key][i])
                    
                    # Current Year Target
                    cyt_key = f"{month}_CYT"
                    if cyt_key in current_year_target and i < len(current_year_target[cyt_key]):
                        excel_data.set_monthly_cyt(month, current_year_target[cyt_key][i])
                
                db.session.add(excel_data)
            
            db.session.commit()
            logger.info(f"Successfully saved {len(units)} records for market: {market}")
            
        except Exception as e:
            logger.error(f"Error saving Excel data for market: {market} with batch: {batch_id}", exc_info=True)
            db.session.rollback()
            raise RuntimeError(f"Failed to save Excel data: {str(e)}")
    
    def get_data_by_filters(self, market_name: Optional[str] = None,
                           data_month: Optional[str] = None,
                           batch_id: Optional[str] = None,
                           user_id: Optional[str] = None) -> List[ExcelData]:
        """Get data by filters with SQL injection protection"""
        try:
            # Validate and sanitize inputs
            if market_name and (len(market_name) > 255 or not market_name.replace('-', '').replace('_', '').isalnum()):
                logger.warning(f"Invalid market_name parameter: {market_name}")
                return []

            if data_month and (len(data_month) > 255 or not self._is_valid_data_month(data_month)):
                logger.warning(f"Invalid data_month parameter: {data_month}")
                return []

            if batch_id and len(batch_id) > 255:
                logger.warning(f"Invalid batch_id parameter length: {len(batch_id)}")
                return []

            if user_id and (len(user_id) > 255 or not user_id.replace('_', '').isalnum()):
                logger.warning(f"Invalid user_id parameter: {user_id}")
                return []

            logger.info(f"Querying data with filters - MarketName: {market_name}, "
                       f"DataMonth: {data_month}, BatchId: {batch_id}, UserId: {user_id}")

            query = ExcelData.query

            # Use parameterized queries (SQLAlchemy ORM automatically handles this)
            if market_name:
                query = query.filter(ExcelData.market_name == market_name)
            if data_month:
                query = query.filter(ExcelData.data_month == data_month)
            if batch_id:
                # Use exact match instead of LIKE for better security
                query = query.filter(ExcelData.batch_id.contains(batch_id))
            if user_id:
                # Use exact match instead of LIKE for better security
                query = query.filter(ExcelData.user_id.contains(user_id))

            result = query.order_by(ExcelData.batch_id.desc(),
                                   ExcelData.unit_name,
                                   ExcelData.metric_name).all()

            logger.info(f"Found {len(result)} records matching filters")
            return result

        except Exception as e:
            logger.error(f"Failed to get data by filters: {e}", exc_info=True)
            return []

    def _is_valid_data_month(self, data_month: str) -> bool:
        """Validate data month format (e.g., 2025-Apr)"""
        import re
        pattern = r'^\d{4}-(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)$'
        return bool(re.match(pattern, data_month))
    
    def get_available_markets(self) -> List[str]:
        """Get available markets from database"""
        try:
            markets = db.session.query(ExcelData.market_name).distinct().order_by(ExcelData.market_name).all()
            return [market[0] for market in markets]
        except Exception as e:
            logger.warning(f"Failed to get available markets, returning empty list: {e}")
            return []
    
    def get_available_data_months(self, market_name: Optional[str] = None) -> List[str]:
        """Get available data months"""
        try:
            query = db.session.query(ExcelData.data_month).distinct()
            if market_name:
                query = query.filter(ExcelData.market_name == market_name)
            months = query.order_by(ExcelData.data_month.desc()).all()
            return [month[0] for month in months]
        except Exception as e:
            logger.warning(f"Failed to get available data months, returning empty list: {e}")
            return []
    
    def get_available_batch_ids(self) -> List[str]:
        """Get available batch IDs"""
        try:
            batch_ids = db.session.query(ExcelData.batch_id).distinct().order_by(ExcelData.batch_id.desc()).all()
            return [batch_id[0] for batch_id in batch_ids]
        except Exception as e:
            logger.warning(f"Failed to get available batch IDs, returning empty list: {e}")
            return []
    
    def get_available_user_ids(self) -> List[str]:
        """Get available user IDs"""
        try:
            user_ids = db.session.query(ExcelData.user_id).distinct().order_by(ExcelData.user_id).all()
            return [user_id[0] for user_id in user_ids]
        except Exception as e:
            logger.warning(f"Failed to get available user IDs, returning empty list: {e}")
            return []
    
    def get_all_data(self) -> List[ExcelData]:
        """Get all data from database"""
        try:
            all_data = ExcelData.query.all()
            logger.info(f"Total records in database: {len(all_data)}")
            return all_data
        except Exception as e:
            logger.error(f"Failed to get all data: {e}", exc_info=True)
            return []
    
    def get_aggregated_data_by_filters(self, market_name: Optional[str] = None, 
                                     data_month: Optional[str] = None, 
                                     batch_id: Optional[str] = None, 
                                     user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get aggregated data by filters for display"""
        try:
            raw_data = self.get_data_by_filters(market_name, data_month, batch_id, user_id)
            result_list = []
            
            # Convert each ExcelData record to display format
            for data in raw_data:
                record = {
                    'batchId': data.batch_id,
                    'userId': data.user_id,
                    'uploadTime': data.upload_timestamp,
                    'market': data.market_name,
                    'dataMonth': data.data_month,
                    'unitName': data.unit_name,
                    'metricName': data.metric_name
                }
                
                # Create monthly data mappings
                lya = {}
                cya = {}
                cyt = {}
                
                months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                
                for month_name in months:
                    lya_value = data.get_monthly_lya(month_name)
                    cya_value = data.get_monthly_cya(month_name)
                    cyt_value = data.get_monthly_cyt(month_name)
                    
                    if lya_value and lya_value.strip():
                        lya[month_name] = lya_value
                    if cya_value and cya_value.strip():
                        cya[month_name] = cya_value
                    if cyt_value and cyt_value.strip():
                        cyt[month_name] = cyt_value
                
                record['lastYearActual'] = lya
                record['currentYearActual'] = cya
                record['currentYearTarget'] = cyt
                
                result_list.append(record)
            
            return result_list
            
        except Exception as e:
            logger.error(f"Failed to get aggregated data by filters: {e}", exc_info=True)
            return []


# Global instance
excel_data_service = ExcelDataService()
