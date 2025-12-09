import requests
from core.logging_config import LoggerSetup
from encryption.token_manager import TokenManager
from core.config_manager import ConfigurationManager
from core.string_constants import StringConstants
import json

mantis_logger = LoggerSetup.setup_logger("mantis", "logs/mantis")

class MantisOperations:
    
    def __init__(self, project):
        """
        Initialize MantisOperations with the Mantis API base URL and authentication token.
        """
        # Initialize the configuration manager based on the project
        config = ConfigurationManager(config_file=f"configs/{project}.json")
        
        self.mantis_path = config.get("MANTIS_PATH")
        token_manager = TokenManager(key_file=config.get("KEY_FILE"), token_file=f"credentials/{StringConstants.TOKEN_PREFIX}{project}.txt")
        tokens = token_manager.get_tokens()
        self.auth_token = tokens["mantis_token"]

        self.headers = {
            'Authorization': self.auth_token,
            'Content-Type': 'application/json'
        }

    def get_ticket_data(self, ticket_number):
        """
        Fetch ticket data by ticket number.
        """
        ticket_url = f"{self.mantis_path}/api/rest/issues/{ticket_number}"
        response = requests.get(ticket_url, headers=self.headers, verify=False)
        if response.status_code == 200:
            return response.json()['issues'][0]
        else:
            mantis_logger.error(f'Error fetching ticket: {response.text}')
            return None

    def get_ticket_url(self, ticket_number):
        ticket_url = f"{self.mantis_path}/view.php?id={ticket_number}"
        return ticket_url

    def add_note_to_ticket(self, ticket_number, note_text):
        """
        Add a note to a specific ticket.
        """
        note_url = f"{self.mantis_path}/api/rest/issues/{ticket_number}/notes"
        payload = {"text": note_text}
        response = requests.post(note_url, headers=self.headers, json=payload, verify=False)
        if response.status_code != 201:
            mantis_logger.error(f'Error while adding note to ticket {ticket_number}: {response.text}')

    def close_ticket(self, ticket_number):
        """
        Close a specific ticket.
        """
        close_ticket_url = f"{self.mantis_path}/api/rest/issues/{ticket_number}"
        payload = {"status": {"name": "closed"}}
        response = requests.patch(close_ticket_url, headers=self.headers, json=payload, verify=False)
        if response.status_code != 200:
            mantis_logger.error(f'Error while closing ticket {ticket_number}: {response.text}')

    def get_tickets_from_filter(self, filter_ids):
        """
        Get ticket data from one or more Mantis filters.

        Parameters:
            filter_ids (int or list[int]): A single filter ID or a list of filter IDs.

        Returns:
            list: Combined list of ticket data from all provided filters.
        """

        # Handle comma-separated strings
        if isinstance(filter_ids, str):
            filter_ids = [int(fid.strip()) for fid in filter_ids.split(",") if fid.strip().isdigit()]

        if isinstance(filter_ids, int):
            filter_ids = [filter_ids]  # Convert single ID to list

        all_tickets = []

        for filter_id in filter_ids:
            tickets = []
            page = 1
            limit = 50

            while True:
                filter_url = f"{self.mantis_path}/api/rest/issues?filter_id={filter_id}&page={page}&limit={limit}"
                try:
                    response = requests.get(filter_url, headers=self.headers, verify=False)
                    if response.status_code != 200:
                        mantis_logger.error(f"[Filter {filter_id}] Error fetching tickets: {response.text}")
                        break

                    ticket_data = response.json()
                    issues = ticket_data.get("issues", [])
                    tickets.extend(issues)

                    if len(issues) < limit:
                        break
                    page += 1

                except Exception as e:
                    mantis_logger.error(f"[Filter {filter_id}] Exception while fetching tickets: {e}")
                    break

            all_tickets.extend(tickets)

        return all_tickets


    def update_status_to_fixed(self, ticket_id):
        """
        Update ticket status to 'Fixed'.
        """
        update_url = f"{self.mantis_path}/api/rest/issues/{ticket_id}"
        payload = {"resolution": {"name": "Fixed"}}
        response = requests.patch(update_url, headers=self.headers, json=payload, verify=False)
        if response.status_code != 200:
            mantis_logger.error(f'Failed to update status for Ticket ID {ticket_id}: {response.text}')

    def update_owner(self, ticket_id,owner_id):
        """
        Changing the ticket owner.
        """
        update_url = f"{self.mantis_path}/api/rest/issues/{ticket_id}"
        payload = {"handler": {"id": owner_id}}
        response = requests.patch(update_url, headers=self.headers, json=payload, verify=False)
        if response.status_code != 200:
            mantis_logger.error(f'Failed to update owner for Ticket ID {ticket_id}: {response.text}')

    def update_status_to_new(self, ticket_id):
        """
        Update ticket status to 'New'.
        """
        update_url = f"{self.mantis_path}/api/rest/issues/{ticket_id}"
        payload = {"resolution": {"name": "New"}}
        response = requests.patch(update_url, headers=self.headers, json=payload, verify=False)
        if response.status_code != 200:
            mantis_logger.error(f'Failed to update status for Ticket ID {ticket_id}: {response.text}')

    def update_status_to_doh(self, ticket_id):
        """
        Update ticket status to 'Deployable on Hold'.
        """
        update_url = f"{self.mantis_path}/api/rest/issues/{ticket_id}"
        payload = {"resolution": {"name": "Deployable on Hold"}}
        response = requests.patch(update_url, headers=self.headers, json=payload, verify=False)
        if response.status_code != 200:
            mantis_logger.error(f'Failed to update status for Ticket ID {ticket_id}: {response.text}')

    def update_status_to_for_qa(self, ticket_id):
        """
        Update ticket status to 'For QA'.
        """
        update_url = f"{self.mantis_path}/api/rest/issues/{ticket_id}"
        payload = {"resolution": {"name": "For QA"}}
        response = requests.patch(update_url, headers=self.headers, json=payload, verify=False)
        if response.status_code != 200:
            mantis_logger.error(f'Failed to update status for Ticket ID {ticket_id}: {response.text}')

    def update_qa_status_to_assigned(self, ticket_id):
        """
        Update ticket status to 'assigned'.
        """
        update_url = f"{self.mantis_path}/api/rest/issues/{ticket_id}"
        payload = {"status": {"name": "assigned"}}
        response = requests.patch(update_url, headers=self.headers, json=payload, verify=False)
        if response.status_code != 200:
            mantis_logger.error(f'Failed to update QA status for Ticket ID {ticket_id}: {response.text}')

    def update_qa_status_to_accepted(self, ticket_id):
        """
        Update ticket status to 'QA Accepted'.
        """
        update_url = f"{self.mantis_path}/api/rest/issues/{ticket_id}"
        payload = {"status": {"name": "confirmed"}}
        response = requests.patch(update_url, headers=self.headers, json=payload, verify=False)
        if response.status_code != 200:
            mantis_logger.error(f'Failed to update QA status for Ticket ID {ticket_id}: {response.text}')

    def update_title(self, ticket_id, new_title):
        """
        Update ticket title/summary.
        """
        update_url = f"{self.mantis_path}/api/rest/issues/{ticket_id}"
        payload = {"summary": new_title}
        response = requests.patch(update_url, headers=self.headers, json=payload, verify=False)
        if response.status_code != 200:
            mantis_logger.error(f'Failed to update title for Ticket ID {ticket_id}: {response.text}')

    def update_description(self, ticket_id, new_description):
        """
        Update ticket description.
        """
        update_url = f"{self.mantis_path}/api/rest/issues/{ticket_id}"
        payload = {"description": new_description}
        response = requests.patch(update_url, headers=self.headers, json=payload, verify=False)
        if response.status_code != 200:
            mantis_logger.error(f'Failed to update description for Ticket ID {ticket_id}: {response.text}')

    def add_tags_to_ticket(self, ticket_number, tag_ids):
        """
        Add tags to a specific ticket.
        """
        tags_url = f"{self.mantis_path}/api/rest/issues/{ticket_number}/tags"
        payload = {"tags": [{"id": tag_id} for tag_id in tag_ids]}
        response = requests.post(tags_url, headers=self.headers, json=payload, verify=False)
        if response.status_code != 201:
            mantis_logger.error(f'Error while adding tags to ticket {ticket_number}: {response.text}')
            return False
        return True

    def detach_tags_from_ticket(self, ticket_number, tag_ids):
        """
        Detach tags from a specific ticket.
        """
        success = True
        for tag_id in tag_ids:
            tag_url = f"{self.mantis_path}/api/rest/issues/{ticket_number}/tags/{tag_id}"
            response = requests.delete(tag_url, headers=self.headers, verify=False)
            if response.status_code != 200:
                mantis_logger.error(f"Error while detaching tag ID {tag_id} from ticket {ticket_number}: {response.text}")
                success = False
        return success


    def get_custom_field(self, issue, field_name):
        """
        Retrieve the value of a custom field from a Mantis issue.

        Parameters:
            issue (dict): The Mantis issue data (expected to include custom fields).
            field_name (str): The name of the custom field to retrieve.

        Returns:
            str: The value of the custom field, or an empty string if not found or an error occurs.
        """
        try:
            # Check if the issue has custom fields
            if 'custom_fields' in issue:
                for custom_field in issue['custom_fields']:
                    if custom_field.get('field', {}).get('name') == field_name:
                        return custom_field.get('value', "")
        except Exception as e:
            mantis_logger.error(f"Error while getting custom field {field_name} from ticket {issue["id"]}")
        return ""

    def get_custom_fields_for_project(self, project_id):
        """
        Fetch valid custom field IDs for a specific Mantis project.
        Cleans up garbage HTML after valid JSON in the response.
        """
        url = f"{self.mantis_path}/api/rest/projects/{project_id}/custom_fields"
        try:
            response = requests.get(url, headers=self.headers, verify=False)
            if response.status_code != 200:
                mantis_logger.error(f"Error fetching custom fields: {response.text}")
                return []

            # Clean up HTML/PHP warnings by truncating to last valid JSON bracket
            text = response.text
            json_text = text[:text.rfind("}") + 1]

            try:
                project_data = json.loads(json_text)
                return [field['id'] for field in project_data['projects'][0].get('custom_fields', [])]
            except json.JSONDecodeError as je:
                mantis_logger.error(f"JSON decode error after cleanup: {je}")
                return []

        except Exception as e:
            mantis_logger.error(f"Exception in get_custom_fields_for_project: {e}")
            return []

        
    def relate_issues(self, original_issue_id, related_issue_id):
        """
        Relate two issues using the 'related-to' relationship type.
        """
        url = f"{self.mantis_path}/api/rest/issues/{original_issue_id}/relationships"
        payload = {
            "issue": {"id": related_issue_id},
            "type": {"name": "related-to"}
        }
        try:
            response = requests.post(url, headers=self.headers, json=payload, verify=False)
            if response.status_code != 201:
                mantis_logger.error(f"Failed to relate issues {original_issue_id} -> {related_issue_id}: {response.text}")
        except Exception as e:
            mantis_logger.error(f"Exception while relating issues {original_issue_id} -> {related_issue_id}: {e}")

    
    def unrelate_issues(self, original_issue_id, related_issue_id):
        """
        Remove the relationship between two issues.
        """
        try:
            # First, get all relationships for the original issue
            issue_data = self.get_ticket_data(ticket_number=original_issue_id)
            relationships = issue_data.get("relationships", [])

            # Find the relationship to the related_issue_id
            relationship_id = None
            for relation in relationships:
                if relation.get("issue").get("id") == related_issue_id:
                    relationship_id = relation.get("id")
                    break

            if not relationship_id:
                mantis_logger.info(f"No relationship found between {original_issue_id} and {related_issue_id}.")
                return

            # Now delete the relationship
            delete_url = f"{self.mantis_path}/api/rest/issues/{original_issue_id}/relationships/{relationship_id}"
            delete_response = requests.delete(delete_url, headers=self.headers, verify=False)
            if delete_response.status_code != 200:
                mantis_logger.error(f"Failed to delete relationship {relationship_id}: {delete_response.text}")
            else:
                mantis_logger.info(f"Successfully removed relationship between {original_issue_id} and {related_issue_id}")

        except Exception as e:
            mantis_logger.error(f"Exception while unrelating issues {original_issue_id} -> {related_issue_id}: {e}")

    def delete_all_relationships(self, ticket_id):
        """
        Delete all relationships from the specified ticket.
        """
        try:
            # Fetch ticket data including relationships
            issue_data = self.get_ticket_data(ticket_number=ticket_id)
            relationships = issue_data.get("relationships", [])

            if not relationships:
                mantis_logger.info(f"No relationships found for ticket {ticket_id}.")
                return

            for relation in relationships:
                related_issue_id = relation.get("issue", {}).get("id")
                relationship_id = relation.get("id")

                if not relationship_id or not related_issue_id:
                    mantis_logger.warning(f"Invalid relationship structure found in ticket {ticket_id}. Skipping...")
                    continue

                # Build the DELETE URL
                delete_url = f"{self.mantis_path}/api/rest/issues/{ticket_id}/relationships/{relationship_id}"
                delete_response = requests.delete(delete_url, headers=self.headers, verify=False)

                if delete_response.status_code == 200:
                    mantis_logger.info(f"Removed relationship {relationship_id} (related to issue {related_issue_id}) from ticket {ticket_id}.")
                else:
                    mantis_logger.error(f"Failed to delete relationship {relationship_id} from ticket {ticket_id}: {delete_response.text}")

        except Exception as e:
            mantis_logger.error(f"Exception while deleting all relationships from ticket {ticket_id}: {e}")



    def has_attached_changeset(self,ticket_history):
        """
        Checks whether a ticket has a changeset attached to any of the target branches.

        Parameters:
            ticket_history (list): The 'history' field from a Mantis ticket JSON response.

        Returns:
            bool: True if changeset for a known target branch is attached, False otherwise.
        """
        target_branches = {"NS70SS01-BO", "NS70SS01-C3", "NS70SS01-C4", "NS70SS01-APP"}

        for entry in ticket_history:
            field = entry.get("field", {}).get("name", "")
            message = entry.get("message", "")
            new_value = entry.get("new_value", "")

            if field == "Source_changeset_attached" and message == "Changeset attached":
                # Check if any known target branch is in the new_value
                if any(branch in new_value for branch in target_branches):
                    return True

        return False

    def has_status_changed(self,ticket,from_status,to_status,user):
        """
        Checks if the ticket's status changed from 'Partially Fixed' to 'Deployable on Hold'.

        Parameters:
            ticket (dict): A Mantis ticket object (must include 'history').
            from_status (string): The previous status.
            to_status (string): The new status.
            user: The user responsible for changing the status.

        Returns:
            bool: True if status changed from the from_status to the to_status, False otherwise.
        """
        history = ticket.get("history", [])[::-1]  # Reverse the history list


        for entry in history:
            if (entry.get("field", {}).get("name") == "resolution" and
                entry.get("message") == "Current Status"):

                old_status = entry.get("old_value", {}).get("name", "")
                new_status = entry.get("new_value", {}).get("name", "")
                mantis_user = entry.get("user", {}).get("name", "")

                if mantis_user==user and old_status == from_status and new_status == to_status:
                    return True

        return False


    def create_ticket(self, ticket_data):
        """
        Create a new Mantis ticket with the provided ticket data.
        """
        url = f"{self.mantis_path}/api/rest/issues/"
        try:
            response = requests.post(url, headers=self.headers, json=ticket_data, verify=False)
            if response.status_code == 201:
                return response.json()
            else:
                mantis_logger.error(f"Error creating ticket: {response.text}")
                mantis_logger.error(json.dumps(ticket_data, indent=2))
                return None
        except Exception as e:
            mantis_logger.error(f"Exception while creating new ticket: {e}")
            return None

    def get_developer_for_module(self,moduleName):
        #   Map for getting dev name wrt module
        devModuleMap = {
        "Activities" : StringConstants.MUHAMMAD_MOIZ_PATUJO,
        "Admin" : StringConstants.SYED_ZAIN_BADAR_UDDIN,
        "AP" : StringConstants.OWAIS_UL_HAQ,
        "AP Report" : StringConstants.OWAIS_UL_HAQ,
        "AR" : StringConstants.OWAIS_UL_HAQ,
        "Banquet" : StringConstants.SYED_MOIZ_ISMAIL,
        "Banquet Report" : StringConstants.SYED_MOIZ_ISMAIL,
        "Campaign" : StringConstants.MUHAMMAD_USAMA_HABIB_UR_REHMAN,
        "Classes" : StringConstants.MUHAMMAD_MOIZ_PATUJO,
        "Club Now" : StringConstants.FARAZ_ABBASI,
        "Club View" : StringConstants.FARAZ_ABBASI,
        "Compliance" : StringConstants.SIMON_ANTHONY,
        "Concierge" : StringConstants.MUHAMMAD_MOIZ_PATUJO,
        "Credit Card" : StringConstants.SYED_ZAIN_BADAR_UDDIN,
        "Dashboard" : StringConstants.SYEDA_ZUNAIRA_AHMED,
        "Dining" : StringConstants.SYED_MOIZ_ISMAIL,
        "Employee App" : StringConstants.USAMA_SAJID,
        "Events" : StringConstants.MUHAMMAD_MOIZ_PATUJO,
        "F & B POS Report" : StringConstants.SHAHROZ_SHAHID_KHAN,
        "FB POS" : StringConstants.SHAHROZ_SHAHID_KHAN,
        "Front Desk" : StringConstants.AADESH_KUMAR,
        "Gate House" : StringConstants.AADESH_KUMAR,
        "General" : StringConstants.SYED_ZAIN_BADAR_UDDIN,
        "GL" : StringConstants.OWAIS_UL_HAQ,
        "GL Report" : StringConstants.OWAIS_UL_HAQ,
        "HOA" : StringConstants.ZUBAIR_AHMED,
        "Infrastructure" : StringConstants.SYED_ZAIN_BADAR_UDDIN,
        "Inventory" : StringConstants.SYED_KHURRAM_KAMRAN,
        "Inventory Report" : StringConstants.SYED_KHURRAM_KAMRAN,
        "Liferay" : StringConstants.AHSAN_RAZA,
        "Locker Reservation" : StringConstants.ALI_HASSAN,
        "Marina" : StringConstants.ALI_HASSAN,
        "Member Center" : StringConstants.MUHAMMAD_USAMA_HABIB_UR_REHMAN,
        "Membership" : StringConstants.MUHAMMAD_USAMA_HABIB_UR_REHMAN,
        "Membership Report" : StringConstants.MUHAMMAD_USAMA_HABIB_UR_REHMAN,
        "Northstar Connect" : StringConstants.AHSAN_RAZA,
        "POA" : StringConstants.SIMON_ANTHONY,
        "POA Connect" : StringConstants.SIMON_ANTHONY,
        "Purchasing" : StringConstants.SYED_KHURRAM_KAMRAN,
        "Purchasing Report" : StringConstants.SYED_KHURRAM_KAMRAN,
        "Resort Connect" : StringConstants.ALI_HASSAN,
        "Retail POS" : StringConstants.SYED_KHURRAM_KAMRAN,
        "Retail POS Reports" : StringConstants.SYED_KHURRAM_KAMRAN,
        "Room Reservation" : StringConstants.ALI_HASSAN,
        "Shopping Cart" : StringConstants.SYED_ZAIN_BADAR_UDDIN,
        "Spa" : StringConstants.MUHAMMAD_MOIZ_PATUJO,
        "Tableside POS" : StringConstants.SYED_MOIZ_ISMAIL,
        "Tee Time" : StringConstants.SYED_KHURRAM_KAMRAN,
        "Timekeeping" : StringConstants.MUHAMMAD_MOIZ_PATUJO,
        "Timekeeping Report" : StringConstants.MUHAMMAD_MOIZ_PATUJO,
        "WO Connect" : StringConstants.ALI_HASSAN,
        "Work Order" : StringConstants.ALI_HASSAN,
        }
        return devModuleMap.get(moduleName)
    
    def get_qa_for_module(self,moduleName):
        # Map for getting QA name wrt module
        qaModuleMap = {
        "Activities" : StringConstants.RIMSHA_MOIN,
        "Admin" : StringConstants.SHABBIR_AHMED,
        "AP" : StringConstants.MUHAMMAD_ZEESHAN,
        "AP Report" : StringConstants.MUHAMMAD_ZEESHAN,
        "AR" : StringConstants.MUHAMMAD_ZEESHAN,
        "Banquet" : StringConstants.HAZIQ_JAMIL,
        "Banquet Report" : StringConstants.HAZIQ_JAMIL,
        "Campaign" : StringConstants.FARRUKH_FAHIM,
        "Classes" : StringConstants.RIMSHA_MOIN,
        "Club Now" : StringConstants.NIMRA_IFTIKHAR,
        "Club View" : StringConstants.NIMRA_IFTIKHAR,
        "Compliance" : StringConstants.HAFSA_YASEEN,
        "Concierge" : StringConstants.RIMSHA_MOIN,
        "Credit Card" : StringConstants.SHABBIR_AHMED,
        "Dashboard" : StringConstants.AMMAR_BHAI,
        "Dining" : StringConstants.HAZIQ_JAMIL,
        "Employee App" : StringConstants.RIMSHA_MOIN,
        "Events" : StringConstants.RIMSHA_MOIN,
        "F & B POS Report" : StringConstants.KAUSAR_TASNEEM,
        "FB POS" : StringConstants.KAUSAR_TASNEEM,
        "Front Desk" : StringConstants.FARRUKH_FAHIM,
        "Gate House" : StringConstants.FARRUKH_FAHIM,
        "General" : StringConstants.MUHAMMAD_ZEESHAN,
        "GL" : StringConstants.MUHAMMAD_ZEESHAN,
        "GL Report" : StringConstants.MUHAMMAD_ZEESHAN,
        "HOA" : StringConstants.HAFSA_YASEEN,
        "Infrastructure" : StringConstants.SHABBIR_AHMED,
        "Inventory" : StringConstants.ANUSHA_MAKHIJA,
        "Inventory Report" : StringConstants.ANUSHA_MAKHIJA,
        "Liferay" : StringConstants.GHULAM_SAKINA,
        "Locker Reservation" : StringConstants.QAZI_HAMZA_AHMED,
        "Marina" : StringConstants.QAZI_HAMZA_AHMED,
        "Member Center" : StringConstants.FARRUKH_FAHIM,
        "Membership" : StringConstants.FARRUKH_FAHIM,
        "Membership Report" : StringConstants.FARRUKH_FAHIM,
        "Northstar Connect" : StringConstants.GHULAM_SAKINA,
        "POA" : StringConstants.HAFSA_YASEEN,
        "POA Connect" : StringConstants.HAFSA_YASEEN,
        "Purchasing" : StringConstants.ANUSHA_MAKHIJA,
        "Purchasing Report" : StringConstants.ANUSHA_MAKHIJA,
        "Resort Connect" : StringConstants.QAZI_HAMZA_AHMED,
        "Retail POS" : StringConstants.ANUSHA_MAKHIJA,
        "Retail POS Reports" : StringConstants.ANUSHA_MAKHIJA,
        "Room Reservation" : StringConstants.QAZI_HAMZA_AHMED,
        "Shopping Cart" : StringConstants.SHABBIR_AHMED,
        "Spa" : StringConstants.RIMSHA_MOIN,
        "Tableside POS" : StringConstants.HAZIQ_JAMIL,
        "Tee Time" : StringConstants.ANUSHA_MAKHIJA,
        "Timekeeping" : StringConstants.RIMSHA_MOIN,
        "Timekeeping Report" : StringConstants.RIMSHA_MOIN,
        "WO Connect" : StringConstants.QAZI_HAMZA_AHMED,
        "Work Order" : StringConstants.QAZI_HAMZA_AHMED,
            };

        return qaModuleMap[moduleName] or "Unassigned";
    
    def get_record_type(self,issue):
        return self.get_custom_field(issue,"Record Type")

    def get_target_version(self,issue):
        return self.get_custom_field(issue,"Target Version")

    def get_clients(self,issue):
        return self.get_custom_field(issue,"Clients")

    def get_contacts(self,issue):
        return self.get_custom_field(issue,"Contacts")

    def get_pvcs_id(self,issue):
        return self.get_custom_field(issue,"PVCS ID")

    def get_qa_owner(self,issue):
        return self.get_custom_field(issue,"QA Owner")

    def get_priority_order(self,issue):
        return self.get_custom_field(issue,"Priority Order")

    def get_for_release_notes(self,issue):
        return self.get_custom_field(issue,"For Release Notes")

    def get_platform(self,issue):
        return self.get_custom_field(issue,"Platform")

    def get_sugar_case_number(self,issue):
        return self.get_custom_field(issue,"Sugar Case Number")

    def get_erdate(self,issue):
        return self.get_custom_field(issue,"ERDate")

    def get_resolution(self,issue):
        return self.get_custom_field(issue,"Resolution")

    def get_available_to_clients(self,issue):
        return self.get_custom_field(issue,"Available_To_Clients")

    def get_code_reviewed_by(self,issue):
        return self.get_custom_field(issue,"Code Reviewed By")

    def get_code_review_ids(self,issue):
        return self.get_custom_field(issue,"Code Review Id(s)")

    def get_action(self,issue):
        return self.get_custom_field(issue,"Action")

    def get_change_initiated_from(self,issue):
        return self.get_custom_field(issue,"Change Initiated From")

    def get_task_order(self,issue):
        return self.get_custom_field(issue,"Task_Order")

    def get_target_patch(self,issue):
        return self.get_custom_field(issue,"Target Patch")

    def get_efforts_dev(self,issue):
        return self.get_custom_field(issue,"Efforts Dev")

    def get_efforts_qa(self,issue):
        return self.get_custom_field(issue,"Efforts QA")

    def get_faucet(self,issue):
        return self.get_custom_field(issue,"Faucet")

    def get_git_file_trace(self,issue):
        return self.get_custom_field(issue,"Git File Trace")

    def get_impacted_areas(self,issue):
        return self.get_custom_field(issue,"Impacted Areas")

    def get_test_scenarios_and_cases(self,issue):
        return self.get_custom_field(issue,"Test Scenarios/Cases")

    def get_summary(self,issue):
        return self.get_custom_field(issue,"Summary")

    def get_product_delivery_manager(self,issue):
        return self.get_custom_field(issue,"Product Delivery Manager (PDM)")

    def get_sprint(self,issue):
        return self.get_custom_field(issue,"Sprint")

    def get_design_review(self,issue):
        return self.get_custom_field(issue,"Design Review")

    def get_client_demo(self,issue):
        return self.get_custom_field(issue,"Client Demo")

    def get_purchase_order(self,issue):
        return self.get_custom_field(issue,"Purchase Order")

    def get_club_informed(self,issue):
        return self.get_custom_field(issue,"Club_Informed")
