"""E2E tests for ltasg SDK — hit the live LTA DataMall API.

Quick tests (arrival, filtered services/stops, train alerts, taxi) run in < 10s.
Slow tests (unfiltered paginated routes/stops) are grouped separately.
"""

import unittest
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ltasg.transport.bus import Bus
from ltasg.transport.train import Train
from ltasg.transport.taxi import Taxi
from ltasg.constants import DEFAULT_BASE_URL
import dotenv


class TestQuickE2E(unittest.IsolatedAsyncioTestCase):
    """Quick E2E tests — all run in < 10s total."""

    dotenv.load_dotenv()
    api_key = os.getenv("LTA_API_KEY")
    bus = Bus(api_key=api_key)
    train = Train(api_key=api_key)
    taxi = Taxi(api_key=api_key)

    def setUp(self):
        self.assertEqual(self.bus.lta_api.BASE_URL, DEFAULT_BASE_URL)
        self.assertEqual(self.train.lta_api.BASE_URL, DEFAULT_BASE_URL)
        self.assertEqual(self.taxi.lta_api.BASE_URL, DEFAULT_BASE_URL)
        # Reset sessions — IsolatedAsyncioTestCase creates a fresh event loop per test
        for api in [self.bus.lta_api, self.train.lta_api, self.taxi.lta_api]:
            api._session = None

    async def test_bus_arrival(self):
        """Bus Arrival v3 — verify endpoint, Monitored attribute, alphanumeric ServiceNo."""
        # Numeric service number
        data = await self.bus.arrival(71111, "63")
        self.assertGreater(len(data), 0)
        self.assertEqual(data[0]['ServiceNo'], "63")
        self.assertIn("Monitored", data[0]['NextBus'])

        # Alphanumeric service number
        data2 = await self.bus.arrival(71111, "63M")
        self.assertGreater(len(data2), 0)
        self.assertEqual(data2[0]['ServiceNo'], "63M")

    async def test_bus_services(self):
        """Bus Services — unfiltered returns records, filtered returns correct subset."""
        all_svc = await self.bus.services()
        self.assertGreater(len(all_svc), 0, "Services data is empty")

        filtered = await self.bus.services(service_no="63")
        self.assertGreater(len(filtered), 0, "Filtered services empty")
        for s in filtered:
            self.assertIn("63", s['ServiceNo'])

    async def test_bus_stops_filtered(self):
        """Bus Stops with BusStopCode filter — returns specific stop."""
        stops = await self.bus.stops(bus_stop_code="01012")
        self.assertGreater(len(stops), 0)
        self.assertEqual(stops[0]['BusStopCode'], "01012")
        self.assertIn("RoadName", stops[0])

    async def test_train_facilities_maintenance(self):
        """Facilities Maintenance — returns list of lift maintenance records."""
        data = await self.train.facilities_maintenance()
        # May be empty if no maintenance is scheduled; verify shape if present
        if data:
            self.assertIn("Line", data[0])
            self.assertIn("StationCode", data[0])
            self.assertIn("StationName", data[0])
            self.assertIn("LiftDesc", data[0])
        print(f"Facilities Maintenance: {len(data)} records")

    async def test_train_service_alerts(self):
        """Train Service Alerts — returns dict with Status, AffectedSegments, Message."""
        alerts = await self.train.service_alerts()
        self.assertIn("Status", alerts)
        self.assertIn("AffectedSegments", alerts)
        self.assertIn("Message", alerts)
        self.assertIn(alerts['Status'], [1, 2], "Status is not valid")

    async def test_taxi_availability(self):
        """Taxi Availability — returns list of taxi locations."""
        data = await self.taxi.availability()
        self.assertGreater(len(data), 0, "Availability data is empty")
        self.assertIn("Latitude", data[0])
        self.assertIn("Longitude", data[0])

    async def test_taxi_stands(self):
        """Taxi Stands — returns list of stand details."""
        data = await self.taxi.stands()
        self.assertGreater(len(data), 0, "Stands data is empty")
        self.assertIn("TaxiCode", data[0])
        self.assertIn("Latitude", data[0])


class TestSlowE2E(unittest.IsolatedAsyncioTestCase):
    """Slow E2E tests — paginated endpoints that take 30s+.

    These are skipped by default. Run with: SLOW_TESTS=1 python -m unittest
    """

    dotenv.load_dotenv()
    api_key = os.getenv("LTA_API_KEY")
    bus = Bus(api_key=api_key)

    def setUp(self):
        skip = os.getenv("SLOW_TESTS") != "1"
        if skip:
            self.skipTest("Skip slow E2E. Set SLOW_TESTS=1 to run.")

    async def test_bus_routes_all(self):
        """Bus Routes — full paginated fetch. Can take 30-60s."""
        routes = await self.bus.routes()
        self.assertGreater(len(routes), 100, "Expected many route records")

    async def test_bus_stops_all(self):
        """Bus Stops — full paginated fetch. Can take 30-60s."""
        stops = await self.bus.stops()
        self.assertGreater(len(stops), 100, "Expected many stop records")

    async def test_stop_services(self):
        """stop_services — fetches all routes then filters client-side."""
        services = await self.bus.stop_services("71111")
        self.assertGreater(len(services), 0, "Expected services at stop 71111")


if __name__ == "__main__":
    unittest.main()


class TestTrafficE2E(unittest.IsolatedAsyncioTestCase):
    """Quick E2E tests for Traffic APIs — run in < 5s total."""

    dotenv.load_dotenv()
    api_key = os.getenv("LTA_API_KEY")
    from ltasg.traffic import Traffic
    traffic = Traffic(api_key=api_key)

    def setUp(self):
        self.assertEqual(self.traffic.lta_api.BASE_URL, DEFAULT_BASE_URL)
        self.traffic.lta_api._session = None  # fresh session per test

    async def test_carpark_availability(self):
        """Carpark Availability — always populated."""
        data = await self.traffic.carpark_availability()
        self.assertGreater(len(data), 0, "Expected carpark data")
        self.assertIn("CarParkID", data[0])
        self.assertIn("AvailableLots", data[0])

    async def test_traffic_incidents(self):
        """Traffic Incidents — usually populated."""
        data = await self.traffic.traffic_incidents()
        self.assertGreater(len(data), 0, "Expected traffic incident data")
        self.assertIn("Type", data[0])
        self.assertIn("Message", data[0])


