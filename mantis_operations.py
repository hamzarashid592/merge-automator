import requests
from logging_config import LoggerSetup
from config import MANTIS_PATH, KEY_FILE, TOKEN_FILE
from token_manager import TokenManager

mantis_logger = LoggerSetup.setup_logger("mantis", "logs/mantis.log")

class MantisOperations:
    
    def __init__(self):
        """
        Initialize MantisOperations with the Mantis API base URL and authentication token.
        """
        self.mantis_path = MANTIS_PATH

        # Fetch the token dynamically
        token_manager = TokenManager(key_file=KEY_FILE, token_file=TOKEN_FILE)
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
            return response.json()
        else:
            mantis_logger.error(f'Error fetching ticket: {response.text}')
            return None

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

    def get_tickets_from_filter(self, filter_id):
        """
        Get ticket IDs from a Mantis filter.
        """
        tickets = []
        page = 1
        limit = 50  # Fetch up to 50 tickets per page
        while True:
            filter_url = f"{self.mantis_path}/api/rest/issues?filter_id={filter_id}&page={page}&limit={limit}"
            try:
                response = requests.get(filter_url, headers=self.headers, verify=False)
                if response.status_code != 200:
                    mantis_logger.error(f'Error fetching tickets from Mantis filter: {response.text}')
                    break
                ticket_data = response.json()
                tickets.extend(ticket_data.get("issues", []))
                if len(ticket_data.get("issues", [])) < limit:
                    break
                page += 1
            except Exception as e:
                mantis_logger.error(f"Error fetching tickets from Mantis filter: {e}")
                break
        return tickets

    def update_status_to_fixed(self, ticket_id):
        """
        Update ticket status to 'Fixed'.
        """
        update_url = f"{self.mantis_path}/api/rest/issues/{ticket_id}"
        payload = {"resolution": {"name": "Fixed"}}
        response = requests.patch(update_url, headers=self.headers, json=payload, verify=False)
        if response.status_code != 200:
            mantis_logger.error(f'Failed to update status for Ticket ID {ticket_id}: {response.text}')

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
