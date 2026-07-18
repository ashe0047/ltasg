"""Taxi API methods."""

from ..transport.base import Transport
from ..constants import TransportType


class Taxi(Transport):
    """Wrapper around LTA DataMall Taxi APIs."""

    _service_type = TransportType.TAXI

    async def availability(self):
        """Available taxi locations."""
        return await self.lta_api.fetch(self._svc["AVAILABILITY"])

    async def stands(self):
        """Taxi stand locations and details."""
        return await self.lta_api.fetch(self._svc["STANDS"])
