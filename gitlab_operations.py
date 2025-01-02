import requests
from logging_config import LoggerSetup
import time
from config import GITLAB_PATH, KEY_FILE, TOKEN_FILE
from token_manager import TokenManager

git_logger = LoggerSetup.setup_logger("git", "logs/git")

class GitLabOperations:
    def __init__(self):
        """
        Initialize GitLabOperations with the GitLab API base URL and authentication token.
        """
        self.gitlab_path = GITLAB_PATH

        # Fetch the token dynamically
        token_manager = TokenManager(key_file=KEY_FILE, token_file=TOKEN_FILE)
        tokens = token_manager.get_tokens()
        self.auth_token = tokens["gitlab_token"]

        self.headers = {
            'PRIVATE-TOKEN': self.auth_token,
            'Content-Type': 'application/json'
        }

    def get_target_project(self, merge_request_url):
        """
        Get the target project ID based on the merge request URL.

        Parameters:
            merge_request_url (str): The URL of the merge request.

        Returns:
            int: Target project ID or None if not found.
        """
        if 'NS61x' in merge_request_url:
            return 3
        elif 'NSConnect40' in merge_request_url:
            return 30
        elif 'nscp30' in merge_request_url:
            return 20
        elif 'ClubNow' in merge_request_url:
            return 2
        else:
            git_logger.error(f"Couldn't get a target project for the merge request: {merge_request_url}")
            return None

    def get_merge_request(self, merge_request_url):
        """
        Fetch merge request data by its URL.

        Parameters:
            merge_request_url (str): The URL of the merge request.

        Returns:
            dict: Merge request data or None if an error occurs.
        """
        merge_request_id = merge_request_url.split('/')[-1]
        target_project_id = self.get_target_project(merge_request_url)
        if not target_project_id:
            return None

        read_mr_url = f"{self.gitlab_path}/api/v4/projects/{target_project_id}/merge_requests/{merge_request_id}"
        response = requests.get(read_mr_url, headers=self.headers, verify=False)

        if response.status_code == 200:
            return response.json()
        else:
            git_logger.error(f'Error fetching merge request: {response.text}')
            return None

    def merge_merge_request(self, merge_request_url, retries=3, delay=5):
        """
        Try to merge a GitLab merge request with retries.

        Parameters:
            merge_request_url (str): The URL of the merge request.
            retries (int): Number of retries in case of failure.
            delay (int): Delay (in seconds) between retries.

        Returns:
            bool: True if the merge is successful, False otherwise.
        """
        merge_request_id = merge_request_url.split('/')[-1]
        target_project_id = self.get_target_project(merge_request_url)
        if not target_project_id:
            return False

        merge_mr_url = f"{self.gitlab_path}/api/v4/projects/{target_project_id}/merge_requests/{merge_request_id}/merge"

        for attempt in range(1, retries + 1):
            response = requests.put(merge_mr_url, headers=self.headers, verify=False)
            if response.status_code == 200:
                # git_logger.info(f"Merge request {merge_request_id} merged successfully.")
                return True
            else:
                git_logger.error(f"Attempt {attempt}: Error merging merge request {merge_request_id}: {response.text}")
                if attempt < retries:
                    git_logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    git_logger.error("Exceeded maximum retry attempts. Merge request could not be merged.")

        return False
