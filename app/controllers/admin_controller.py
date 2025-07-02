"""
Admin Controller - Python equivalent of Java AdminController
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.data_period_service import data_period_service
from app.services.market_config_loader import market_config_loader
from app.services.user_service import user_service
from app.services.security_audit_service import security_audit_service
from app.models import DataPeriod
from app.security import security_required

logger = logging.getLogger(__name__)

# Create blueprint
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/datamonth', methods=['GET', 'POST'])
@security_required
def data_month():
    """Data month management page"""
    if request.method == 'GET':
        # Get all data periods and available markets
        data_periods = data_period_service.get_all_data_periods()
        markets = market_config_loader.get_available_markets()
        
        # Create new data period object for the form
        new_data_period = DataPeriod('', '', 'Y', user_service.get_admin_user_id())
        
        return render_template('admin/datamonth.html',
                             dataPeriods=data_periods,
                             markets=markets,
                             newDataPeriod=new_data_period)
    
    elif request.method == 'POST':
        try:
            # Get form data
            market_name = request.form.get('marketName')
            data_month = request.form.get('dataMonth')
            active_idc = request.form.get('activeIdc', 'Y')
            
            # Validate inputs
            if not market_name or not data_month:
                flash('Market name and data month are required', 'error')
                return redirect(url_for('admin.data_month'))
            
            # Get current user
            user_id = user_service.get_admin_user_id()
            
            # Create new data period
            data_period_service.create_data_period(
                market_name=market_name,
                data_month=data_month,
                active_idc=active_idc,
                update_by=user_id
            )
            
            # Log admin operation
            security_audit_service.log_admin_operation(
                user_id, 'CREATE_DATA_PERIOD', f'{market_name}-{data_month}', request
            )
            
            flash(f'Data period created successfully: {market_name} - {data_month}', 'success')
            return redirect(url_for('admin.data_month'))
            
        except Exception as e:
            logger.error(f"Error creating data period: {e}", exc_info=True)
            flash(f'Error creating data period: {str(e)}', 'error')
            return redirect(url_for('admin.data_month'))

@admin_bp.route('/datamonth/update/<int:period_id>', methods=['POST'])
@security_required
def update_data_month(period_id):
    """Update data period status"""
    try:
        active_idc = request.form.get('activeIdc')
        user_id = user_service.get_admin_user_id()
        
        # Update data period
        updated_period = data_period_service.update_data_period(
            period_id=period_id,
            active_idc=active_idc,
            update_by=user_id
        )
        
        if updated_period:
            # Log admin operation
            security_audit_service.log_admin_operation(
                user_id, 'UPDATE_DATA_PERIOD', f'ID:{period_id} Status:{active_idc}', request
            )
            
            flash(f'Data period updated successfully', 'success')
        else:
            flash('Data period not found', 'error')
            
    except Exception as e:
        logger.error(f"Error updating data period {period_id}: {e}", exc_info=True)
        flash(f'Error updating data period: {str(e)}', 'error')
    
    return redirect(url_for('admin.data_month'))

@admin_bp.route('/datamonth/delete/<int:period_id>', methods=['POST'])
@security_required
def delete_data_month(period_id):
    """Delete data period"""
    try:
        user_id = user_service.get_admin_user_id()
        
        # Delete data period
        success = data_period_service.delete_data_period(period_id)
        
        if success:
            # Log admin operation
            security_audit_service.log_admin_operation(
                user_id, 'DELETE_DATA_PERIOD', f'ID:{period_id}', request
            )
            
            flash('Data period deleted successfully', 'success')
        else:
            flash('Data period not found', 'error')
            
    except Exception as e:
        logger.error(f"Error deleting data period {period_id}: {e}", exc_info=True)
        flash(f'Error deleting data period: {str(e)}', 'error')
    
    return redirect(url_for('admin.data_month'))
