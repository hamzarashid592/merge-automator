from projects.ticket_manager import modify_tickets
from projects.sprint_planner import plan_sprint
from core.string_constants import StringConstants

from operations.mantis_operations import MantisOperations

if __name__ == "__main__":

    mantis = MantisOperations(StringConstants.REGRESSION)

    # mantis.unrelate_issues(original_issue_id="422406", related_issue_id=422725)

    # mantis.update_owner(423574,StringConstants.SYED_KHURRAM_KAMRAN)

    modify_tickets()

    # plan_sprint()