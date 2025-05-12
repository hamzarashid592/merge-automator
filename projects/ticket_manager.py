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
        tickets = [285939,405246,410315,412135,415292,415377,415579,415732,416028,416262,416755,416824,416825,417068,417112,417271,417291,417335,417600,417859,418039,418184,419179,419466,419908,419981,420010,420477,420514,420557,420642,420897,420939,421206,421288,421634,421776,422111,422121,422320,422406,423051,423193,423214,423219,423574,423799,423946,423969,424005,424027,424132,424172,424285,424528,424655,424946,424975,425669,425768,426208,426527,426535,426600,426934,427947,428113,428726,429439,429531,429739,430866,431426,434101,435105,435741,436417,436560,436581,436898,437159,437728,438381,438530]


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

        for idx, ticket_id in enumerate(tickets):
            
            
            ticket_data = mantis.get_ticket_data(ticket_id)
            ticket_history = ticket_data.get("history", [])

            if mantis.has_attached_changeset(ticket_history):
                ticket_logger.info(f"Changeset attached for NS70SS01 for ticket {mantis.get_ticket_url(ticket_id)}")
                mantis.update_qa_status_to_accepted(ticket_id)
                mantis.update_status_to_doh(ticket_id)
                mantis.add_note_to_ticket(ticket_id,"Will be released in <b>Nexus E05</b> on the given ERD.")
            else:
                ticket_logger.info(f"No relevant changeset found for ticket {mantis.get_ticket_url(ticket_id)}")



            # mantis.update_status_to_new(ticket_id=ticket_id)

            # mantis.add_note_to_ticket(ticket_number=ticket_id,note_text=f"Relating the ticket to <b>{CONTROL_TICKET_DESC}</b> and removing its link from <b>{OLD_CONTROL_TICKET}</b>.")

            # mantis.relate_issues(ticket_id,CONTROL_TICKET)

            # mantis.unrelate_issues(ticket_id,OLD_CONTROL_TICKET)

            # mantis.update_qa_status_to_assigned(ticket_id=ticket_id)

            # mantis.update_owner(ticket_id=ticket_id,owner_id=StringConstants.SYED_KHURRAM_KAMRAN)

            # ticket_logger.info(f"Updated the details for {mantis.get_ticket_url(ticket_id)}")

            

      
           
    except Exception as e:
        progress["status"] = f"error: {str(e)}"
        progress["percentage"] = 0
        ticket_logger.exception("Error in automation")




