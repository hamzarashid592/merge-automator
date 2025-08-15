from .base_merger import BaseMerger
from operations.utils import *
from core.string_constants import StringConstants

class RegressionMerger(BaseMerger):
    def __init__(self):
        super().__init__(StringConstants.REGRESSION, f"configs/{StringConstants.REGRESSION}.json", f"{StringConstants.REGRESSION}")

    def run(self):
        try:
            """
            Automates the process of merging regression-related tickets.
            """
            self.progress["status"] = "running"
            self.progress["percentage"] = 0

            tickets = self.mantis.get_tickets_from_filter(self.config.get("REGRESSION_ISSUES_FILTER_ID"))
            if not tickets:
                self.logger.info('No tickets found for the given filter.')
                self.progress["status"] = "completed"
                self.progress["percentage"] = 100
                return
            
            total_tickets = len(tickets)
            self.logger.info(f"Found {total_tickets} tickets to review")

            # Counters to keep track of stats
            pending_for_qa = 0
            pending_for_review = 0
            invalid_target_branches = 0
            successful_merges = 0

            for idx, ticket_data in enumerate(tickets):
                ticket_id = ticket_data["id"]
                self.logger.info(f"Ticket to process: {self.mantis.get_ticket_url(ticket_number=ticket_id)}")

                # Update self.progress percentage
                self.progress["percentage"] = int(((idx + 1) / total_tickets) * 100)

                is_code_move_ticket = False
                original_ticket_id = None
                if self.mantis.get_record_type(ticket_data) == "Code Move":
                    is_code_move_ticket = True
                    original_ticket_id = extract_ticket_id_from_description(ticket_data["description"])


                # Checking for code move tickets which have been marked for submitter
                if is_code_move_ticket and original_ticket_id and ticket_data["resolution"]["label"] == "For Submitter":
                    # original_ticket_id = extract_ticket_id_from_description(ticket_data["description"])
                    self.mantis.add_note_to_ticket(ticket_id,"Closing this ticket as the <b>code move is not required</b> as per the developer's investigation")
                    self.mantis.update_status_to_fixed(ticket_id)
                    self.mantis.close_ticket(ticket_id)
                    hyperlink_formula = f'=HYPERLINK("{self.mantis.get_ticket_url(ticket_id)}", "Code move not required as per the developer\'s investigation, details in ticket MT#{ticket_id}")'
                    self.sheets.update_comments_and_dev_status_in_sheet(original_ticket_id,hyperlink_formula)
                    self.logger.info(f"For Submitter Code move ticket {ticket_data['id']} has been closed.")
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

                                merge_request_data = self.gitlab.get_merge_request(merge_request_url)

                                if not merge_request_data:
                                    self.logger.info(f"Unable to fetch MR data for: {merge_request_url}")
                                    self.logger.info(f"Skipping rest of the operations for ticket {ticket_data['id']}")
                                    all_mrs_merged = False
                                    continue

                                merge_request_status = merge_request_data.get("state")
                                if merge_request_status == "closed":
                                    number_of_mrs_in_ticket = number_of_mrs_in_ticket - 1
                                    self.logger.info(f"The MR {merge_request_url} is closed. Going to the next MR.")
                                    continue

                                target_branch = get_target_branch(merge_request_url, StringConstants.REGRESSION)
                                labels = merge_request_data.get("labels", [])
                                assignee = (merge_request_data.get("assignee") or {}).get("name")
                                author = (merge_request_data.get("author") or {}).get("name")

                                branch_matches = (target_branch == merge_request_data.get("target_branch", ""))
                                code_move_ready = is_code_move_ticket and (("Unit Tested" in labels) or ("QA Verified" in labels))
                                qa_ready = (not is_code_move_ticket) and \
                                        any(label in labels for label in ("QA Verified", "QA Accepted")) and \
                                        any(label in labels for label in ("Code Reviewed", "Reviewed"))

                                if branch_matches and (code_move_ready or qa_ready):
                                    self.mantis.detach_tags_from_ticket(ticket_id, [self.config.get("TAG_CODE_REVIEW_AWAITED")])

                                    if merge_request_status == "opened":
                                        merge_status = self.gitlab.merge_merge_request(merge_request_url)
                                        if merge_status:
                                            if is_code_move_ticket and original_ticket_id:
                                                self.logger.info(f"Merge request {merge_request_url} successfully merged. Code Move Ticket ID: {self.mantis.get_ticket_url(original_ticket_id)}")
                                                self.mantis.add_note_to_ticket(ticket_id, f"The code move MR <b>{merge_request_url}</b> has been merged into <b>{target_branch}</b>.")
                                            else:    
                                                self.logger.info(f"Merge request {merge_request_url} successfully merged. Ticket ID: {self.mantis.get_ticket_url(ticket_id)}")
                                                self.mantis.add_note_to_ticket(ticket_id, f"The MR <b>{merge_request_url}</b> has been merged into <b>{target_branch}</b>.")
                                            successful_merges = successful_merges + 1
                                        else:
                                            self.logger.info(f"Unable to merge MR: {merge_request_url} despite trying")
                                            self.logger.info(f"Skipping rest of the operations for ticket {ticket_id}")
                                            all_mrs_merged = False
                                            continue
                                    elif merge_request_status == "merged":
                                        self.logger.info(f"The MR {merge_request_url} is already merged, Ticket: {self.mantis.get_ticket_url(ticket_id)}")

                                else:
                                    if merge_request_status == "opened": # Printing the error logs only for open MRs
                                        error_message = "Labels not valid for merging"
                                        if not branch_matches:
                                            error_message = f"Invalid target branch in the MR, it should be {target_branch}, Author: {author}"
                                            invalid_target_branches = invalid_target_branches + 1
                                        elif is_code_move_ticket and ("Unit Tested" not in labels):
                                            error_message = "Code move not unit tested"                                        
                                            # self.mantis.update_status_to_new(ticket_id=ticket_id)
                                        elif not qa_ready:
                                            if 'QA Verified' not in labels:
                                                error_message = "QA Verified label missing in the MR, skipping it"
                                                pending_for_qa = pending_for_qa + 1
                                            elif 'Code Reviewed' not in labels and 'Reviewed' not in labels:
                                                error_message = "Code Review pending at " + (assignee if assignee is not None else "Unknown")
                                                self.mantis.add_tags_to_ticket(ticket_id, [self.config.get("TAG_CODE_REVIEW_AWAITED")])
                                                pending_for_review = pending_for_review + 1
                                        self.logger.info(f"{error_message} for: {merge_request_url}")

                                    all_mrs_merged = False

                    if all_mrs_merged and number_of_mrs_in_ticket > 0:
                        self.mantis.update_status_to_fixed(ticket_id)
                        if is_code_move_ticket and original_ticket_id:
                            hyperlink_formula = f'=HYPERLINK("{self.mantis.get_ticket_url(ticket_id)}", "Code move done in ticket MT#{ticket_id}")'
                            self.sheets.update_comments_and_dev_status_in_sheet(original_ticket_id,hyperlink_formula)
                else:
                    self.logger.info(f'No notes found for ticket: {ticket_id}')
            
            # Log stats
            self.logger.info(f"Total Number of Tickets Processed: {total_tickets}")
            self.logger.info(f"Number of MR's in the QA Verification Queue: {pending_for_qa}")
            self.logger.info(f"Number of MR's in the Code Review Queue: {pending_for_review}")
            self.logger.info(f"Number of MR's with Wrong Target Branches: {invalid_target_branches}")
            self.logger.info(f"Number of MR's Successfully Merged: {successful_merges}")

            # Posting the stats to Google Chat
            if self.chat_notifier:
                self.chat_notifier.send_summary()

            # Mark self.progress as completed
            self.progress["status"] = "completed"
            self.progress["percentage"] = 100

        except Exception as e:
            self.progress["status"] = f"error: {str(e)}"
            self.progress["percentage"] = 0
            self.logger.exception("Error in automation")