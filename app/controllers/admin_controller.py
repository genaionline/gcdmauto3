"""
Admin Controller - Python equivalent of Java AdminController
"""

import logging
import os
import glob
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app
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

@admin_bp.route('/download', methods=['GET', 'POST'])
@security_required
def download():
    """File download page"""
    if request.method == 'GET':
        # Get available markets and data periods
        markets = market_config_loader.get_available_markets()
        all_data_periods = data_period_service.get_all_active_data_periods()

        # Convert DataPeriod objects to dictionaries
        data_periods_dict = []
        for period in all_data_periods:
            data_periods_dict.append({
                'market_name': period.market_name,
                'data_month': period.data_month,
                'active_idc': period.active_idc
            })

        return render_template('admin/download.html',
                             markets=markets,
                             allDataPeriods=data_periods_dict,
                             files=[])

    elif request.method == 'POST':
        # Get filter parameters
        market = request.form.get('market', '').strip()
        data_month = request.form.get('dataMonth', '').strip()
        batch_id = request.form.get('batchId', '').strip()

        # Get available markets and data periods for the form
        markets = market_config_loader.get_available_markets()
        all_data_periods = data_period_service.get_all_active_data_periods()

        # Convert DataPeriod objects to dictionaries
        data_periods_dict = []
        for period in all_data_periods:
            data_periods_dict.append({
                'market_name': period.market_name,
                'data_month': period.data_month,
                'active_idc': period.active_idc
            })

        # Search for files based on filters
        upload_folder = current_app.config['UPLOAD_FOLDER']
        files = []

        try:
            # Build search pattern
            pattern_parts = []
            if market:
                pattern_parts.append(market)
            else:
                pattern_parts.append('*')

            if data_month:
                pattern_parts.append(data_month)
            else:
                pattern_parts.append('*')

            # Add wildcard for timestamp and uuid parts
            pattern_parts.extend(['*', '*'])

            if batch_id:
                # If specific batch_id is provided, search for it
                search_pattern = os.path.join(upload_folder, f"*{batch_id}*")
            else:
                # Build pattern from market and data_month
                search_pattern = os.path.join(upload_folder, f"{'_'.join(pattern_parts)}*")

            # Find matching files
            matching_files = glob.glob(search_pattern)

            for file_path in matching_files:
                filename = os.path.basename(file_path)
                # Extract batch_id from filename (everything before the original filename)
                if '_' in filename:
                    parts = filename.split('_')
                    if len(parts) >= 4:  # market_datamonth_timestamp_uuid_originalfile
                        file_batch_id = '_'.join(parts[:4])
                        original_filename = '_'.join(parts[4:])

                        # Get file info
                        file_stat = os.stat(file_path)
                        file_size = file_stat.st_size
                        upload_time = datetime.fromtimestamp(file_stat.st_mtime)

                        files.append({
                            'filename': filename,
                            'original_filename': original_filename,
                            'batch_id': file_batch_id,
                            'file_size': file_size,
                            'upload_time': upload_time,
                            'download_url': url_for('admin.download_file', filename=filename)
                        })

            # Sort files by upload time (newest first)
            files.sort(key=lambda x: x['upload_time'], reverse=True)

        except Exception as e:
            logger.error(f"Error searching for files: {e}", exc_info=True)
            flash(f'Error searching for files: {str(e)}', 'error')

        return render_template('admin/download.html',
                             markets=markets,
                             allDataPeriods=data_periods_dict,
                             files=files,
                             selected_market=market,
                             selected_data_month=data_month,
                             selected_batch_id=batch_id)

@admin_bp.route('/download/file/<filename>')
@security_required
def download_file(filename):
    """Download a specific file"""
    try:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, filename)

        # Security check: ensure file exists and is in upload folder
        if not os.path.exists(file_path) or not os.path.commonpath([upload_folder, file_path]) == upload_folder:
            flash('File not found or access denied.', 'error')
            return redirect(url_for('admin.download'))

        # Extract original filename for download
        if '_' in filename:
            parts = filename.split('_')
            if len(parts) >= 5:  # market_datamonth_timestamp_uuid_originalfile
                original_filename = '_'.join(parts[4:])
            else:
                original_filename = filename
        else:
            original_filename = filename

        # Log download activity
        user_id = user_service.get_user_id()
        security_audit_service.log_file_download(user_id, filename, request)

        return send_file(file_path, as_attachment=True, download_name=original_filename)

    except Exception as e:
        logger.error(f"Error downloading file {filename}: {e}", exc_info=True)
        flash(f'Error downloading file: {str(e)}', 'error')
        return redirect(url_for('admin.download'))
