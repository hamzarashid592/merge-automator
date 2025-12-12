import gspread
from google.oauth2.service_account import Credentials
from core.logging_config import LoggerSetup

sheet_updater_logger = LoggerSetup.setup_logger("sheet_updater_operations", "logs/sheet_updater_operations")

class SheetUpdaterOperations:
    def __init__(self, credentials_file='credentials/credentials.json'):
        """
        Initialize Google Sheets client for sheet updater.
        """
        self.scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive'
        ]
        self.credentials_file = credentials_file
        self.client = self.setup_google_sheets()

    def setup_google_sheets(self):
        """
        Authorize and return a Google Sheets client.
        """
        creds = Credentials.from_service_account_file(self.credentials_file, scopes=self.scope)
        return gspread.authorize(creds)

    def get_ticket_numbers_and_column_indices(self, sheet_key, worksheet_name):
        """
        Get all ticket numbers from column A and find the column indices for status columns.
        
        Parameters:
            sheet_key (str): The Google Sheet key
            worksheet_name (str): The name of the worksheet
            
        Returns:
            tuple: (ticket_data, worksheet, column_indices)
                - ticket_data: List of tuples (row_index, ticket_number)
                - worksheet: The worksheet object for batch updates
                - column_indices: Dict with keys 'code_reviewed', 'qa_verified', 'ticket_merged'
        """
        try:
            spread_sheet = self.client.open_by_key(sheet_key)
            worksheet = spread_sheet.worksheet(worksheet_name)
            
            # Get header row to find column indices (single read)
            header_row = worksheet.row_values(1)
            
            # Find column indices for our target columns
            column_indices = {
                'code_reviewed': None,
                'qa_verified': None,
                'ticket_merged': None
            }
            
            for i, header in enumerate(header_row, start=1):
                header_lower = header.strip().lower()
                if header_lower == "code reviewed":
                    column_indices['code_reviewed'] = i
                elif header_lower == "qa verified":
                    column_indices['qa_verified'] = i
                elif header_lower == "ticket merged":
                    column_indices['ticket_merged'] = i
            
            sheet_updater_logger.info(f"Column indices found: {column_indices}")
            
            # Get all values from column A (skip header row)
            column_a_values = worksheet.col_values(1)
            
            # Create list of (row_index, ticket_number) starting from row 2 (index 1)
            ticket_data = []
            for i, value in enumerate(column_a_values[1:], start=2):  # start=2 because row 1 is header
                if value and value.strip():
                    ticket_data.append((i, value.strip()))
            
            sheet_updater_logger.info(f"Found {len(ticket_data)} tickets in sheet")
            return ticket_data, worksheet, column_indices
            
        except Exception as e:
            sheet_updater_logger.error(f"Error reading sheet: {e}")
            raise Exception(f"Error reading sheet: {e}")

    def update_ticket_status(self, worksheet, column_indices, row_index, code_reviewed=None, qa_verified=None, ticket_merged=None):
        """
        Update the status columns for a specific ticket row using pre-fetched column indices.
        Uses batch update to write all 3 columns in a single API call.
        
        Parameters:
            worksheet: The worksheet object
            column_indices (dict): Dictionary with column indices
            row_index (int): The row number to update
            code_reviewed (int): 1 if code reviewed, 0 otherwise, None to skip
            qa_verified (int): 1 if QA verified, 0 otherwise, None to skip
            ticket_merged (int): 1 if ticket merged, 0 otherwise, None to skip
        """
        try:
            # Prepare batch update data
            cells_to_update = []
            
            if code_reviewed is not None and column_indices['code_reviewed']:
                cells_to_update.append({
                    'range': worksheet.title + f"!{self._get_column_letter(column_indices['code_reviewed'])}{row_index}",
                    'values': [[code_reviewed]]
                })
            
            if qa_verified is not None and column_indices['qa_verified']:
                cells_to_update.append({
                    'range': worksheet.title + f"!{self._get_column_letter(column_indices['qa_verified'])}{row_index}",
                    'values': [[qa_verified]]
                })
            
            if ticket_merged is not None and column_indices['ticket_merged']:
                cells_to_update.append({
                    'range': worksheet.title + f"!{self._get_column_letter(column_indices['ticket_merged'])}{row_index}",
                    'values': [[ticket_merged]]
                })
            
            # Perform batch update (single API call for all 3 columns)
            if cells_to_update:
                worksheet.spreadsheet.values_batch_update(
                    body={'value_input_option': 'RAW', 'data': cells_to_update}
                )
                sheet_updater_logger.info(
                    f"Updated row {row_index}: Code Reviewed={code_reviewed}, "
                    f"QA Verified={qa_verified}, Ticket Merged={ticket_merged}"
                )
            
        except Exception as e:
            sheet_updater_logger.error(f"Error updating sheet at row {row_index}: {e}")
            raise Exception(f"Error updating sheet at row {row_index}: {e}")
    
    def _get_column_letter(self, col_num):
        """
        Convert column number to letter (1 -> A, 2 -> B, etc.)
        
        Parameters:
            col_num (int): Column number (1-based)
            
        Returns:
            str: Column letter(s)
        """
        letter = ''
        while col_num > 0:
            col_num, remainder = divmod(col_num - 1, 26)
            letter = chr(65 + remainder) + letter
        return letter
