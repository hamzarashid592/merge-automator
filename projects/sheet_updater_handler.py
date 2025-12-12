import re
import time
from core.logging_config import LoggerSetup
from operations.mantis_operations import MantisOperations
from operations.gitlab_operations import GitLabOperations
from operations.sheet_updater_operations import SheetUpdaterOperations
from core.config_manager import ConfigurationManager
from core.string_constants import StringConstants

sheet_updater_logger = LoggerSetup.setup_logger("sheet_updater", "logs/sheet_updater")

# Progress tracking
progress = {"status": "idle", "percentage": 0, "message": ""}

def extract_merge_request_urls_from_notes(notes):
    """
    Extract all merge request URLs from ticket notes.
    
    Parameters:
        notes (list): List of note dictionaries from Mantis ticket
        
    Returns:
        list: List of all merge request URLs found
    """
    merge_request_pattern = r"http://gitlab\.sibisoft\.com:7070/.*?/merge_requests/\d+"
    mr_urls = []
    
    if notes:
        for note in notes:
            note_text = note.get("text", "")
            matches = re.findall(merge_request_pattern, note_text)
            if matches:
                mr_urls.extend(matches)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_urls = []
    for url in mr_urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    
    return unique_urls


def check_mr_tags(merge_request_data):
    """
    Check if MR has specific tags.
    
    Parameters:
        merge_request_data (dict): Merge request data from GitLab
        
    Returns:
        tuple: (has_code_reviewed, has_qa_verified, is_merged)
    """
    has_code_reviewed = False
    has_qa_verified = False
    is_merged = False
    
    if not merge_request_data:
        return has_code_reviewed, has_qa_verified, is_merged
    
    # Check if MR is merged
    if merge_request_data.get("state") == "merged":
        is_merged = True
    
    # Check for labels
    labels = merge_request_data.get("labels", [])
    
    # Check for Code Reviewed tag
    if any(label in labels for label in ("Code Reviewed", "Reviewed")):
        has_code_reviewed = True
    
    # Check for QA Verified tag
    if any(label in labels for label in ("QA Verified", "QA Accepted")):
        has_qa_verified = True
    
    return has_code_reviewed, has_qa_verified, is_merged


def run_sheet_updater(sheet_url=None):
    """
    Main function to update the Google Sheet based on Mantis tickets and GitLab MRs.
    
    Parameters:
        sheet_url (str): Optional sheet URL to update in config
    """
    global progress
    
    try:
        progress["status"] = "running"
        progress["percentage"] = 0
        progress["message"] = "Initializing..."
        
        # Load configuration
        config = ConfigurationManager(config_file="configs/sheet_updater.json")
        
        # Update sheet URL if provided
        if sheet_url:
            # Extract sheet key from URL
            sheet_key_match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', sheet_url)
            if sheet_key_match:
                sheet_key = sheet_key_match.group(1)
                config.set("SHEET_KEY", sheet_key)
                config.set("SHEET_URL", sheet_url)
                sheet_updater_logger.info(f"Updated sheet URL to: {sheet_url}")
            else:
                sheet_updater_logger.error("Invalid sheet URL format")
                progress["status"] = "error"
                progress["message"] = "Invalid sheet URL format"
                return
        
        # Get configuration values
        sheet_key = config.get("SHEET_KEY")
        worksheet_name = config.get("WORKSHEET_NAME")
        
        # Initialize operations
        sheet_updater_logger.info("Initializing operations...")
        progress["message"] = "Initializing operations..."
        
        mantis = MantisOperations(StringConstants.REGRESSION)
        gitlab = GitLabOperations(StringConstants.REGRESSION)
        sheets = SheetUpdaterOperations()
        
        # Get ticket numbers from sheet and column indices (single read operation)
        sheet_updater_logger.info("Reading tickets from sheet...")
        progress["message"] = "Reading tickets from sheet..."
        progress["percentage"] = 10
        
        ticket_data, worksheet, column_indices = sheets.get_ticket_numbers_and_column_indices(sheet_key, worksheet_name)
        
        if not ticket_data:
            sheet_updater_logger.info("No tickets found in sheet")
            progress["status"] = "completed"
            progress["percentage"] = 100
            progress["message"] = "No tickets found in sheet"
            return
        
        total_tickets = len(ticket_data)
        sheet_updater_logger.info(f"Processing {total_tickets} tickets")
        
        # Counters
        successful_updates = 0
        failed_updates = 0
        no_mr_found = 0
        
        # Process each ticket
        for idx, (row_index, ticket_number) in enumerate(ticket_data):
            try:
                # Update progress
                progress["percentage"] = 10 + int(((idx + 1) / total_tickets) * 85)
                progress["message"] = f"Processing ticket {idx + 1}/{total_tickets}: {ticket_number}"
                
                sheet_updater_logger.info(f"Processing ticket {ticket_number} at row {row_index}")
                
                # Remove any hash or prefix from ticket number
                ticket_id = ticket_number.replace("#", "").strip()
                if not ticket_id.isdigit():
                    sheet_updater_logger.warning(f"Invalid ticket number format: {ticket_number}")
                    failed_updates += 1
                    continue
                
                # Get ticket data from Mantis
                ticket_info = mantis.get_ticket_data(ticket_id)
                
                if not ticket_info:
                    sheet_updater_logger.warning(f"Could not fetch ticket {ticket_id} from Mantis")
                    failed_updates += 1
                    continue
                
                # Extract MR URLs from notes
                notes = ticket_info.get("notes", [])
                mr_urls = extract_merge_request_urls_from_notes(notes)

                # Filter out automation MRs containing 'ns_cypress'
                mr_urls = [url for url in mr_urls if "ns_cypress" not in url]
                
                if not mr_urls:
                    sheet_updater_logger.info(f"No MR found for ticket {ticket_id}")
                    no_mr_found += 1
                    # Update sheet with zeros
                    sheets.update_ticket_status(
                        worksheet,
                        column_indices,
                        row_index,
                        code_reviewed=0,
                        qa_verified=0,
                        ticket_merged=0
                    )
                    # Add delay to respect rate limits (1 second for safer rate limiting)
                    time.sleep(1.0)
                    continue
                
                sheet_updater_logger.info(f"Found {len(mr_urls)} MR(s) for ticket {ticket_id}: {mr_urls}")
                
                # Try to fetch data from all MRs
                mr_data = None
                for mr_url in mr_urls:
                    sheet_updater_logger.info(f"Attempting to fetch MR: {mr_url}")
                    temp_mr_data = gitlab.get_merge_request(mr_url)
                    if temp_mr_data:
                        mr_data = temp_mr_data
                        sheet_updater_logger.info(f"Successfully fetched MR data from: {mr_url}")
                        break
                    else:
                        sheet_updater_logger.warning(f"Could not fetch MR data for {mr_url}")
                
                # If none of the MRs could be fetched, increment failed_updates
                if not mr_data:
                    sheet_updater_logger.error(f"Could not fetch any MR data for ticket {ticket_id}")
                    failed_updates += 1
                    continue
                
                # Check MR tags and merge status
                has_code_reviewed, has_qa_verified, is_merged = check_mr_tags(mr_data)
                
                sheet_updater_logger.info(
                    f"Ticket {ticket_id}: Code Reviewed={has_code_reviewed}, "
                    f"QA Verified={has_qa_verified}, Merged={is_merged}"
                )
                
                # Update sheet
                sheets.update_ticket_status(
                    worksheet,
                    column_indices,
                    row_index,
                    code_reviewed=1 if has_code_reviewed else 0,
                    qa_verified=1 if has_qa_verified else 0,
                    ticket_merged=1 if is_merged else 0
                )
                
                successful_updates += 1
                
                # Add delay to respect rate limits (1 second for safer rate limiting)
                time.sleep(1.0)
                
            except Exception as e:
                sheet_updater_logger.error(f"Error processing ticket {ticket_number}: {e}")
                failed_updates += 1
                continue
        
        # Log summary
        sheet_updater_logger.info(f"Sheet update completed:")
        sheet_updater_logger.info(f"Total tickets processed: {total_tickets}")
        sheet_updater_logger.info(f"Successful updates: {successful_updates}")
        sheet_updater_logger.info(f"Failed updates: {failed_updates}")
        sheet_updater_logger.info(f"Tickets without MR: {no_mr_found}")
        
        progress["status"] = "completed"
        progress["percentage"] = 100
        progress["message"] = (
            f"Completed! Processed: {total_tickets}, "
            f"Success: {successful_updates}, "
            f"Failed: {failed_updates}, "
            f"No MR: {no_mr_found}"
        )
        
    except Exception as e:
        sheet_updater_logger.exception("Error in sheet updater")
        progress["status"] = "error"
        progress["percentage"] = 0
        progress["message"] = f"Error: {str(e)}"
