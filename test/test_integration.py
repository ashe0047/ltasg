"""Integration tests for ltasg SDK — mock aiohttp at module level."""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from unittest.mock import patch, AsyncMock, MagicMock
from ltasg.api import LTADataMall, LTADataMallHTTPError
from ltasg.constants import DEFAULT_BASE_URL


MODULE = "ltasg.api"


def _make_mock_session(*, status=200, json_data=None, json_side_effect=None):
    """Create a mock aiohttp ClientSession with controlled responses."""
    mock_resp = MagicMock()
    mock_resp.ok = status == 200
    mock_resp.status = status
    if json_side_effect:
        mock_resp.json = AsyncMock(side_effect=json_side_effect)
    else:
        mock_resp.json = AsyncMock(return_value=json_data or {})

    mock_get_inner = MagicMock()
    mock_get_inner.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_get_inner.__aexit__ = AsyncMock(return_value=None)

    mock_session = MagicMock()
    mock_session.get.return_value = mock_get_inner
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)
    return mock_session


class TestFetchResponseShapes(unittest.IsolatedAsyncioTestCase):
    """fetch() always returns a flat list of records."""

    def setUp(self):
        self.api = LTADataMall(DEFAULT_BASE_URL, "test-key")

    async def test_services_key_extracted_into_flat_list(self):
        """BusArrival 'Services' → flattened into list records."""
        session = _make_mock_session(
            json_data={"Services": [{"ServiceNo": "15"}], "BusStopCode": "83139"}
        )
        with patch(f"{MODULE}.ClientSession", return_value=session):
            result = await self.api.fetch("v3/BusArrival", records_key="Services")
        self.assertEqual(result, [{"ServiceNo": "15"}])

    async def test_standard_value_array_becomes_flat_list(self):
        """Standard API with value array → flat list."""
        session = _make_mock_session(
            json_data={"value": [{"a": 1}, {"a": 2}]}
        )
        with patch(f"{MODULE}.ClientSession", return_value=session):
            result = await self.api.fetch("BusServices")
        self.assertEqual(result, [{"a": 1}, {"a": 2}])

    async def test_empty_response_returns_empty_list(self):
        """No buses / empty response → []."""
        session = _make_mock_session(json_data={"value": []})
        with patch(f"{MODULE}.ClientSession", return_value=session):
            result = await self.api.fetch("Taxi-Availability")
        self.assertEqual(result, [])

    async def test_no_value_key_returns_empty_list(self):
        """Response with neither Services nor value → fallback to []."""
        session = _make_mock_session(json_data={})
        with patch(f"{MODULE}.ClientSession", return_value=session):
            result = await self.api.fetch("SomeEndpoint")
        self.assertEqual(result, [])


class TestFetchValue(unittest.IsolatedAsyncioTestCase):
    """fetch_value() returns the value dict directly."""

    def setUp(self):
        self.api = LTADataMall(DEFAULT_BASE_URL, "test-key")

    async def test_fetch_value_returns_dict(self):
        """TrainServiceAlerts → value dict."""
        session = _make_mock_session(
            json_data={"value": {"Status": 1, "AffectedSegments": [], "Message": []}}
        )
        with patch(f"{MODULE}.ClientSession", return_value=session):
            result = await self.api.fetch_value("TrainServiceAlerts")
        self.assertEqual(result, {"Status": 1, "AffectedSegments": [], "Message": []})

    async def test_fetch_value_with_query_params(self):
        """Fetch value with query params."""
        session = _make_mock_session(
            json_data={"value": {"Status": 2, "AffectedSegments": []}}
        )
        with patch(f"{MODULE}.ClientSession", return_value=session):
            result = await self.api.fetch_value(
                "TrainServiceAlerts", query_params={"param": "val"}
            )
        self.assertEqual(result["Status"], 2)


class TestFetchErrorHandling(unittest.IsolatedAsyncioTestCase):
    """HTTP errors throw typed exceptions."""

    def setUp(self):
        self.api = LTADataMall(DEFAULT_BASE_URL, "test-key")

    async def _assert_http_error(self, status, endpoint):
        session = _make_mock_session(status=status, json_data={})
        with patch(f"{MODULE}.ClientSession", return_value=session):
            with self.assertRaises(LTADataMallHTTPError) as ctx:
                await self.api.fetch(endpoint)
        self.assertEqual(ctx.exception.status, status)
        self.assertIn(endpoint, str(ctx.exception))

    async def test_404_raises(self):
        await self._assert_http_error(404, "BadEndpoint")

    async def test_500_raises(self):
        await self._assert_http_error(500, "Broken")

    async def test_fetch_value_404_raises(self):
        session = _make_mock_session(status=404, json_data={})
        with patch(f"{MODULE}.ClientSession", return_value=session):
            with self.assertRaises(LTADataMallHTTPError) as ctx:
                await self.api.fetch_value("BadEndpoint")
        self.assertEqual(ctx.exception.status, 404)


class TestFetchPagination(unittest.IsolatedAsyncioTestCase):
    """fetch() auto-paginates into a single flat list."""

    def setUp(self):
        self.api = LTADataMall(DEFAULT_BASE_URL, "test-key")

    async def test_two_pages_flattened(self):
        """500 records + 100 records → flat list of 600."""
        page1 = [{"i": i} for i in range(500)]
        page2 = [{"i": i} for i in range(100)]
        session = _make_mock_session(json_side_effect=[
            {"value": page1},
            {"value": page2},
        ])
        with patch(f"{MODULE}.ClientSession", return_value=session):
            result = await self.api.fetch("BusRoutes")
        self.assertEqual(len(result), 600)
        self.assertEqual(result[0]["i"], 0)
        self.assertEqual(result[599]["i"], 99)  # last item of page2

    async def test_single_page_direct(self):
        """< 500 records → no extra HTTP calls."""
        page = [{"i": i} for i in range(50)]
        session = _make_mock_session(json_data={"value": page})
        with patch(f"{MODULE}.ClientSession", return_value=session):
            result = await self.api.fetch("BusRoutes")
        self.assertEqual(len(result), 50)

    async def test_exactly_500_triggers_next_page(self):
        """500 records + empty → flat list of 500."""
        page1 = [{"i": i} for i in range(500)]
        session = _make_mock_session(json_side_effect=[
            {"value": page1},
            {"value": []},
        ])
        with patch(f"{MODULE}.ClientSession", return_value=session):
            result = await self.api.fetch("BusRoutes")
        self.assertEqual(len(result), 500)

    async def test_paginates_with_query_params(self):
        """Pagination preserves query params properly."""
        page1 = [{"i": i} for i in range(500)]
        page2 = [{"i": i} for i in range(50)]
        session = _make_mock_session(json_side_effect=[
            {"value": page1},
            {"value": page2},
        ])
        with patch(f"{MODULE}.ClientSession", return_value=session):
            result = await self.api.fetch("BusRoutes", query_params={"ServiceNo": "63"})
        self.assertEqual(len(result), 550)


if __name__ == "__main__":
    unittest.main()
