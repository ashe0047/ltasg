from api import LTADataMall
from transport.transport import Transport
from constants import TransportType

class Bus(Transport):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.bus_services = self.transport_services[TransportType.BUS]

    async def arrival(self, bus_stop_code: int, bus_no: int):
        data = await self.lta_api.fetch(self.bus_services['ARRIVAL'], query_params={
            "BusStopCode": bus_stop_code,
            "ServiceNo": bus_no
        })
        return data["Services"]
    
    async def services(self):
        data = await self.lta_api.fetch(self.bus_services['SERVICES'])
        return data["value"]

    async def routes(self):
        data = await self.lta_api.fetch(self.bus_services['ROUTES'])
        return data["value"]

    async def stops(self):
        data = await self.lta_api.fetch(self.bus_services['STOPS'])
        return data["value"]

    
# BusArrivalv2?BusStopCode=71111&ServiceNo=137