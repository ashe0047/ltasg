from transport.transport import Transport
from constants import TransportType


class Taxi(Transport):
    def __init__(self, api_key) -> None:
        super().__init__(api_key)
        self.taxi_services = self.transport_services[TransportType.TAXI]

    async def availability(self):
        data = await self.lta_api.fetch(self.taxi_services["AVAILABILITY"])
        return data['value']
    
    async def stands(self):
        data = await self.lta_api.fetch(self.taxi_services["STANDS"])
        return data['value']