"""Base class for transport-domain API wrappers."""

from typing import ClassVar

from ltasg.api import LTADataMall
from ltasg.constants import DEFAULT_BASE_URL, LTA_SERVICES, TransportType


class Transport:
    """Base class for public-transport API wrappers (Bus, Train, Taxi).

    Subclasses override ``_service_type`` to select the correct endpoint
    mapping from ``LTA_SERVICES``.  The selected mapping is stored in
    ``self._svc``.

    Can be used as an async context manager::

        async with Bus(api_key=key) as bus:
            data = await bus.arrival(71111, "63")
    """

    _service_type: ClassVar[TransportType | None] = None

    def __init__(self, base_url=DEFAULT_BASE_URL, api_key=None):
        self.lta_api = LTADataMall(base_url=base_url, api_key=api_key)
        services = LTA_SERVICES["PUBLIC_TRANSPORT_SERVICES"]
        self._svc = services[self._service_type] if self._service_type else {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.lta_api.close()
