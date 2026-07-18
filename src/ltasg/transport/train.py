"""Train (MRT/LRT) API methods."""

from ..transport.base import Transport
from ..constants import TransportType


class Train(Transport):
    """Wrapper around LTA DataMall Train APIs."""

    _service_type = TransportType.TRAIN

    async def service_alerts(self):
        """Train service disruption info.

        API returns value as a single dict: {Status, AffectedSegments, Message}.
        Returns that dict directly.
        """
        return await self.lta_api.fetch_value(self._svc['SERVICE_ALERTS'])

    async def facilities_maintenance(self):
        """Adhoc lift maintenance in MRT stations."""
        return await self.lta_api.fetch(self._svc['FACILITIES_MAINTENANCE'])

    async def station_crowd_density_realtime(self, train_line: str):
        """Real-time station crowdedness for a train line (e.g. 'EWL', 'NSL')."""
        return await self.lta_api.fetch(
            self._svc["PLATFORM_CROWD_DENSITY"]['REALTIME'],
            query_params={"TrainLine": train_line},
        )

    async def station_crowd_density_forecast(self, train_line: str):
        """Forecasted station crowdedness for a train line."""
        return await self.lta_api.fetch(
            self._svc["PLATFORM_CROWD_DENSITY"]['FORECAST'],
            query_params={"TrainLine": train_line},
        )

    async def passenger_volume_by_od_train_stations(self, date: str = None):
        """Passenger trips from origin to destination train stations (returns download Link)."""
        params = {}
        if date:
            params["Date"] = date
        return await self.lta_api.fetch(
            self._svc['PV_OD_TRAIN'], query_params=params or None
        )

    async def passenger_volume_by_train_stations(self, date: str = None):
        """Tap in/out passenger volume by train station (returns download Link)."""
        params = {}
        if date:
            params["Date"] = date
        return await self.lta_api.fetch(
            self._svc['PV_TRAIN'], query_params=params or None
        )
