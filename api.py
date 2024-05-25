from aiohttp import ClientSession, ClientConnectionError
import traceback

class LTADataMall:
    def __init__(self, api_key) -> None:
        self.BASE_URL = "http://datamall2.mytransport.sg/ltaodataservice/"
        self.API_KEY = api_key
        self.HEADERS = {
            "Accept": "application/json",
            "AccountKey": self.API_KEY
        }

    async def fetch(self, service_endpoint: str, query_params: dict=None, data:dict=None):
        url = f"{self.BASE_URL}{service_endpoint}"
        if query_params:
            url += "?"
            for param, value in query_params.items():
                url += f"{param}={value}"
                if param != list(query_params.keys())[-1]:
                    url += "&"
        async with ClientSession() as session:
            try:
                async with session.get(url, headers=self.HEADERS) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception("Error calling api for {} with status code: {}".format(
                            service_endpoint, response.status)) from None
            except ClientConnectionError as e:
                raise e
