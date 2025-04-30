import requests
from core.logging_config import LoggerSetup
import time
from encryption.token_manager import TokenManager
from operations.utils import get_target_project
from core.config_manager import ConfigurationManager
from core.string_constants import StringConstants

git_logger = LoggerSetup.setup_logger("git", "logs/git")

class GitLabOperations:
    def __init__(self, project):
        """
        Initialize GitLabOperations with the GitLab API base URL and authentication token.
        """
        # Fetch the token dynamically
        # Initialize the configuration manager based on the project
        config = ConfigurationManager(config_file=f"configs/{project}.json")

        self.gitlab_path = config.get("GITLAB_PATH")
        
        token_manager = TokenManager(key_file=config.get("KEY_FILE"), token_file=config.get("TOKEN_FILE"))
        tokens = token_manager.get_tokens()
        self.auth_token = tokens["gitlab_token"]

        self.headers = {
            'PRIVATE-TOKEN': self.auth_token,
            'Content-Type': 'application/json'
        }

    def get_merge_request(self, merge_request_url):
        """
        Fetch merge request data by its URL.

        Parameters:
            merge_request_url (str): The URL of the merge request.

        Returns:
            dict: Merge request data or None if an error occurs.
        """
        merge_request_id = merge_request_url.split('/')[-1]
        target_project_id = get_target_project(merge_request_url)
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
        target_project_id = get_target_project(merge_request_url)
        if not target_project_id:
            return False

        merge_mr_url = f"{self.gitlab_path}/api/v4/projects/{target_project_id}/merge_requests/{merge_request_id}/merge"

        for attempt in range(1, retries + 1):
            response = requests.put(merge_mr_url, headers=self.headers, verify=False)
            response_body = response.json()
            if response.status_code == 200 and response_body.get("state") == "merged":
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
