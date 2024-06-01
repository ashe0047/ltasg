from ..transport.transport import Transport
from ..constants import TransportType
from ..helpers.helpers import transform_data


class Bus(Transport):
    def __init__(self, base_url, api_key) -> None:
        super().__init__(base_url=base_url,api_key= api_key)
        self.bus_services = self.transport_services[TransportType.BUS]
    
    async def arrival(self, bus_stop_code: int, bus_no: int):
        data = await self.lta_api.fetch(self.bus_services['ARRIVAL'], query_params={
            "BusStopCode": bus_stop_code,
            "ServiceNo": bus_no
        })
        return data["Services"]
    
    async def services(self):
        data = await self.lta_api.fetch(self.bus_services['SERVICES'])
        return transform_data(data)
    async def stop_services(self, bus_stop_code):
        data = transform_data(await self.lta_api.fetch(self.bus_services['ROUTES']))
        services = [ service["ServiceNo"] for service in data if service['BusStopCode'] == str(bus_stop_code)]
        return services
    async def routes(self):
        data = await self.lta_api.fetch(self.bus_services['ROUTES'])
        return transform_data(data)

    async def stops(self):
        data = await self.lta_api.fetch(self.bus_services['STOPS'])
        return transform_data(data)
