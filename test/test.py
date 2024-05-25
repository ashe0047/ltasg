import unittest
from transport.bus import Bus
from transport.train import Train
from transport.taxi import Taxi
import dotenv
import os

class Test(unittest.IsolatedAsyncioTestCase):
    dotenv.load_dotenv()
    api_key = os.getenv("LTA_API_KEY")
    bus = Bus(api_key=api_key)
    train = Train(api_key=api_key)
    taxi = Taxi(api_key=api_key)

    async def test_bus(self):
        print("Start test for bus \n")
        # bus arrival
        arrival_params = [
            [71111, 63],
            [71111, "63M"],
            [71111, 137],
            [71119, 63],
            [71119, "63M"],
            [71119, 137],
        ]
        for param in arrival_params:
            arrival_data = await self.bus.arrival(param[0], param[1])
            print(arrival_data)
            self.assertEqual(str(
                param[1]), arrival_data[0]['ServiceNo'], "Service No is not the same as param")
        # bus services
        services_data = await self.bus.services()
        print(services_data)
        self.assertNotEqual(len(services_data), 0, "Services data is empty")

        # bus routes
        routes_data = await self.bus.routes()
        print(routes_data)
        self.assertNotEqual(len(routes_data), 0, "Routes data is empty")

        # bus stops
        stops_data = await self.bus.stops()
        print(stops_data)
        self.assertNotEqual(len(stops_data), 0, "Stops data is empty")

        print("\Bus test completed\n")

    async def test_train(self):
        print("Start test for train \n")

        # service alerts
        service_alerts_data = await self.train.service_alerts()
        print(service_alerts_data)
        self.assertIn(service_alerts_data['Status'], [
                      1, 2], "Status returned is not valid")
        # platform crowd density realtime

        # platform crowd density forecast

        print("\Train test completed\n")

    async def test_taxi(self):
        print("Start test for taxi \n")

        # Availability
        availability_data = await self.taxi.availability()
        print(availability_data)
        self.assertNotEqual(len(availability_data), 0,
                            "Availability data is empty")
        # stands
        stands_data = await self.taxi.stands()
        print(stands_data)
        self.assertNotEqual(len(stands_data), 0, "Stands data is empty")

        print("\Taxi test completed\n")


if __name__ == "__main__":
    unittest.main()
