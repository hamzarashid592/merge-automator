import re
import os
import requests
from collections import defaultdict
from core.config_manager import ConfigurationManager

class ChatNotifier:
    def __init__(self, ticket_type, log_dir):
        self.ticket_type = ticket_type
        self.log_dir = log_dir
        self.log_path = self._get_latest_log_path()
        self.log_path = 'logs//Sample.log'

        # Load webhook from config
        config_mgr = ConfigurationManager()
        self.webhook_url = config_mgr.get("WEBHOOKS", {}).get(ticket_type)

        if not self.webhook_url:
            raise ValueError(f"No webhook configured for ticket type: {ticket_type}")

        self.review_map = defaultdict(set)
        self.qa_skipped_mrs = set()
        self.merged_mrs = set()
        self.summary = {
            "tickets_processed": 0
        }

    def _get_latest_log_path(self):
        log_files = [f for f in os.listdir(self.log_dir) if f.startswith(self.ticket_type)]
        if not log_files:
            raise FileNotFoundError(f"No log file found for ticket type '{self.ticket_type}' in '{self.log_dir}'")
        latest = sorted(log_files, reverse=True)[0]
        print(f"[ChatNotifier] Using log file: {latest}")
        return os.path.join(self.log_dir, latest)

    def _parse_full_log(self):
        with open(self.log_path, "r", encoding="utf-8") as file:
            for line in file:
                # Code review lines
                if "Code Review pending at" in line:
                    match = re.search(r"Code Review pending at\s+(.*?)\s+for:\s+(http[^\s]+)", line)
                    if match:
                        reviewer = match.group(1).strip()
                        url = match.group(2).strip()
                        self.review_map[reviewer].add(url)

                # QA skipped lines
                elif "QA Verified label missing in the MR, skipping it for:" in line:
                    match = re.search(r"skipping it for:\s+(http[^\s]+)", line)
                    if match:
                        url = match.group(1).strip()
                        self.qa_skipped_mrs.add(url)

                # Merged lines
                elif "Merge request" in line and "successfully merged" in line:
                    match = re.search(r"Merge request\s+(http[^\s]+)", line)
                    if match:
                        self.merged_mrs.add(match.group(1).strip())

                # Ticket summary lines
                elif "Total Number of Tickets Processed" in line:
                    self.summary["tickets_processed"] += int(line.split(":")[-1].strip())

    def _build_message(self):
        lines = []

        # Heading
        lines.append(f"*🛠️ {self.ticket_type.capitalize()} Merge Summary*\n")

        # Final stats as a blue-style blockquote
        lines.append("> 📦 Total Tickets Processed: {}".format(self.summary["tickets_processed"]))
        lines.append("> 🧪 QA Verification Queue: {}".format(len(self.qa_skipped_mrs)))
        lines.append("> 👁️ Code Review Queue: {}".format(sum(len(urls) for urls in self.review_map.values())))
        lines.append("> ✅ MRs Successfully Merged: {}".format(len(self.merged_mrs)))
        lines.append("")  # spacer

        # Grouped review MRs
        for reviewer, urls in self.review_map.items():
            lines.append(f"*Code Review pending at {reviewer} for:*")
            for url in sorted(urls):
                lines.append(url)
            lines.append("")

        # Listing the successfully merged MR's
        lines.append(f"*Successfully Merged MR's*")
        for mr in self.merged_mrs:
            lines.append(mr)

        return "\n".join(lines)


    def send_summary(self):
        try:
            self._parse_full_log()
            message = self._build_message()

            payload = {"text": message}
            response = requests.post(self.webhook_url, json=payload)

            if response.status_code != 200:
                print(f"[ChatNotifier] Failed to post: {response.status_code} - {response.text}")
                return False

            print(f"[ChatNotifier] Summary posted successfully.")
            return True

        except Exception as e:
            print(f"[ChatNotifier] Error: {e}")
            return False
