"""Traffic API methods."""

from .api import LTADataMall
from .constants import DEFAULT_BASE_URL, TRAFFIC_SERVICES


class Traffic:
    """Wrapper around LTA DataMall Traffic APIs.

    Can be used as an async context manager::

        async with Traffic(api_key=key) as t:
            data = await t.carpark_availability()
    """

    def __init__(self, base_url=DEFAULT_BASE_URL, api_key=None):
        self.lta_api = LTADataMall(base_url=base_url, api_key=api_key)
        self._svc = TRAFFIC_SERVICES

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.lta_api.close()

    async def carpark_availability(self):
        """Available lots for HDB, LTA and URA carparks."""
        return await self.lta_api.fetch(self._svc["CARPARK_AVAILABILITY"])

    async def estimated_travel_times(self):
        """Estimated travel times of expressways (in segments)."""
        return await self.lta_api.fetch(self._svc["ESTIMATED_TRAVEL_TIMES"])

    async def faulty_traffic_lights(self):
        """Alerts of faulty traffic lights or scheduled maintenance."""
        return await self.lta_api.fetch(self._svc["FAULTY_TRAFFIC_LIGHTS"])

    async def planned_road_openings(self):
        """Information on planned road openings."""
        return await self.lta_api.fetch(self._svc["PLANNED_ROAD_OPENINGS"])

    async def approved_road_works(self):
        """Information on approved road works."""
        return await self.lta_api.fetch(self._svc["APPROVED_ROAD_WORKS"])

    async def traffic_images(self):
        """Links to live traffic images along expressways."""
        return await self.lta_api.fetch(self._svc["TRAFFIC_IMAGES"])

    async def traffic_incidents(self):
        """Current traffic incidents (accidents, breakdowns, etc.)."""
        return await self.lta_api.fetch(self._svc["TRAFFIC_INCIDENTS"])

    async def traffic_speed_bands(self):
        """Current traffic speeds expressed in speed bands (v4)."""
        return await self.lta_api.fetch(self._svc["TRAFFIC_SPEED_BANDS"])

    async def vms(self):
        """Variable Message Signs / EMAS advisories."""
        return await self.lta_api.fetch(self._svc["VMS"])

    async def traffic_flow(self):
        """Hourly average traffic flow (quarterly data; returns download Link)."""
        return await self.lta_api.fetch(self._svc["TRAFFIC_FLOW"])

    async def flood_alerts(self):
        """Flood alert information across Singapore, provided by PUB."""
        return await self.lta_api.fetch(self._svc["FLOOD_ALERTS"])
