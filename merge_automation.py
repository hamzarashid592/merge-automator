import re
from logging_config import LoggerSetup
from mantis_operations import MantisOperations
from gitlab_operations import GitLabOperations
from google_sheets_operations import GoogleSheetsOperations
from utils import get_target_branch, extract_ticket_id_from_description
from config_manager import ConfigurationManager

# Initialize modules
mantis = MantisOperations()
gitlab = GitLabOperations()
sheets_ops = GoogleSheetsOperations()
# Initialize the configuration manager
config = ConfigurationManager()

# Global variable to track progress
progress = {"status": "idle", "percentage": 0}

def automate_regression_merging():
    try:
        """
        Automates the process of merging regression-related tickets.
        """
        merge_logger = LoggerSetup.setup_logger("merge_analytics", "logs/merge_analytics")
        # Initialize progress
        global progress
        progress["status"] = "running"
        progress["percentage"] = 0

        tickets = mantis.get_tickets_from_filter(config.get("REGRESSION_ISSUES_FILTER_ID"))
        if not tickets:
            merge_logger.info('No tickets found for the given filter.')
            progress["status"] = "completed"
            progress["percentage"] = 100
            return

        total_tickets = len(tickets)
        merge_logger.info(f"Found {total_tickets} tickets to review")

        # Counters to keep track of stats
        pending_for_qa = 0
        pending_for_review = 0
        invalid_target_branches = 0
        successful_merges = 0

        for idx, ticket_data in enumerate(tickets):
            ticket_id = ticket_data["id"]

            # Update progress percentage
            progress["percentage"] = int(((idx + 1) / total_tickets) * 100)

            is_code_move_ticket = False
            original_ticket_id = None
            if mantis.get_record_type(ticket_data) == "Code Move":
                is_code_move_ticket = True
                original_ticket_id = extract_ticket_id_from_description(ticket_data["description"])


            # Checking for code move tickets which have been marked for submitter
            if is_code_move_ticket and original_ticket_id and ticket_data["resolution"]["label"] == "For Submitter":
                # original_ticket_id = extract_ticket_id_from_description(ticket_data["description"])
                mantis.add_note_to_ticket(ticket_id,"Closing this ticket as the <b>code move is not required</b> as per the developer's investigation")
                mantis.update_status_to_fixed(ticket_id)
                mantis.close_ticket(ticket_id)
                hyperlink_formula = f'=HYPERLINK("{mantis.get_ticket_url(ticket_id)}", "Code move not required as per the developer\'s investigation, details in ticket MT#{ticket_id}")'
                sheets_ops.update_comments_and_dev_status_in_sheet(original_ticket_id,hyperlink_formula)
                merge_logger.info(f"For Submitter Code move ticket {ticket_data['id']} has been closed.")
                continue
                
            if ticket_data and ticket_data.get("notes"):
                merge_request_pattern = r"http://gitlab\.sibisoft\.com:7070/.*?/merge_requests/\d+"
                all_mrs_merged = True
                number_of_mrs_in_ticket = 0

                for note in ticket_data["notes"]:
                    note_text = note["text"]
                    matches = re.findall(merge_request_pattern, note_text)  # Extract all MR URLs
                    
                    if matches:
                        for merge_request_url in matches:  # Loop through all extracted MR URLs
                            number_of_mrs_in_ticket = number_of_mrs_in_ticket + 1

                            merge_request_data = gitlab.get_merge_request(merge_request_url)

                            if not merge_request_data:
                                merge_logger.info(f"Unable to fetch MR data for: {merge_request_url}")
                                merge_logger.info(f"Skipping rest of the operations for ticket {ticket_data['id']}")
                                all_mrs_merged = False
                                continue

                            merge_request_status = merge_request_data.get("state")
                            if merge_request_status == "closed":
                                number_of_mrs_in_ticket = number_of_mrs_in_ticket - 1
                                merge_logger.info(f"The MR {merge_request_url} is closed. Going to the next MR.")
                                continue

                            target_branch = get_target_branch(merge_request_url)
                            labels = merge_request_data.get("labels", [])
                            assignee = (merge_request_data.get("assignee") or {}).get("name")
                            author = (merge_request_data.get("author") or {}).get("name")

                            if (target_branch in merge_request_data.get("target_branch", "") and
                                ('QA Verified' in labels or 'QA Accepted' in labels) and
                                ('Code Reviewed' in labels or 'Reviewed' in labels)):

                                mantis.detach_tags_from_ticket(ticket_id, [config.get("TAG_CODE_REVIEW_AWAITED")])

                                if merge_request_status == "opened":
                                    merge_status = gitlab.merge_merge_request(merge_request_url)
                                    if merge_status:
                                        if is_code_move_ticket and original_ticket_id:
                                            merge_logger.info(f"Merge request {merge_request_url} successfully merged. Code Move Ticket ID: {mantis.get_ticket_url(original_ticket_id)}")
                                            mantis.add_note_to_ticket(ticket_id, f"The code move MR <b>{merge_request_url}</b> has been merged into <b>{target_branch}</b>.")
                                        else:    
                                            merge_logger.info(f"Merge request {merge_request_url} successfully merged. Ticket ID: {mantis.get_ticket_url(ticket_id)}")
                                            mantis.add_note_to_ticket(ticket_id, f"The MR <b>{merge_request_url}</b> has been merged into <b>{target_branch}</b>.")
                                        successful_merges = successful_merges + 1
                                    else:
                                        merge_logger.info(f"Unable to merge MR: {merge_request_url} despite trying")
                                        merge_logger.info(f"Skipping rest of the operations for ticket {ticket_id}")
                                        all_mrs_merged = False
                                        continue
                                elif merge_request_status == "merged":
                                    merge_logger.info(f"The MR {merge_request_url} is already merged, Ticket: {mantis.get_ticket_url(ticket_id)}")

                            else:
                                if merge_request_status == "opened": # Printing the error logs only for open MRs
                                    error_message = "Labels not valid for merging"
                                    if target_branch not in merge_request_data.get("target_branch", ""):
                                        error_message = f"Invalid target branch in the MR, it should be {target_branch}, Author: {author}"
                                        invalid_target_branches = invalid_target_branches + 1
                                    elif 'QA Verified' not in labels:
                                        error_message = "QA Verified label missing in the MR, skipping it"
                                        pending_for_qa = pending_for_qa + 1
                                    elif 'Code Reviewed' not in labels and 'Reviewed' not in labels:
                                        error_message = "Code Review pending at " + (assignee if assignee is not None else "Unknown")
                                        mantis.add_tags_to_ticket(ticket_id, [config.get("TAG_CODE_REVIEW_AWAITED")])
                                        pending_for_review = pending_for_review + 1
                                    merge_logger.info(f"{error_message} for: {merge_request_url}")

                                all_mrs_merged = False

                if all_mrs_merged and number_of_mrs_in_ticket > 0:
                    mantis.update_status_to_fixed(ticket_id)
                    if is_code_move_ticket and original_ticket_id:
                        hyperlink_formula = f'=HYPERLINK("{mantis.get_ticket_url(ticket_id)}", "Code move done in ticket MT#{ticket_id}")'
                        sheets_ops.update_comments_and_dev_status_in_sheet(original_ticket_id,hyperlink_formula)
                        # sheets_ops.update_dev_status_in_sheet(original_ticket_id)
            else:
                merge_logger.info(f'No notes found for ticket: {ticket_id}')
        
        # Log stats
        merge_logger.info(f"Total Number of Tickets Processed: {total_tickets}")
        merge_logger.info(f"Number of MR's in the QA Verification Queue: {pending_for_qa}")
        merge_logger.info(f"Number of MR's in the Code Review Queue: {pending_for_review}")
        merge_logger.info(f"Number of MR's with Wrong Target Branches: {invalid_target_branches}")
        merge_logger.info(f"Number of MR's Successfully Merged: {successful_merges}")

        # Mark progress as completed
        progress["status"] = "completed"
        progress["percentage"] = 100

    except Exception as e:
        progress["status"] = f"error: {str(e)}"
        progress["percentage"] = 0
        merge_logger.exception("Error in automation")



if __name__ == "__main__":
    automate_regression_merging()

