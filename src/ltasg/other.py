"""Miscellaneous API methods (Active Mobility, Geospatial, EV)."""

from .api import LTADataMall
from .constants import DEFAULT_BASE_URL, OTHER_SERVICES


class Other:
    """Wrapper around LTA DataMall miscellaneous APIs.

    Covers: Bicycle Parking, Geospatial Whole Island,
    EV Charging Points, EV Charging Points Batch.
    """

    def __init__(self, base_url=DEFAULT_BASE_URL, api_key=None):
        self.lta_api = LTADataMall(base_url=base_url, api_key=api_key)
        self._svc = OTHER_SERVICES

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.lta_api.close()

    async def bicycle_parking(self, lat: float, long: float, dist: float = 0.5):
        """Bicycle parking locations within a radius.

        Args:
            lat: Latitude of location.
            long: Longitude of location.
            dist: Radius in kilometres (default 0.5 km).
        """
        return await self.lta_api.fetch(
            self._svc["BICYCLE_PARKING"],
            query_params={"Lat": lat, "Long": long, "Dist": dist},
        )

    async def geospatial_whole_island(self, layer_id: str):
        """Download SHP files for a geospatial layer.

        Args:
            layer_id: Layer name from ANNEX E (case-sensitive, no spaces).
        """
        return await self.lta_api.fetch(
            self._svc["GEOSPATIAL_WHOLE_ISLAND"],
            query_params={"ID": layer_id},
        )

    async def ev_charging_points(self, postal_code: str):
        """EV charging points by postal code.

        Returns charging stations with nested chargingPoints,
        plugTypes, and evIds.
        """
        return await self.lta_api.fetch(
            self._svc["EV_CHARGING_POINTS"],
            query_params={"PostalCode": postal_code},
            records_key="value",
        )

    async def ev_charging_points_batch(self):
        """All EV charging points in a single downloadable file.

        Returns a single record with a ``Link`` key (expires in 5 min).
        """
        return await self.lta_api.fetch(self._svc["EV_CHARGING_POINTS_BATCH"])
