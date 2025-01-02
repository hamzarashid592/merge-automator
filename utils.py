import re
from logging_config import LoggerSetup
from config_manager import ConfigurationManager

util_logger = LoggerSetup.setup_logger("utils", "logs/utils")
# Initialize the configuration manager
config = ConfigurationManager()

def get_target_branch(merge_request_url):
    """
    Get the target branch based on the merge request URL.

    Parameters:
        merge_request_url (str): The URL of the merge request.

    Returns:
        str: The name of the target branch, or None if no match is found.
    """
    if 'NS61x' in merge_request_url:
        return config.get("NEXUS_BO")
    elif 'NSConnect40' in merge_request_url:
        return config.get("NEXUS_C4")
    elif 'nscp30' in merge_request_url:
        return config.get("NEXUS_C3")
    elif 'ClubNow' in merge_request_url:
        return config.get("NEXUS_APP")
    else:
        util_logger.error(f"Couldn't get a target branch for the merge request: {merge_request_url}")
        return None

def get_target_project(merge_request_url):
        """
        Get the target project ID based on the merge request URL.

        Parameters:
            merge_request_url (str): The URL of the merge request.

        Returns:
            int: Target project ID or None if not found.
        """
        if 'NS61x' in merge_request_url:
            return config.get("BO_PROJECT")
        elif 'NSConnect40' in merge_request_url:
            return config.get("C4_PROJECT")
        elif 'nscp30' in merge_request_url:
            return config.get("C3_PROJECT")
        elif 'ClubNow' in merge_request_url:
            return config.get("APP_PROJECT")
        else:
            util_logger.error(f"Couldn't get a target project for the merge request: {merge_request_url}")
            return None

def extract_ticket_id_from_description(description):
    """
    Extract the ticket ID from a given description.

    Parameters:
        description (str): The description containing the ticket ID.

    Returns:
        str: The extracted ticket ID, or None if no match is found.
    """
    match = re.search(r"Original Ticket: #?<b>#?(\d+)</b>", description)
    return match.group(1) if match else None
