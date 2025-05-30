from core.logging_config import LoggerSetup
from operations.mantis_operations import MantisOperations
from operations.google_sheets_operations import GoogleSheetsOperations
from operations.utils import *
from core.config_manager import ConfigurationManager
from core.string_constants import StringConstants
import datetime
import time

# Initialize modules
sheets_ops = GoogleSheetsOperations()
config = ConfigurationManager(config_file="configs/code_move.json")
mantis = MantisOperations(StringConstants.REGRESSION)
cm_logger = LoggerSetup.setup_logger("code_move_analytics", "logs/code_move_analytics")
progress = {"status": "idle", "percentage": 0}

def clone_mantis_tickets(ticket_ids, er_date, target_version, target_patch, qa_owner, instructions, title_prefix):
    global progress
    progress["status"] = "running"
    progress["percentage"] = 0

    cm_logger.info(f"Started the cloning process for {len(ticket_ids)} tickets having the title {title_prefix}.")

    try:
        for idx, ticket_id in enumerate(ticket_ids):
            ticket_data = mantis.get_ticket_data(ticket_number=ticket_id)
            valid_custom_field_ids = mantis.get_custom_fields_for_project(config.get("REGRESSION_PROJECT_ID"))

            new_title = f"<b>{title_prefix}</b> {ticket_data['summary']}"
            new_title = new_title[:125] + "..." if len(new_title) > 128 else new_title

            full_instructions = instructions + (
                f"\n\nOriginal Ticket: <b>{ticket_id}</b>"
            )

            new_description = ticket_data['description'] + "\n\n" + full_instructions
            category_name = ticket_data['category']['name']
            handler_id = mantis.get_developer_for_module(category_name)

            date_obj = datetime.datetime.strptime(er_date, "%Y-%m-%d")
            unix_timestamp = int(time.mktime(date_obj.timetuple()))

            new_ticket_data = {
                "summary": new_title,
                "description": new_description,
                "project": {"id": config.get("REGRESSION_PROJECT_ID")},
                "category": ticket_data['category']['name'],
                "view_state": {"id": ticket_data['view_state']['id']},
                "priority": {"id": ticket_data['priority']['id']},
                "severity": {"id": ticket_data['severity']['id']},
                "reproducibility": {"id": ticket_data['reproducibility']['id']},
                "sticky": ticket_data['sticky'],
                "project_version": ticket_data.get('project_version'),
                "handler": {"id": handler_id or ticket_data['handler']['id']} if ticket_data.get('handler') else None,
                "status": {"id": 50},
                "custom_fields": [
                    {"field": {"id": 1}, "value": "Code Move"},
                    {"field": {"id": 2}, "value": target_version},
                    {"field": {"id": 38}, "value": target_patch},
                    {"field": {"id": 6}, "value": qa_owner},
                    {"field": {"id": 41}, "value": "None"},
                    {"field": {"id": 18}, "value": str(unix_timestamp)},
                ] + [
                    {"field": {"id": field['field']['id']}, "value": field['value']}
                    for field in ticket_data.get('custom_fields', [])
                    if field['field']['id'] in valid_custom_field_ids and field['field']['id'] not in [1, 2, 6, 18, 38, 41]
                ],
                "additional_information": ticket_data.get('additional_information'),
                "steps_to_reproduce": ticket_data.get('steps_to_reproduce'),
                "tags": [{"name": tag['name']} for tag in ticket_data.get('tags', [])]
            }

            cloned_ticket_data = mantis.create_ticket(new_ticket_data)
            if cloned_ticket_data:
                cloned_id = cloned_ticket_data['issue']['id']
                mantis.relate_issues(ticket_id, cloned_id)
                mantis.relate_issues(cloned_id, config.get("NEXUS_CONTROL_TICKET"))
                cm_logger.info(f"Ticket with ID {cloned_id} successfully cloned")
                hyperlink_comment = f'=HYPERLINK("{mantis.get_ticket_url(cloned_id)}", "Code Move Ticket: MT#{cloned_id}")'
                sheets_ops.update_comments_in_sheet(ticket_id, hyperlink_comment)
                
            
            else:
                error_msg = f"Failed to create ticket for ID {ticket_id}. Check logs for details."
                cm_logger.debug(error_msg)
                progress["status"] = "error"
                progress["percentage"] = 0
                return {"status": "error", "percentage": 0, "error": error_msg}
            
            progress["percentage"] = int(((idx + 1) / len(ticket_ids)) * 100)

        progress["status"] = "completed"
        progress["percentage"] = 100
        return {"status": "completed", "percentage": 100}

    except Exception as e:
        progress["status"] = f"error: {str(e)}"
        progress["percentage"] = 0
        cm_logger.exception("Error in automation")
        return {"status": progress["status"], "percentage": 0, "error": str(e)}

