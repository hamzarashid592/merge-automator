from core.logging_config import LoggerSetup
from operations.mantis_operations import MantisOperations
from operations.gitlab_operations import GitLabOperations
from operations.google_sheets_operations import GoogleSheetsOperations
from operations.utils import *
from core.config_manager import ConfigurationManager
from core.string_constants import StringConstants

# Initialize modules
sheets_ops = GoogleSheetsOperations()
# Initialize the configuration manager
config = ConfigurationManager(config_file="configs/reg_merge.json")

# Global variable to track progress
progress = {"status": "idle", "percentage": 0}

def modify_tickets():
    try:
        """
        Automates the process of merging regression-related tickets.
        """
        mantis = MantisOperations(StringConstants.REGRESSION)
        ticket_logger = LoggerSetup.setup_logger("ticket_manager_analytics", "logs/ticket_manager_analytics")
        # Initialize progress
        global progress
        progress["status"] = "running"
        progress["percentage"] = 0

        # tickets = mantis.get_tickets_from_filter(config.get("GENERAL_ISSUES_FILTER_ID"))
        tickets = [438785,438382,438624,438415,438674,438672,438191,437510,438617,438615,438399,438422,438403,438380,438376,438295,438277,438276,437495,438219,437819,437307,437486,437138,437111,438100]


        if not tickets:
            ticket_logger.info('No tickets found for the given filter.')
            progress["status"] = "completed"
            progress["percentage"] = 100
            return

        total_tickets = len(tickets)
        ticket_logger.info(f"Found {total_tickets} tickets to review")

        CONTROL_TICKET= 438810
        CONTROL_TICKET_DESC="MT#0438810: Nexus E5 (Re)Stability Sprint#2 : Retesting Control Ticket"
        OLD_CONTROL_TICKET = 436818

        for idx, ticket_data in enumerate(tickets):
            
            # ticket_id = ticket_data["id"]

            ticket_id = ticket_data

            # mantis.update_status_to_new(ticket_id=ticket_id)

            mantis.add_note_to_ticket(ticket_number=ticket_id,note_text=f"Relating the ticket to <b>{CONTROL_TICKET_DESC}</b> and removing its link from <b>{OLD_CONTROL_TICKET}</b>.")

            mantis.relate_issues(ticket_id,CONTROL_TICKET)

            mantis.unrelate_issues(ticket_id,OLD_CONTROL_TICKET)

            # mantis.update_qa_status_to_assigned(ticket_id=ticket_id)

            # mantis.update_owner(ticket_id=ticket_id,owner_id=StringConstants.SYED_KHURRAM_KAMRAN)

            ticket_logger.info(f"Updated the details for {mantis.get_ticket_url(ticket_id)}")

            

      
           
    except Exception as e:
        progress["status"] = f"error: {str(e)}"
        progress["percentage"] = 0
        ticket_logger.exception("Error in automation")




