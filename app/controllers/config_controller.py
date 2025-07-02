"""
Config Controller - Python equivalent of Java ConfigController
"""

from flask import Blueprint, render_template, request
from app.services.market_config_loader import market_config_loader

# Create blueprint
config_bp = Blueprint('config', __name__)

@config_bp.route('/view')
def view():
    """View configuration for a specific market"""
    market = request.args.get('market')
    
    # Get available markets
    markets = market_config_loader.get_available_markets()
    
    # If no market specified, use the first available market
    selected_market = market
    if not selected_market and markets:
        selected_market = markets[0]
    elif not selected_market:
        selected_market = 'SG'  # Default fallback
    
    # Get configuration content
    config_content = market_config_loader.get_config_content(selected_market)
    
    return render_template('config/view.html',
                         markets=markets,
                         selectedMarket=selected_market,
                         config=config_content)
