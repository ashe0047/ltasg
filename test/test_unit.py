"""Unit tests for ltasg SDK — all API calls are mocked."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from unittest.mock import AsyncMock, patch

from ltasg.api import LTADataMall
from ltasg.constants import DEFAULT_BASE_URL, LTA_SERVICES, TransportType
from ltasg.transport.bus import Bus
from ltasg.transport.taxi import Taxi
from ltasg.transport.train import Train


class TestConstants(unittest.TestCase):
    def test_default_url_uses_https(self):
        self.assertTrue(DEFAULT_BASE_URL.startswith("https://"))
        self.assertIn("datamall2.mytransport.sg", DEFAULT_BASE_URL)

    def test_bus_endpoints(self):
        svc = LTA_SERVICES["PUBLIC_TRANSPORT_SERVICES"][TransportType.BUS]
        self.assertEqual(svc["ARRIVAL"], "v3/BusArrival")
        self.assertEqual(svc["SERVICES"], "BusServices")
        self.assertEqual(svc["ROUTES"], "BusRoutes")
        self.assertEqual(svc["STOPS"], "BusStops")

    def test_train_endpoints(self):
        svc = LTA_SERVICES["PUBLIC_TRANSPORT_SERVICES"][TransportType.TRAIN]
        self.assertEqual(svc["SERVICE_ALERTS"], "TrainServiceAlerts")
        self.assertEqual(svc["PLATFORM_CROWD_DENSITY"]["REALTIME"], "PCDRealTime")
        self.assertEqual(svc["PLATFORM_CROWD_DENSITY"]["FORECAST"], "PCDForecast")
        self.assertEqual(svc["FACILITIES_MAINTENANCE"], "v2/FacilitiesMaintenance")

    def test_taxi_endpoints(self):
        svc = LTA_SERVICES["PUBLIC_TRANSPORT_SERVICES"][TransportType.TAXI]
        self.assertEqual(svc["AVAILABILITY"], "Taxi-Availability")
        self.assertEqual(svc["STANDS"], "TaxiStands")


class TestLTADataMall(unittest.TestCase):
    def test_constructor_stores_values(self):
        api = LTADataMall(base_url="https://example.com/", api_key="test-key")
        self.assertEqual(api.BASE_URL, "https://example.com/")
        self.assertEqual(api.API_KEY, "test-key")
        self.assertEqual(api.HEADERS["Accept"], "application/json")
        self.assertEqual(api.HEADERS["AccountKey"], "test-key")


class TestBus(unittest.IsolatedAsyncioTestCase):
    """Verify Bus methods call fetch() with correct endpoints and params.

    fetch() is mocked to return the flat list it would normally return.
    """

    def setUp(self):
        self.bus = Bus(api_key="test-key")

    async def _mock_fetch(self, return_value):
        patcher = patch.object(self.bus.lta_api, "fetch", new_callable=AsyncMock)
        mock = patcher.start()
        mock.return_value = return_value
        self.addCleanup(patcher.stop)
        return mock

    async def test_arrival_calls_correct_endpoint(self):
        mock = await self._mock_fetch([{"ServiceNo": "15"}])
        result = await self.bus.arrival(83139, "15")
        mock.assert_called_once_with(
            "v3/BusArrival",
            query_params={"BusStopCode": 83139, "ServiceNo": "15"},
            records_key="Services",
        )
        self.assertEqual(result, [{"ServiceNo": "15"}])

    async def test_arrival_returns_empty_array_when_no_buses(self):
        await self._mock_fetch([])
        result = await self.bus.arrival(83139, "999")
        self.assertEqual(result, [])

    async def test_arrival_handles_alphanumeric_service_no(self):
        mock = await self._mock_fetch([{"ServiceNo": "63M"}])
        result = await self.bus.arrival(71111, "63M")
        mock.assert_called_once()
        self.assertEqual(result[0]["ServiceNo"], "63M")

    async def test_services_calls_correct_endpoint(self):
        mock = await self._mock_fetch([{"ServiceNo": "63"}])
        result = await self.bus.services()
        mock.assert_called_once_with("BusServices", query_params=None)
        self.assertEqual(result, [{"ServiceNo": "63"}])

    async def test_services_with_filter_passes_param(self):
        mock = await self._mock_fetch([{"ServiceNo": "63"}])
        result = await self.bus.services(service_no="63")
        mock.assert_called_once_with("BusServices", query_params={"ServiceNo": "63"})
        self.assertEqual(len(result), 1)

    async def test_services_handles_empty_response(self):
        await self._mock_fetch([])
        result = await self.bus.services()
        self.assertEqual(result, [])

    async def test_routes_calls_correct_endpoint(self):
        mock = await self._mock_fetch([{"ServiceNo": "63"}])
        result = await self.bus.routes()
        mock.assert_called_once_with("BusRoutes")
        self.assertEqual(result, [{"ServiceNo": "63"}])

    async def test_routes_handles_empty(self):
        await self._mock_fetch([])
        result = await self.bus.routes()
        self.assertEqual(result, [])

    async def test_routes_multiple_pages_are_flattened(self):
        await self._mock_fetch([{"ServiceNo": "63"}, {"ServiceNo": "63M"}])
        result = await self.bus.routes()
        self.assertEqual(len(result), 2)

    async def test_stops_calls_correct_endpoint(self):
        mock = await self._mock_fetch([{"BusStopCode": "01012"}])
        result = await self.bus.stops()
        mock.assert_called_once_with("BusStops", query_params=None)
        self.assertEqual(result, [{"BusStopCode": "01012"}])

    async def test_stops_with_filter_passes_param(self):
        mock = await self._mock_fetch([{"BusStopCode": "01012"}])
        result = await self.bus.stops(bus_stop_code="01012")
        mock.assert_called_once_with("BusStops", query_params={"BusStopCode": "01012"})
        self.assertEqual(len(result), 1)

    async def test_stop_services_filters_by_stop_code(self):
        await self._mock_fetch(
            [
                {"ServiceNo": "63", "BusStopCode": "83139"},
                {"ServiceNo": "65", "BusStopCode": "83139"},
                {"ServiceNo": "63", "BusStopCode": "99999"},
            ]
        )
        result = await self.bus.stop_services("83139")
        self.assertEqual(sorted(result), sorted(["63", "65"]))

    async def test_stop_services_returns_empty_when_no_match(self):
        await self._mock_fetch(
            [
                {"ServiceNo": "63", "BusStopCode": "83139"},
            ]
        )
        result = await self.bus.stop_services("00000")
        self.assertEqual(result, [])

    async def test_stop_services_handles_empty_routes(self):
        await self._mock_fetch([])
        result = await self.bus.stop_services("83139")
        self.assertEqual(result, [])


class TestTrain(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.train = Train(api_key="test-key")

    async def _mock_fetch(self, return_value):
        patcher = patch.object(self.train.lta_api, "fetch", new_callable=AsyncMock)
        mock = patcher.start()
        mock.return_value = return_value
        self.addCleanup(patcher.stop)
        return mock

    async def _mock_fetch_value(self, return_value):
        patcher = patch.object(
            self.train.lta_api, "fetch_value", new_callable=AsyncMock
        )
        mock = patcher.start()
        mock.return_value = return_value
        self.addCleanup(patcher.stop)
        return mock

    # --- service_alerts (uses fetch_value) ---

    async def test_service_alerts_calls_correct_endpoint(self):
        mock = await self._mock_fetch_value(
            {"Status": 1, "AffectedSegments": [], "Message": []}
        )
        result = await self.train.service_alerts()
        mock.assert_called_once_with("TrainServiceAlerts")
        self.assertIn("Status", result)
        self.assertIn("AffectedSegments", result)
        self.assertIn("Message", result)

    async def test_service_alerts_status_value(self):
        mock = await self._mock_fetch_value(
            {
                "Status": 2,
                "AffectedSegments": [
                    {"Line": "NEL", "Direction": "Both", "Stations": "NE1,NE3"}
                ],
                "Message": [],
            }
        )
        result = await self.train.service_alerts()
        mock.assert_called_once_with("TrainServiceAlerts")
        self.assertEqual(result["Status"], 2)
        self.assertEqual(len(result["AffectedSegments"]), 1)

    async def test_service_alerts_normal_status(self):
        await self._mock_fetch_value(
            {"Status": 1, "AffectedSegments": [], "Message": []}
        )
        result = await self.train.service_alerts()
        self.assertEqual(result["Status"], 1)

    # --- facilities_maintenance (uses fetch) ---

    async def test_facilities_maintenance_calls_correct_endpoint(self):
        mock = await self._mock_fetch(
            [
                {
                    "Line": "NEL",
                    "StationCode": "NE12",
                    "StationName": "Serangoon",
                    "LiftID": "B1L01",
                    "LiftDesc": "Exit B Street level - Concourse",
                }
            ]
        )
        result = await self.train.facilities_maintenance()
        mock.assert_called_once_with("v2/FacilitiesMaintenance")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["Line"], "NEL")

    async def test_facilities_maintenance_handles_empty(self):
        await self._mock_fetch([])
        result = await self.train.facilities_maintenance()
        self.assertEqual(result, [])

    # --- station_crowd_density_realtime (uses fetch) ---

    async def test_realtime_calls_correct_endpoint_with_param(self):
        mock = await self._mock_fetch([{"Station": "EW1", "CrowdLevel": "l"}])
        result = await self.train.station_crowd_density_realtime("EWL")
        mock.assert_called_once_with("PCDRealTime", query_params={"TrainLine": "EWL"})
        self.assertEqual(len(result), 1)

    async def test_realtime_returns_multiple_stations(self):
        await self._mock_fetch(
            [
                {"Station": "EW1", "CrowdLevel": "l"},
                {"Station": "EW2", "CrowdLevel": "m"},
            ]
        )
        result = await self.train.station_crowd_density_realtime("EWL")
        self.assertEqual(len(result), 2)

    async def test_realtime_handles_empty(self):
        await self._mock_fetch([])
        result = await self.train.station_crowd_density_realtime("EWL")
        self.assertEqual(result, [])

    # --- station_crowd_density_forecast (uses fetch) ---

    async def test_forecast_calls_correct_endpoint_with_param(self):
        mock = await self._mock_fetch([{"Station": "NS1", "CrowdLevel": "l"}])
        result = await self.train.station_crowd_density_forecast("NSL")
        mock.assert_called_once_with("PCDForecast", query_params={"TrainLine": "NSL"})
        self.assertEqual(len(result), 1)

    async def test_forecast_handles_all_crowd_levels(self):
        await self._mock_fetch(
            [
                {"Station": "CC1", "CrowdLevel": "l"},
                {"Station": "CC2", "CrowdLevel": "m"},
                {"Station": "CC3", "CrowdLevel": "h"},
                {"Station": "CC4", "CrowdLevel": "NA"},
            ]
        )
        result = await self.train.station_crowd_density_forecast("CCL")
        self.assertEqual(len(result), 4)
        levels = {r["CrowdLevel"] for r in result}
        self.assertEqual(levels, {"l", "m", "h", "NA"})


class TestTaxi(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.taxi = Taxi(api_key="test-key")

    async def _mock_fetch(self, return_value):
        patcher = patch.object(self.taxi.lta_api, "fetch", new_callable=AsyncMock)
        mock = patcher.start()
        mock.return_value = return_value
        self.addCleanup(patcher.stop)
        return mock

    async def test_availability_calls_correct_endpoint(self):
        mock = await self._mock_fetch([{"Latitude": 1.35667, "Longitude": 103.93314}])
        result = await self.taxi.availability()
        mock.assert_called_once_with("Taxi-Availability")
        self.assertEqual(len(result), 1)
        self.assertIn("Latitude", result[0])
        self.assertIn("Longitude", result[0])

    async def test_availability_handles_empty(self):
        await self._mock_fetch([])
        result = await self.taxi.availability()
        self.assertEqual(result, [])

    async def test_stands_calls_correct_endpoint(self):
        mock = await self._mock_fetch([{"TaxiCode": "A01", "Latitude": 1.30398}])
        result = await self.taxi.stands()
        mock.assert_called_once_with("TaxiStands")
        self.assertEqual(len(result), 1)

    async def test_stands_handles_empty(self):
        await self._mock_fetch([])
        result = await self.taxi.stands()
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()


class TestTraffic(unittest.IsolatedAsyncioTestCase):
    """Verify Traffic methods call fetch() with correct endpoints."""

    def setUp(self):
        from ltasg.traffic import Traffic

        self.traffic = Traffic(api_key="test-key")

    async def _mock_fetch(self, return_value):
        from unittest.mock import AsyncMock, patch

        patcher = patch.object(self.traffic.lta_api, "fetch", new_callable=AsyncMock)
        mock = patcher.start()
        mock.return_value = return_value
        self.addCleanup(patcher.stop)
        return mock

    async def _test_endpoint(self, method_name, endpoint_key, sample_record=None):
        """Helper: mock fetch, call method, verify endpoint."""
        sample = sample_record or {"a": 1}
        mock = await self._mock_fetch([sample])
        method = getattr(self.traffic, method_name)
        result = await method()
        expected_endpoint = self.traffic._svc[endpoint_key]
        mock.assert_called_once_with(expected_endpoint)
        self.assertEqual(len(result), 1)

    async def test_carpark_availability(self):
        await self._test_endpoint(
            "carpark_availability",
            "CARPARK_AVAILABILITY",
            {"CarParkID": "1", "AvailableLots": 352},
        )

    async def test_estimated_travel_times(self):
        await self._test_endpoint(
            "estimated_travel_times",
            "ESTIMATED_TRAVEL_TIMES",
            {"Name": "AYE", "EstTime": 2},
        )

    async def test_faulty_traffic_lights(self):
        await self._test_endpoint(
            "faulty_traffic_lights", "FAULTY_TRAFFIC_LIGHTS", {"AlarmID": "GL703034136"}
        )

    async def test_planned_road_openings(self):
        await self._test_endpoint(
            "planned_road_openings",
            "PLANNED_ROAD_OPENINGS",
            {"EventID": "RMAPP-201603-0900"},
        )

    async def test_approved_road_works(self):
        await self._test_endpoint(
            "approved_road_works",
            "APPROVED_ROAD_WORKS",
            {"EventID": "RMAPP-201512-0217"},
        )

    async def test_traffic_images(self):
        await self._test_endpoint(
            "traffic_images",
            "TRAFFIC_IMAGES",
            {"CameraID": "5795", "ImageLink": "https://..."},
        )

    async def test_traffic_incidents(self):
        await self._test_endpoint(
            "traffic_incidents",
            "TRAFFIC_INCIDENTS",
            {"Type": "Vehicle breakdown", "Message": "..."},
        )

    async def test_traffic_speed_bands(self):
        await self._test_endpoint(
            "traffic_speed_bands", "TRAFFIC_SPEED_BANDS", {"LinkID": 1, "SpeedBand": 2}
        )

    async def test_vms(self):
        await self._test_endpoint("vms", "VMS", {"EquipmentID": "amvms_v9104"})

    async def test_traffic_flow(self):
        await self._test_endpoint(
            "traffic_flow", "TRAFFIC_FLOW", {"Link": "https://..."}
        )

    async def test_flood_alerts(self):
        await self._test_endpoint(
            "flood_alerts",
            "FLOOD_ALERTS",
            {"alertId": "2.49.0.0", "event": "Flood", "severity": "Minor"},
        )

    async def test_empty_response(self):
        await self._mock_fetch([])
        result = await self.traffic.carpark_availability()
        self.assertEqual(result, [])


class TestBusAdditional(unittest.IsolatedAsyncioTestCase):
    """Additional Bus tests for newly implemented methods."""

    def setUp(self):
        from ltasg.transport.bus import Bus

        self.bus = Bus(api_key="test-key")

    async def _mock_fetch(self, return_value):
        from unittest.mock import AsyncMock, patch

        patcher = patch.object(self.bus.lta_api, "fetch", new_callable=AsyncMock)
        mock = patcher.start()
        mock.return_value = return_value
        self.addCleanup(patcher.stop)
        return mock

    async def test_passenger_volume_by_bus_stops(self):
        mock = await self._mock_fetch([{"Link": "https://..."}])
        result = await self.bus.passenger_volume_by_bus_stops()
        mock.assert_called_once_with("PV/Bus", query_params=None)
        self.assertEqual(len(result), 1)
        self.assertIn("Link", result[0])

    async def test_passenger_volume_by_bus_stops_with_date(self):
        mock = await self._mock_fetch([{"Link": "https://..."}])
        result = await self.bus.passenger_volume_by_bus_stops(date="202605")
        mock.assert_called_once_with("PV/Bus", query_params={"Date": "202605"})
        self.assertEqual(len(result), 1)

    async def test_passenger_volume_by_od_bus_stops(self):
        mock = await self._mock_fetch([{"Link": "https://..."}])
        result = await self.bus.passenger_volume_by_od_bus_stops()
        mock.assert_called_once_with("PV/ODBus", query_params=None)
        self.assertIn("Link", result[0])

    async def test_planned_bus_routes(self):
        mock = await self._mock_fetch([{"ServiceNo": "107M"}])
        result = await self.bus.planned_bus_routes()
        mock.assert_called_once_with("PlannedBusRoutes")
        self.assertEqual(result[0]["ServiceNo"], "107M")


class TestTrainAdditional(unittest.IsolatedAsyncioTestCase):
    """Additional Train tests for newly implemented methods."""

    def setUp(self):
        from ltasg.transport.train import Train

        self.train = Train(api_key="test-key")

    async def _mock_fetch(self, return_value):
        from unittest.mock import AsyncMock, patch

        patcher = patch.object(self.train.lta_api, "fetch", new_callable=AsyncMock)
        mock = patcher.start()
        mock.return_value = return_value
        self.addCleanup(patcher.stop)
        return mock

    async def test_passenger_volume_by_od_train_stations(self):
        mock = await self._mock_fetch([{"Link": "https://..."}])
        result = await self.train.passenger_volume_by_od_train_stations()
        mock.assert_called_once_with("PV/ODTrain", query_params=None)
        self.assertIn("Link", result[0])

    async def test_passenger_volume_by_od_train_stations_with_date(self):
        mock = await self._mock_fetch([{"Link": "https://..."}])
        await self.train.passenger_volume_by_od_train_stations(date="202605")
        mock.assert_called_once_with("PV/ODTrain", query_params={"Date": "202605"})

    async def test_passenger_volume_by_train_stations(self):
        mock = await self._mock_fetch([{"Link": "https://..."}])
        result = await self.train.passenger_volume_by_train_stations()
        mock.assert_called_once_with("PV/Train", query_params=None)
        self.assertIn("Link", result[0])


class TestOther(unittest.IsolatedAsyncioTestCase):
    """Test Other (miscellaneous) API methods."""

    def setUp(self):
        from ltasg.other import Other

        self.other = Other(api_key="test-key")

    async def _mock_fetch(self, return_value):
        from unittest.mock import AsyncMock, patch

        patcher = patch.object(self.other.lta_api, "fetch", new_callable=AsyncMock)
        mock = patcher.start()
        mock.return_value = return_value
        self.addCleanup(patcher.stop)
        return mock

    async def test_bicycle_parking(self):
        mock = await self._mock_fetch([{"Description": "Bus Stop 43267"}])
        result = await self.other.bicycle_parking(1.364897, 103.766094)
        mock.assert_called_once_with(
            "BicycleParkingv2",
            query_params={"Lat": 1.364897, "Long": 103.766094, "Dist": 0.5},
        )
        self.assertEqual(len(result), 1)

    async def test_bicycle_parking_custom_dist(self):
        mock = await self._mock_fetch([{"Description": "Test"}])
        await self.other.bicycle_parking(1.3, 103.8, dist=1.0)
        mock.assert_called_once_with(
            "BicycleParkingv2",
            query_params={"Lat": 1.3, "Long": 103.8, "Dist": 1.0},
        )

    async def test_geospatial_whole_island(self):
        mock = await self._mock_fetch([{"Link": "https://..."}])
        result = await self.other.geospatial_whole_island("ArrowMarking")
        mock.assert_called_once_with(
            "GeospatialWholeIsland",
            query_params={"ID": "ArrowMarking"},
        )
        self.assertIn("Link", result[0])

    async def test_ev_charging_points(self):
        mock = await self._mock_fetch([{"address": "123 Road", "name": "Station"}])
        result = await self.other.ev_charging_points("123456")
        mock.assert_called_once_with(
            "EVChargingPoints",
            query_params={"PostalCode": "123456"},
            records_key="value",
        )
        self.assertEqual(result[0]["address"], "123 Road")

    async def test_ev_charging_points_batch(self):
        mock = await self._mock_fetch([{"Link": "https://..."}])
        result = await self.other.ev_charging_points_batch()
        mock.assert_called_once_with("EVCBatch")
        self.assertIn("Link", result[0])

    async def test_empty_response(self):
        await self._mock_fetch([])
        result = await self.other.bicycle_parking(1.3, 103.8)
        self.assertEqual(result, [])
