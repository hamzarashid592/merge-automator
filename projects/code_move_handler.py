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

    try:
        for idx, ticket_id in enumerate(ticket_ids):
            ticket_data = mantis.get_ticket_data(ticket_number=ticket_id)
            valid_custom_field_ids = mantis.get_custom_fields_for_project(config.get("REGRESSION_PROJECT_ID"))

            original_issue = ticket_data['issues'][0]
            new_title = f"<b>{title_prefix}</b> {original_issue['summary']}"
            new_title = new_title[:125] + "..." if len(new_title) > 128 else new_title

            full_instructions = instructions + (
                f"\n\nOriginal Ticket: <b>{ticket_id}</b>"
            )

            cm_logger.info("Started the cloning")

            new_description = original_issue['description'] + "\n\n" + full_instructions
            category_name = original_issue['category']['name']
            handler_id = mantis.get_developer_for_module(category_name)

            date_obj = datetime.datetime.strptime(er_date, "%Y-%m-%d")
            unix_timestamp = int(time.mktime(date_obj.timetuple()))

            new_ticket_data = {
                "summary": new_title,
                "description": new_description,
                "project": {"id": config.get("REGRESSION_PROJECT_ID")},
                "category": original_issue['category']['name'],
                "view_state": {"id": original_issue['view_state']['id']},
                "priority": {"id": original_issue['priority']['id']},
                "severity": {"id": original_issue['severity']['id']},
                "reproducibility": {"id": original_issue['reproducibility']['id']},
                "sticky": original_issue['sticky'],
                "project_version": original_issue.get('project_version'),
                "handler": {"id": handler_id or original_issue['handler']['id']} if original_issue.get('handler') else None,
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
                    for field in original_issue.get('custom_fields', [])
                    if field['field']['id'] in valid_custom_field_ids and field['field']['id'] not in [1, 2, 6, 18, 38, 41]
                ],
                "additional_information": original_issue.get('additional_information'),
                "steps_to_reproduce": original_issue.get('steps_to_reproduce'),
                "tags": [{"name": tag['name']} for tag in original_issue.get('tags', [])]
            }

            cloned_ticket_data = mantis.create_ticket(new_ticket_data)
            if cloned_ticket_data:
                cloned_id = cloned_ticket_data['issue']['id']
                # mantis.relate_issues(ticket_id, cloned_id)
                # mantis.relate_issues(cloned_id, config.get("NEXUS_CONTROL_TICKET"))
                cm_logger.info(f"Ticket with ID {cloned_id} successfully cloned")
                hyperlink_comment = f'=HYPERLINK("{mantis.get_ticket_url(cloned_id)}", "Code Move Ticket: MT#{cloned_id}")'
                sheets_ops.update_comments_in_sheet(ticket_id, hyperlink_comment)
                
                # Debugging
                mantis.add_note_to_ticket(cloned_id,"Ticket filed for testing purposes, please ignore")
                mantis.close_ticket(ticket_number=cloned_id)
            
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

