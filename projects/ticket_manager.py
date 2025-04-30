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
        tickets = [285939,413154,423574,408061,390269,412448,411940,415285,417068,420642,414984,412798,409331,402338,403417,421206,426600,417335,407931,418184,420635,420676,421634,417859,408350]


        if not tickets:
            ticket_logger.info('No tickets found for the given filter.')
            progress["status"] = "completed"
            progress["percentage"] = 100
            return

        total_tickets = len(tickets)
        ticket_logger.info(f"Found {total_tickets} tickets to review")

        CONTROL_TICKET= 436818
        CONTROL_TICKET_DESC="MT#0436818: Nexus E5 (Re)Stability Sprint#1 : Retesting Control Ticket"

        for idx, ticket_data in enumerate(tickets):
            
            # ticket_id = ticket_data["id"]

            ticket_id = ticket_data

            # mantis.update_status_to_new(ticket_id=ticket_id)

            # mantis.add_note_to_ticket(ticket_number=ticket_id,note_text=f"Relating the ticket to <b>{CONTROL_TICKET_DESC}</b> and marking the status back to <b>New</b>.")

            # mantis.relate_issues(ticket_id,CONTROL_TICKET)

            # mantis.update_qa_status_to_assigned(ticket_id=ticket_id)

            mantis.update_owner(ticket_id=ticket_id,owner_id=StringConstants.SYED_KHURRAM_KAMRAN)

            ticket_logger.info(f"Updated the details for {mantis.get_ticket_url(ticket_id)}")

            

      
           
    except Exception as e:
        progress["status"] = f"error: {str(e)}"
        progress["percentage"] = 0
        ticket_logger.exception("Error in automation")




