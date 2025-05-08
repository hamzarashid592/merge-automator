from core.logging_config import LoggerSetup
from operations.mantis_operations import MantisOperations
from operations.gitlab_operations import GitLabOperations
from operations.google_sheets_operations import GoogleSheetsOperations
from core.config_manager import ConfigurationManager
from notifier.chat_notifier import ChatNotifier

class BaseMerger:
    def __init__(self, ticket_type, config_file, logger_name):
        self.ticket_type = ticket_type
        self.config = ConfigurationManager(config_file=config_file)
        self.mantis = MantisOperations(ticket_type)
        self.gitlab = GitLabOperations(ticket_type)
        self.logger = LoggerSetup.setup_logger(logger_name, f"logs/{logger_name}")
        self.sheets = GoogleSheetsOperations()
        self.progress = {"status": "idle", "percentage": 0}

        # Chat notification configuration
        self.enable_notifier = self.config.get("ENABLE_CHAT_NOTIFICATIONS", False)
        if self.enable_notifier:
            webhook_url = self.config.get("WEBHOOK_URL")
            if webhook_url:
                self.chat_notifier = ChatNotifier(
                    ticket_type=ticket_type,
                    log_dir="logs",
                    webhook_url=webhook_url
                )
            else:
                self.chat_notifier = None
                self.logger.warning("Chat notifications enabled but no WEBHOOK_URL provided.")
        else:
            self.chat_notifier = None

    def run(self):
        raise NotImplementedError("Subclasses must implement the run method")
