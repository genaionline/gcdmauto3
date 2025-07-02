"""
Excel Controller - Python equivalent of Java ExcelController
"""

import os
import uuid
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from werkzeug.utils import secure_filename

from app.services.market_config_loader import market_config_loader
from app.services.excel_service import ExcelService
from app.services.excel_data_service import excel_data_service
from app.services.data_period_service import data_period_service
from app.services.user_service import user_service
from app.services.security_audit_service import security_audit_service
from app.security import security_required

logger = logging.getLogger(__name__)

# Create blueprint
excel_bp = Blueprint('excel', __name__)

# Initialize Excel service
excel_service = ExcelService(market_config_loader)

@excel_bp.route('/upload', methods=['GET', 'POST', 'HEAD'])
@security_required
def upload():
    """Excel file upload page"""
    if request.method == 'HEAD':
        # Return empty response for HEAD requests
        return '', 200
    elif request.method == 'GET':
        # Get available markets and data periods
        markets = market_config_loader.get_available_markets()
        all_data_periods = data_period_service.get_all_active_data_periods()

        # Convert DataPeriod objects to dictionaries for JSON serialization
        data_periods_dict = []
        for period in all_data_periods:
            data_periods_dict.append({
                'market_name': period.market_name,
                'data_month': period.data_month,
                'active_idc': period.active_idc
            })

        return render_template('excel/upload.html',
                             markets=markets,
                             allDataPeriods=data_periods_dict)
    
    elif request.method == 'POST':
        try:
            # Get form data
            market = request.form.get('market')
            data_month = request.form.get('dataMonth')
            file = request.files.get('file')
            
            # Validate inputs
            if not market or not data_month or not file:
                flash('Please fill in all required fields', 'error')
                return redirect(url_for('excel.upload'))
            
            if not market_config_loader.is_supported_market(market):
                flash(f'Unsupported market: {market}', 'error')
                return redirect(url_for('excel.upload'))
            
            # Get user info
            user_id = user_service.get_user_id()
            
            # Generate batch ID
            batch_id = f"{market}_{data_month}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"

            # Save the uploaded file with batch_id prefix for later download
            saved_filename = f"{batch_id}_{secure_filename(file.filename)}"
            saved_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], saved_filename)
            file.save(saved_file_path)
            file.seek(0)  # Reset file pointer for processing

            # Log file upload
            security_audit_service.log_file_upload(
                user_id, file.filename, len(file.read()), market, request
            )
            file.seek(0)  # Reset file pointer

            # Process Excel file
            result = excel_service.process_excel_file(file, market)
            data = result.get('data', {})
            
            # Save data to database
            excel_data_service.save_excel_data(
                market=market,
                units=data.get('units', []),
                metrics=data.get('metrics', []),
                last_year_actual=data.get('lastYearActual', {}),
                current_year_actual=data.get('currentYearActual', {}),
                current_year_target=data.get('currentYearTarget', {}),
                data_period=data_month,
                batch_id=batch_id,
                user_id=user_id,
                worksheet_name=data.get('worksheetName', ''),
                upload_timestamp=datetime.now()
            )
            
            flash('File uploaded and processed successfully!', 'success')
            return redirect(url_for('excel.result', 
                                  market=market, 
                                  dataMonth=data_month, 
                                  batchId=batch_id))
            
        except Exception as e:
            logger.error(f"Error processing file upload: {e}", exc_info=True)
            flash(f'Error processing file: {str(e)}', 'error')
            return redirect(url_for('excel.upload'))

@excel_bp.route('/result')
def result():
    """Display upload results"""
    market = request.args.get('market')
    data_month = request.args.get('dataMonth')
    batch_id = request.args.get('batchId')
    
    if not all([market, data_month, batch_id]):
        flash('Missing required parameters', 'error')
        return redirect(url_for('excel.upload'))
    
    # Get data for display
    data_list = excel_data_service.get_data_by_filters(
        market_name=market,
        data_month=data_month,
        batch_id=batch_id
    )
    
    # Prepare data for template
    if data_list:
        sample_data = data_list[0]
        data = {
            'worksheetName': sample_data.worksheet_name,
            'units': [d.unit_name for d in data_list],
            'metrics': [d.metric_name for d in data_list]
        }
    else:
        data = {'worksheetName': '', 'units': [], 'metrics': []}
    
    return render_template('excel/result.html', 
                         market=market,
                         dataMonth=data_month,
                         batchId=batch_id,
                         data=data)

@excel_bp.route('/view')
def view():
    """View Excel data"""
    market = request.args.get('market')
    data_month = request.args.get('dataMonth')
    batch_id = request.args.get('batchId')
    
    # Get data for display
    data_list = excel_data_service.get_data_by_filters(
        market_name=market,
        data_month=data_month,
        batch_id=batch_id
    )
    
    # Prepare data for template
    if data_list:
        sample_data = data_list[0]
        data = {
            'worksheetName': sample_data.worksheet_name,
            'units': [d.unit_name for d in data_list],
            'metrics': [d.metric_name for d in data_list]
        }
    else:
        data = {'worksheetName': '', 'units': [], 'metrics': []}
    
    return render_template('excel/view.html', 
                         market=market,
                         dataMonth=data_month,
                         batchId=batch_id,
                         data=data)

@excel_bp.route('/viewallmarketresults')
@security_required
def view_all_market_results():
    """View all market results with filtering"""
    # Get filter parameters
    selected_market = request.args.get('selectedMarket')
    selected_data_month = request.args.get('selectedDataMonth')
    selected_batch_id = request.args.get('selectedBatchId')
    selected_user_id = request.args.get('selectedUserId')
    
    # Get available filter options
    markets = excel_data_service.get_available_markets()
    data_months = excel_data_service.get_available_data_months()
    batch_ids = excel_data_service.get_available_batch_ids()
    user_ids = excel_data_service.get_available_user_ids()
    
    # Get aggregated data
    aggregated_data = excel_data_service.get_aggregated_data_by_filters(
        market_name=selected_market,
        data_month=selected_data_month,
        batch_id=selected_batch_id,
        user_id=selected_user_id
    )
    
    # Calculate statistics
    total_records = len(aggregated_data)
    unique_batches = len(set(item['batchId'] for item in aggregated_data))
    unique_users = len(set(item['userId'] for item in aggregated_data))
    unique_markets = len(set(item['market'] for item in aggregated_data))

    # Calculate monthly data statistics for 3 categories
    monthly_stats = {
        'lastYearActual': {},
        'currentYearActual': {},
        'currentYearTarget': {}
    }

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    for item in aggregated_data:
        for category in ['lastYearActual', 'currentYearActual', 'currentYearTarget']:
            if category in item and item[category]:
                for month in months:
                    if month in item[category] and item[category][month]:
                        if month not in monthly_stats[category]:
                            monthly_stats[category][month] = 0
                        monthly_stats[category][month] += 1

    return render_template('excel/viewallmarketresults.html',
                         markets=markets,
                         dataMonths=data_months,
                         batchIds=batch_ids,
                         userIds=user_ids,
                         selectedMarket=selected_market,
                         selectedDataMonth=selected_data_month,
                         selectedBatchId=selected_batch_id,
                         selectedUserId=selected_user_id,
                         aggregatedData=aggregated_data,
                         totalRecords=total_records,
                         uniqueBatches=unique_batches,
                         uniqueUsers=unique_users,
                         uniqueMarkets=unique_markets,
                         monthlyStats=monthly_stats,
                         months=months)
