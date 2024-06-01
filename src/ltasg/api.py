from aiohttp import ClientSession, ClientConnectionError


class LTADataMall:
    def __init__(self, base_url, api_key) -> None:
        self.BASE_URL = base_url
        self.API_KEY = api_key
        self.HEADERS = {
            "Accept": "application/json",
            "AccountKey": self.API_KEY
        }

    async def fetch(self, service_endpoint: str, query_params: dict = None, data: dict = None):
        url = f"{self.BASE_URL}{service_endpoint}"
        skip_count = 0
        data = []
        if query_params:
            url += "?"
            for param, value in query_params.items():
                url += f"{param}={value}&"
                # if param != list(query_params.keys())[-1]:
                #     url += "&"
        async with ClientSession() as session:
            while True:
                try:
                    url_with_skip = url + f"{"" if query_params else "?"}$skip={skip_count}"
                    async with session.get(url_with_skip, headers=self.HEADERS) as response:
                        if response.ok:
                            curr_data = await response.json()
                            if "Services" in curr_data or isinstance(curr_data['value'], dict):
                                return curr_data
                            if len(curr_data['value']) < 500:
                                data.append(curr_data)
                                break
                            if len(curr_data['value']) == 0:
                                break
                            data.append(curr_data)
                            skip_count += 500
                        else:
                            raise Exception("Error calling api for {} with status code: {}".format(
                                service_endpoint, response.status)) from None
                except ClientConnectionError as e:
                    raise e
            return data

