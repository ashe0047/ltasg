from transport.transport import Transport
from constants import TransportType
from typing import Literal

class Train(Transport):
    def __init__(self, api_key) -> None:
        super().__init__(api_key)
        self.train_services = self.transport_services[TransportType.TRAIN]

    async def service_alerts(self):
        data = await self.lta_api.fetch(self.train_services['SERVICE_ALERTS'])
        return data['value']
    
    # API currently results in Error 404 not found
    # async def platform_crowd_density(self, type: Literal["realtime", "forecast"] = "realtime"):
    #     if type == "realtime":
    #         return await self.lta_api.fetch(self.train_services["PLATFORM_CROWD_DENSITY"]['REALTIME'])
    #     else:
    #         return await self.lta_api.fetch(self.train_services["PLATFORM_CROWD_DENSITY"]["FORECAST"])