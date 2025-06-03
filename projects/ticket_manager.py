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
        tickets = [441297,440484,423103,441150,435163,439855,440160,440813,440811,434687,438191,439753,439087,438376,439604,439319,437510,437495,437111,437138,437486,437307,438219,438276,438277,438403,438422,438615]


        if not tickets:
            ticket_logger.info('No tickets found for the given filter.')
            progress["status"] = "completed"
            progress["percentage"] = 100
            return

        total_tickets = len(tickets)
        ticket_logger.info(f"Found {total_tickets} tickets to review")

        CONTROL_TICKET= 434669
        CONTROL_TICKET_DESC="MT#0434669: Nexus E6-B: Regression Testing Control Ticket"
        OLD_CONTROL_TICKET = 438810

        for idx, ticket_id in enumerate(tickets):
            
            
            # ticket_data = mantis.get_ticket_data(ticket_id)
            
            # ticket_history = ticket_data.get("history", [])
            # if mantis.has_attached_changeset(ticket_history):
            #     ticket_logger.info(f"Changeset attached for NS70SS01 for ticket {mantis.get_ticket_url(ticket_id)}")
            #     mantis.update_qa_status_to_accepted(ticket_id)
            #     mantis.update_status_to_doh(ticket_id)
            #     mantis.add_note_to_ticket(ticket_id,"Will be released in <b>Nexus E05</b> on the given ERD.")
            # else:
            #     ticket_logger.info(f"No relevant changeset found for ticket {mantis.get_ticket_url(ticket_id)}")
            # if mantis.has_status_changed(ticket_data,StringConstants.MANTIS_RESOLUTION_PARTIALLY_FIXED, 
            #                              StringConstants.MANTIS_RESOLUTION_DOH, "hamzarashid"):
            #     ticket_logger.info(f"Changed from partially fixed to DOH --> {mantis.get_ticket_url(ticket_id)}")



            # mantis.update_status_to_new(ticket_id=ticket_id)

            mantis.add_note_to_ticket(ticket_number=ticket_id,note_text=f"Relating the ticket to <b>{CONTROL_TICKET_DESC}</b> and removing its link from <b>{OLD_CONTROL_TICKET}</b>.")

            mantis.relate_issues(ticket_id,CONTROL_TICKET)

            mantis.unrelate_issues(ticket_id,OLD_CONTROL_TICKET)

            # mantis.update_status_to_new(ticket_id=ticket_id)

            # mantis.update_qa_status_to_assigned(ticket_id=ticket_id)

            # mantis.update_owner(ticket_id=ticket_id,owner_id=StringConstants.SYED_KHURRAM_KAMRAN)

            ticket_logger.info(f"Updated the details for {mantis.get_ticket_url(ticket_id)}")

            

      
           
    except Exception as e:
        progress["status"] = f"error: {str(e)}"
        progress["percentage"] = 0
        ticket_logger.exception("Error in automation")




