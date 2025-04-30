from .regression import RegressionMerger
from .ps import PSMerger
from core.string_constants import StringConstants

class MergerFactory:
    @staticmethod
    def get_merger(ticket_type):
        if ticket_type == StringConstants.REGRESSION:
            return RegressionMerger()
        elif ticket_type == StringConstants.PROD_SUPPORT:
            return PSMerger()
        else:
            raise ValueError("Unsupported ticket type")
