import re
import logging

def get_target_branch(merge_request_url):
    """
    Get the target branch based on the merge request URL.

    Parameters:
        merge_request_url (str): The URL of the merge request.

    Returns:
        str: The name of the target branch, or None if no match is found.
    """
    if 'NS61x' in merge_request_url:
        return "NEXUS05-BO"
    elif 'NSConnect40' in merge_request_url:
        return "NEXUS05-C4"
    elif 'nscp30' in merge_request_url:
        return "NEXUS05-C3"
    elif 'ClubNow' in merge_request_url:
        return "NEXUS05-APP"
    else:
        logging.error(f"Couldn't get a target branch for the merge request: {merge_request_url}")
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
