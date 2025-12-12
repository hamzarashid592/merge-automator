# Sheet Updater Feature

## Overview
The Sheet Updater feature automatically updates a Google Sheet with ticket status information by fetching data from Mantis tickets and GitLab merge requests.

## Files Created

### 1. Configuration
- **configs/sheet_updater.json**: Configuration file containing:
  - `SHEET_URL`: The Google Sheet URL to update
  - `SHEET_KEY`: Extracted sheet key from the URL
  - `WORKSHEET_NAME`: Name of the worksheet to update (default: "Sheet1")

### 2. Core Logic
- **projects/sheet_updater_handler.py**: Main handler that:
  - Reads ticket numbers from column A of the sheet
  - Fetches ticket data from Mantis
  - Extracts merge request URLs from ticket notes
  - Fetches MR data from GitLab
  - Checks for "Code Reviewed" and "QA Verified" labels
  - Checks if MR is merged
  - Updates the sheet columns accordingly

### 3. Operations
- **operations/sheet_updater_operations.py**: Google Sheets operations including:
  - `get_ticket_numbers_from_sheet()`: Reads all ticket numbers from column A
  - `update_ticket_status()`: Updates the Code Reviewed, QA Verified, and Ticket Merged columns

### 4. Routes
- **projects/sheet_updater_routes.py**: Flask blueprint with routes:
  - `/sheet-updater` (GET): Show the UI form
  - `/sheet-updater/start` (POST): Start the update job
  - `/sheet-updater/progress` (GET): Get current progress
  - `/sheet-updater/config` (GET/POST): Manage configuration

### 5. UI
- **templates/sheet_updater.html**: Web interface with:
  - Input field for Google Sheet URL
  - Start button to trigger the job
  - Progress bar showing completion percentage
  - Status display with real-time updates

### 6. Integration
- Updated **app.py**: Registered the new blueprint
- Updated **templates/index.html**: Added "Sheet Updater" tab

## How It Works

1. User enters the Google Sheet URL in the web interface
2. Click "Start Update" to trigger the job
3. The system:
   - Reads all ticket numbers from column A (starting from row 2)
   - For each ticket:
     - Fetches ticket data from Mantis
     - Extracts MR URL from ticket notes
     - Fetches MR data from GitLab
     - Checks for labels: "Code Reviewed", "Reviewed", "QA Verified", "QA Accepted"
     - Checks if MR state is "merged"
     - Updates sheet columns with 1 (true) or 0 (false)
4. Progress is tracked and displayed in real-time
5. Summary is logged with counts of successful/failed updates

## Sheet Columns Expected

The Google Sheet should have these column headers:
- Column A: Ticket numbers (with or without # prefix)
- "Code Reviewed": Updated to 1 if MR has "Code Reviewed" or "Reviewed" label
- "QA Verified": Updated to 1 if MR has "QA Verified" or "QA Accepted" label
- "Ticket Merged": Updated to 1 if MR state is "merged"

## Configuration

The sheet updater uses the same credentials as other features:
- Google Sheets: Uses `credentials/credentials.json`
- Mantis: Uses tokens from `encrypted_tokens_regression.txt`
- GitLab: Uses tokens from `encrypted_tokens_regression.txt`

## Usage

1. Navigate to the main dashboard
2. Click on the "Sheet Updater" tab
3. Enter or verify the Google Sheet URL
4. Click "Start Update"
5. Monitor progress in real-time
6. Check logs at `/view-logs/sheet_updater`

## Design Pattern

This feature follows the existing project architecture:
- Uses ConfigurationManager for config handling
- Uses separate operations classes for external services
- Uses Flask blueprints for route organization
- Uses LoggerSetup for logging
- Uses TokenManager for secure credential storage
- Implements progress tracking similar to other features
