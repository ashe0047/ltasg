from ..api import LTADataMall
from ..constants import LTA_SERVICES


class Transport:
    def __init__(self, base_url, api_key) -> None:
        self.lta_api = LTADataMall(base_url=base_url, api_key=api_key)
        self.transport_services = LTA_SERVICES['PUBLIC_TRANSPORT_SERVICES']
    