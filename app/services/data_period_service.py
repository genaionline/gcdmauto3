"""
Data Period Service - Python equivalent of Java DataPeriodService
"""

import logging
from typing import List, Optional
from app.models import db, DataPeriod

logger = logging.getLogger(__name__)

class DataPeriodService:
    """Data period management service"""
    
    def get_active_data_periods_by_market(self, market_name: str) -> List[DataPeriod]:
        """Get active data periods for a specific market"""
        try:
            return DataPeriod.query.filter(
                DataPeriod.market_name == market_name,
                DataPeriod.active_idc == 'Y'
            ).order_by(DataPeriod.data_month.desc()).all()
        except Exception as e:
            logger.warning(f"Failed to get active data periods for market {market_name}, "
                          f"returning empty list: {e}")
            return []
    
    def get_all_active_data_periods(self) -> List[DataPeriod]:
        """Get all active data periods"""
        try:
            return DataPeriod.query.filter(
                DataPeriod.active_idc == 'Y'
            ).order_by(DataPeriod.market_name, DataPeriod.data_month.desc()).all()
        except Exception as e:
            logger.warning(f"Failed to get all active data periods, returning empty list: {e}")
            return []
    
    def get_all_data_periods(self) -> List[DataPeriod]:
        """Get all data periods"""
        try:
            return DataPeriod.query.order_by(
                DataPeriod.market_name, 
                DataPeriod.data_month.desc()
            ).all()
        except Exception as e:
            logger.warning(f"Failed to get all data periods, returning empty list: {e}")
            return []
    
    def get_data_period_by_id(self, period_id: int) -> Optional[DataPeriod]:
        """Get data period by ID"""
        try:
            return DataPeriod.query.get(period_id)
        except Exception as e:
            logger.warning(f"Failed to get data period by ID {period_id}: {e}")
            return None
    
    def create_data_period(self, market_name: str, data_month: str, 
                          active_idc: str = 'Y', update_by: str = 'admin') -> DataPeriod:
        """Create a new data period"""
        try:
            # Check if data period already exists
            existing = DataPeriod.query.filter(
                DataPeriod.market_name == market_name,
                DataPeriod.data_month == data_month
            ).first()
            
            if existing:
                raise ValueError(f"Data period already exists for {market_name} - {data_month}")
            
            data_period = DataPeriod(
                market_name=market_name,
                data_month=data_month,
                active_idc=active_idc,
                update_by=update_by
            )
            
            db.session.add(data_period)
            db.session.commit()
            
            logger.info(f"Created data period: {market_name} - {data_month}")
            return data_period
            
        except Exception as e:
            logger.error(f"Failed to create data period: {e}", exc_info=True)
            db.session.rollback()
            raise
    
    def update_data_period(self, period_id: int, active_idc: str, 
                          update_by: str = 'admin') -> Optional[DataPeriod]:
        """Update data period status"""
        try:
            data_period = DataPeriod.query.get(period_id)
            if not data_period:
                return None
            
            data_period.active_idc = active_idc
            data_period.update_by = update_by
            data_period.update_time = db.func.now()
            
            db.session.commit()
            
            logger.info(f"Updated data period {period_id}: {active_idc}")
            return data_period
            
        except Exception as e:
            logger.error(f"Failed to update data period {period_id}: {e}", exc_info=True)
            db.session.rollback()
            raise
    
    def delete_data_period(self, period_id: int) -> bool:
        """Delete data period"""
        try:
            data_period = DataPeriod.query.get(period_id)
            if not data_period:
                return False
            
            db.session.delete(data_period)
            db.session.commit()
            
            logger.info(f"Deleted data period {period_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete data period {period_id}: {e}", exc_info=True)
            db.session.rollback()
            raise
    
    def get_available_markets(self) -> List[str]:
        """Get available markets from data periods"""
        try:
            markets = db.session.query(DataPeriod.market_name).distinct().order_by(DataPeriod.market_name).all()
            return [market[0] for market in markets]
        except Exception as e:
            logger.warning(f"Failed to get available markets, returning empty list: {e}")
            return []


# Global instance
data_period_service = DataPeriodService()
