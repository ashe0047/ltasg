"""Bus API methods."""

from ltasg.constants import TransportType
from ltasg.transport.base import Transport


class Bus(Transport):
    """Wrapper around LTA DataMall Bus APIs.

    All methods return a flat list of record dicts.
    """

    _service_type = TransportType.BUS

    async def arrival(self, bus_stop_code: int, bus_no: str):
        """Real-time bus arrival info.  Supports v3 response (Monitored key)."""
        return await self.lta_api.fetch(
            self._svc["ARRIVAL"],
            query_params={
                "BusStopCode": bus_stop_code,
                "ServiceNo": bus_no,
            },
            records_key="Services",
        )

    async def services(self, service_no: str = None):
        """Bus service information, optionally filtered by service number."""
        params = {}
        if service_no:
            params["ServiceNo"] = service_no
        return await self.lta_api.fetch(
            self._svc["SERVICES"], query_params=params or None
        )

    async def routes(self):
        """All bus route records."""
        return await self.lta_api.fetch(self._svc["ROUTES"])

    async def stops(self, bus_stop_code: str = None):
        """Bus stop information, optionally filtered by stop code."""
        params = {}
        if bus_stop_code:
            params["BusStopCode"] = bus_stop_code
        return await self.lta_api.fetch(self._svc["STOPS"], query_params=params or None)

    async def stop_services(self, bus_stop_code):
        """List of service numbers that serve a given bus stop.

        Fetches all routes then filters client-side (the API does not
        expose a dedicated endpoint for this).
        """
        data = await self.lta_api.fetch(self._svc["ROUTES"])
        return [r["ServiceNo"] for r in data if r["BusStopCode"] == str(bus_stop_code)]

    async def passenger_volume_by_bus_stops(self, date: str = None):
        """Tap in/out passenger volume by bus stop (returns download Link)."""
        params = {}
        if date:
            params["Date"] = date
        return await self.lta_api.fetch(
            self._svc["PV_BUS_STOPS"], query_params=params or None
        )

    async def passenger_volume_by_od_bus_stops(self, date: str = None):
        """Passenger trips from origin to destination bus stops.

        Returns a DataMall download link.
        """
        params = {}
        if date:
            params["Date"] = date
        return await self.lta_api.fetch(
            self._svc["PV_OD_BUS"], query_params=params or None
        )

    async def planned_bus_routes(self):
        """Planned new/updated bus routes data."""
        return await self.lta_api.fetch(self._svc["PLANNED_BUS_ROUTES"])
