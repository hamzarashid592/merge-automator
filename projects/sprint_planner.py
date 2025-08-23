from core.logging_config import LoggerSetup
from operations.mantis_operations import MantisOperations
from operations.google_sheets_operations import GoogleSheetsOperations
from operations.utils import *
from core.string_constants import StringConstants
from openpyxl import load_workbook

# Initialize modules
sheets_ops = GoogleSheetsOperations()

# Global variable to track progress
progress = {"status": "idle", "percentage": 0}

def plan_sprint():
    try:
        """
        Automates the process of merging regression-related tickets.
        """
        mantis = MantisOperations(StringConstants.REGRESSION)
        ticket_logger = LoggerSetup.setup_logger("sprint_planner", "logs/sprint_planner")

        # tickets = mantis.get_tickets_from_filter(config.get("GENERAL_ISSUES_FILTER_ID"))
        tickets = [443644,439272,433440,438490,428773,429822,440735,437170,447214,443680,442824,440573,440037,444535,447385,437613,442490,442023,437604,433497,431220,430046,413891,370564,440242,424089,443895,442794,433719,442531,442098,444971,444091,442482,442428,440367,435060,425471,451011,440489,440481,444235,441708,439674,439475,425865,411198,441083,445353,441930,441194,440616,438275,433545,445097,443641,442966,435496,441377,438621,436838,433625,432135,431898,421161,434804]


        if not tickets:
            ticket_logger.info('No tickets found for the given filter.')
            return

        total_tickets = len(tickets)
        ticket_logger.info(f"Found {total_tickets} tickets to review")

        # The work concering excel.
        file_path = r"D:\NS Repo\Prod_Ticket.xlsx"
        workbook = load_workbook(file_path)
        sheet = workbook["Sheet1"]

        for idx, ticket_id in enumerate(tickets):
            
            
            ticket_data = mantis.get_ticket_data(ticket_id)

            sheet[f"A{idx+2}"] = f"=HYPERLINK(\"https://mantis.sibisoft.com/view.php?id={ticket_data.get("id")}\",\"{ticket_data.get("id")}\")"
            sheet[f"B{idx+2}"] = f"{ticket_data.get("category")["name"]}"
            sheet[f"C{idx+2}"] = f"MT#0{ticket_data.get("id")}: {ticket_data.get("summary")}"
            sheet[f"D{idx+2}"] = f"{mantis.get_custom_field(ticket_data,"Efforts Dev").replace('\'','')}"
            sheet[f"E{idx+2}"] = f"{ticket_data.get("handler")["real_name"]}"
            sheet[f"F{idx+2}"] = f"{ticket_data.get("resolution")["name"]}"

        workbook.save(file_path)
      
           
    except Exception as e:
        progress["status"] = f"error: {str(e)}"
        progress["percentage"] = 0
        ticket_logger.exception("Error in automation")

