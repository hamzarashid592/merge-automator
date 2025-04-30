import gspread
from google.oauth2.service_account import Credentials
from core.config_manager import ConfigurationManager

# Initialize the configuration manager
config = ConfigurationManager()

class GoogleSheetsOperations:
    def __init__(self, credentials_file='credentials/credentials.json'):
        """
        Initialize Google Sheets client using the provided credentials file.
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

    def update_dev_status_in_sheet(self, original_ticket_id):
        """
        Update the status of a ticket in the Google Sheets by searching across multiple worksheets.

        Parameters:
            original_ticket_id (str): The ticket ID to update in the sheets.
        """
        if original_ticket_id is None:
            return

        try:
            # Open the spreadsheet
            spread_sheet = self.client.open_by_key(config.get("CODE_MOVE_SHEET_KEY"))

            # Fetch data from both sheets
            sheet_64 = spread_sheet.worksheet(config.get("MASTER_64_TO_NEXUS"))
            data_64 = sheet_64.get_all_values()

            sheet_65 = spread_sheet.worksheet(config.get("MASTER_65_TO_NEXUS"))  # Add the name of the second sheet
            data_65 = sheet_65.get_all_values()

            # Combine the data from both sheets
            all_data = [(sheet_64, data_64)] + [(sheet_65, data_65)]

            # Remove leading zeros from the ticket ID
            original_ticket_id_number = int(str(original_ticket_id).lstrip('0'))

            # Search for the ticket ID in the combined data
            for sheet, data in all_data:
                for i in range(1, len(data)):
                    if data[i][0] and '#' in data[i][0]:
                        ticket_id_from_sheet = int(data[i][0].split('#')[1].lstrip('0'))
                        if ticket_id_from_sheet == original_ticket_id_number:
                            sheet.update_cell(i + 1, 16, True)  # Update DEV Status
                            # Uncomment if QA Status also needs updating
                            # sheet.update_cell(i + 1, 17, True)
                            # return  # Exit the function once the update is complete
        except Exception as e:
            raise Exception(f"Error updating status in sheets: {e}")


    def update_comments_in_sheet(self, original_ticket_id, comments):
        """
        Update the comments of a ticket in the Google Sheets by searching across multiple worksheets.

        Parameters:
            original_ticket_id (str): The ticket ID to update in the sheets.
        """
        if original_ticket_id is None:
            return

        try:
            # Open the spreadsheet
            spread_sheet = self.client.open_by_key(config.get("CODE_MOVE_SHEET_KEY"))

            # Fetch data from both sheets
            sheet_64 = spread_sheet.worksheet(config.get("MASTER_64_TO_NEXUS"))
            data_64 = sheet_64.get_all_values()

            sheet_65 = spread_sheet.worksheet(config.get("MASTER_65_TO_NEXUS"))  # Add the name of the second sheet
            data_65 = sheet_65.get_all_values()

            # Combine the data from both sheets
            all_data = [(sheet_64, data_64)] + [(sheet_65, data_65)]

            # Remove leading zeros from the ticket ID
            original_ticket_id_number = int(original_ticket_id.lstrip('0'))

            # Search for the ticket ID in the combined data
            for sheet, data in all_data:
                for i in range(1, len(data)):
                    if data[i][0] and '#' in data[i][0]:
                        ticket_id_from_sheet = int(data[i][0].split('#')[1].lstrip('0'))
                        if ticket_id_from_sheet == original_ticket_id_number:
                            sheet.update_cell(i + 1, 18, comments)  # Updating the Comments
                            
                            # return  # Exit the function once the update is complete
        except Exception as e:
            raise Exception(f"Error updating status in sheets: {e}")
        

    def update_comments_and_dev_status_in_sheet(self, original_ticket_id, comments):
        """
        Update the comments and dev status of a ticket in the Google Sheets by searching across multiple worksheets.

        Parameters:
            original_ticket_id (str): The ticket ID to update in the sheets.
        """
        if original_ticket_id is None:
            return

        try:
            # Open the spreadsheet
            spread_sheet = self.client.open_by_key(config.get("CODE_MOVE_SHEET_KEY"))

            # Fetch data from both sheets
            sheet_64 = spread_sheet.worksheet(config.get("MASTER_64_TO_NEXUS"))
            data_64 = sheet_64.get_all_values()

            sheet_65 = spread_sheet.worksheet(config.get("MASTER_65_TO_NEXUS"))  # Add the name of the second sheet
            data_65 = sheet_65.get_all_values()

            # Combine the data from both sheets
            all_data = [(sheet_64, data_64)] + [(sheet_65, data_65)]

            # Remove leading zeros from the ticket ID
            original_ticket_id_number = int(original_ticket_id.lstrip('0'))

            # Search for the ticket ID in the combined data
            for sheet, data in all_data:
                for i in range(1, len(data)):
                    if data[i][0] and '#' in data[i][0]:
                        ticket_id_from_sheet = int(data[i][0].split('#')[1].lstrip('0'))
                        if ticket_id_from_sheet == original_ticket_id_number:
                            sheet.update_cell(i + 1, 16, True)  # Update DEV Status
                            sheet.update_cell(i + 1, 18, comments)  # Updating the Comments
                            # return  # Exit the function once the update is complete
        except Exception as e:
            raise Exception(f"Error updating status in sheets: {e}")
        
    def add_hyperlinks_in_sheet(self):
        """
        Adds hyperlinks to the ticket numbers in the Ticket# column of two sheets.
        """
        try:
            spread_sheet = self.client.open_by_key(config.get("CODE_MOVE_SHEET_KEY"))

            sheet_64 = spread_sheet.worksheet(config.get("MASTER_64_TO_NEXUS"))
            sheet_65 = spread_sheet.worksheet(config.get("MASTER_65_TO_NEXUS"))

            for sheet in [sheet_64, sheet_65]:
                data = sheet.get_all_values()
                total_tickets = len(data) - 1
                for i in range(1, len(data)):
                    ticket_cell_value = data[i][0]
                    if ticket_cell_value and "MT#" not in ticket_cell_value:
                        ticket_number = ticket_cell_value.strip()
                        if ticket_number.isdigit():
                            mantis_link = f'{config.get("MANTIS_PATH")}/view.php?id={ticket_number}'
                            hyperlink_formula = f'=HYPERLINK("{mantis_link}", "MT#{ticket_number}")'
                            sheet.update_cell(i + 1, 1, hyperlink_formula)
                            print(f"Progress: {(i / total_tickets) * 100:.2f}% ({i}/{total_tickets}) completed")
        except Exception as e:
            raise Exception(f"Error updating hyperlinks in sheets: {e}")
