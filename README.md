# GCDM Auto - Flask Application

A comprehensive Excel file processing and data management application built with Python Flask. Provides secure file upload, processing, and data management capabilities for multiple markets.

## Features

- **Excel File Upload**: Upload and process Excel files using pandas for efficient data handling
- **Market Configuration**: YAML-based configuration for each market with admin access
- **Data Management**: Store and retrieve Excel data with SQLite database
- **Hierarchical Navigation**: Organized menu structure with admin dropdown containing config and data month management
- **Enhanced Security**: Comprehensive security measures including input validation, rate limiting, and attack prevention
- **Security Auditing**: Detailed logging and security monitoring with real-time threat detection
- **Modern UI**: Responsive web interface with optimized red color scheme and intuitive navigation
- **Cross-Platform**: Support for both Linux/macOS and Windows with dedicated startup scripts

## Project Structure

```
gcdmauto3/
├── app/
│   ├── controllers/          # Flask route controllers
│   ├── models/              # SQLAlchemy database models
│   ├── services/            # Business logic services
│   ├── templates/           # Jinja2 HTML templates
│   └── static/              # Static files (CSS, JS, uploads)
├── config/                  # Market configuration files
├── tests/                   # Test cases
├── venv/                   # Python virtual environment
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── start.sh               # Startup script
└── README.md              # This file
```

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Steps

#### For Linux/macOS:

1. **Clone or navigate to the project directory**
   ```bash
   cd gcdmauto3
   ```

2. **Set up the environment (first time only)**
   ```bash
   ./setup_env.sh
   ```

3. **Start the application**
   ```bash
   ./start.sh
   ```

   The script will:
   - Check if port 8080 is in use
   - Ask for permission to kill existing processes if needed
   - Automatically handle environment setup
   - Start the Flask application

#### For Windows 11:

1. **Open Command Prompt or PowerShell as Administrator**
   ```cmd
   cd gcdmauto3
   ```

2. **Set up the environment (first time only)**
   ```cmd
   setup_env.bat
   ```

3. **Start the application**
   ```cmd
   start.bat
   ```

   The script will:
   - Detect port conflicts using netstat
   - Show process details and ask for confirmation
   - Validate Python and dependencies
   - Start the Flask application

#### Manual Setup (if scripts don't work):
   ```bash
   # Activate virtual environment
   source venv/bin/activate          # Linux/macOS
   venv\Scripts\activate.bat         # Windows

   # Start the application
   python app.py
   ```

4. **Access the application**
   - Open your web browser
   - Navigate to: http://localhost:8080 (localhost only for security)
   - The application will automatically redirect to the upload page

## Scripts

### Linux/macOS Scripts

#### setup_env.sh
Environment setup script (run once):
- Creates Python virtual environment
- Installs all dependencies
- Creates necessary directories
- Validates the setup

#### start.sh
Application startup script:
- **Smart port management**: Automatically detects if port 8080 is in use
- **Interactive kill prompt**: Asks user permission before killing existing processes
- **Process details**: Shows which process is using the port
- **Environment health check**: Validates virtual environment and dependencies
- **Graceful error handling**: Clear error messages and exit codes

### Windows Scripts

#### setup_env.bat
Windows environment setup script:
- Creates Python virtual environment
- Installs all dependencies
- Creates necessary directories
- Windows-specific path handling

#### start.bat
Windows application startup script:
- **Port conflict detection**: Uses netstat to check port 8080 usage
- **Interactive process management**: User confirmation before killing processes
- **Process information**: Shows PID and process details
- **Environment validation**: Checks Python, virtual environment, and dependencies
- **UTF-8 support**: Proper Unicode character display

## Usage

### 1. Upload Excel Files
- Navigate to the Upload page (default landing page)
- Select a market from the dropdown
- Choose a data month
- Upload your Excel file (.xlsx or .xls)
- View the processing results

### 2. View Data
- Use "View Data" to see all uploaded data
- Apply filters by market, data month, batch ID, or user
- View statistics and data records

### 3. Configuration Management
- Access "Config" to view market-specific configurations
- Each market has its own YAML configuration file
- Configurations define Excel file structure and processing rules

### 4. Admin Functions
- Access "Admin" for data period management
- Create, activate, deactivate, or delete data periods
- Manage which data periods are available for upload

## Configuration

### Market Configuration
Market configurations are stored in `config/market/` directory:
- `config/all.markets.config.yml` - List of available markets
- `config/market/{MARKET}.config.yml` - Individual market configurations

### Application Configuration
Main application settings in `app.py`:
- Database: SQLite (file: `gcdmauto.db`)
- Host: 127.0.0.1 (localhost only for security)
- Port: 8080
- Upload folder: `app/static/uploads`
- Max file size: 16MB

## Database

The application uses SQLite database with two main tables:
- **excel_data**: Stores processed Excel data
- **data_period**: Manages data periods for different markets

Database file: `gcdmauto.db` (created automatically)

## Testing

Run tests using pytest:
```bash
# Activate virtual environment
source venv/bin/activate

# Run tests
python -m pytest tests/ -v
```

## Security Features

### Comprehensive Security Measures
- **Network Security**: Application only binds to localhost (127.0.0.1) - no external access
- **Input Validation**: All user inputs validated against suspicious patterns and length limits
- **SQL Injection Protection**: Parameterized queries and input sanitization
- **XSS Prevention**: Content Security Policy and input/output encoding
- **Rate Limiting**: Per-IP request limits to prevent abuse
- **File Upload Security**: Filename validation, extension checking, size limits
- **Security Headers**: Comprehensive HTTP security headers
- **Request Monitoring**: Detailed logging of all security events
- **Path Traversal Protection**: Validation against directory traversal attacks
- **Command Injection Prevention**: Input pattern matching for command injection attempts

### Security Headers Applied
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Content-Security-Policy: Strict policy
- Referrer-Policy: strict-origin-when-cross-origin
- Cache-Control: no-cache, no-store, must-revalidate
- Cross-Origin policies for enhanced isolation

### Rate Limiting
- 60 requests per minute per IP
- 1000 requests per hour per IP
- Automatic IP blocking for violations
- 1-hour block duration for abusive IPs

## API Endpoints

### Main Routes
- `GET /` - Home (redirects to upload)
- `GET /excel/upload` - Upload page
- `POST /excel/upload` - Process file upload
- `GET /excel/viewallmarketresults` - View all data
- `GET /config/view` - Configuration viewer
- `GET /admin/datamonth` - Admin data period management

## Troubleshooting

### Common Issues

1. **Port 8080 already in use**
   - Change the port in `app.py` (line with `app.run`)
   - Or stop other services using port 8080

2. **Virtual environment issues**
   - Recreate virtual environment: `python3 -m venv venv`
   - Activate and reinstall dependencies

3. **Template not found errors**
   - Ensure `app/templates/` directory exists
   - Check template file paths in controllers

4. **Database errors**
   - Delete `gcdmauto.db` to reset database
   - Restart application to recreate tables

## Development

### Adding New Markets
1. Add market code to `config/all.markets.config.yml`
2. Create `config/market/{MARKET}.config.yml`
3. Define Excel file structure and processing rules

### Extending Functionality
- Add new routes in `app/controllers/`
- Create new services in `app/services/`
- Add database models in `app/models/`
- Create templates in `app/templates/`

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review application logs in the terminal
3. Check browser developer console for frontend issues
