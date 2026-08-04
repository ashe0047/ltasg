"""Core HTTP client for the LTA DataMall API."""

from urllib.parse import urlencode

from aiohttp import ClientConnectionError, ClientSession, ClientTimeout


class LTADataMallError(Exception):
    """Base exception for LTA DataMall API errors."""

    pass


class LTADataMallHTTPError(LTADataMallError):
    """HTTP-level error including the endpoint and status code."""

    def __init__(self, endpoint: str, status: int) -> None:
        self.endpoint = endpoint
        self.status = status
        super().__init__(f"Error calling API for {endpoint} with status code: {status}")


class LTADataMall:
    """Low-level HTTP client wrapping the LTA DataMall REST API.

    Two retrieval methods:

    ``fetch(endpoint)``
        Returns a **flat list** of record dicts.  Auto-paginates 500-record
        pages.  The default ``records_key`` is ``"value"``; override for
        APIs such as Bus Arrival v3 where the key is ``"Services"``.

    ``fetch_value(endpoint)``
        Returns the **single dict** inside ``"value"``.  Designed for APIs
        such as Train Service Alerts (``{"value": {Status, ...}}``).

    Usage pattern (preferred — session is auto-closed)::

        async with LTADataMall(url, key) as client:
            records = await client.fetch("BusServices")

    Simple call (session leaked on GC — call ``close()`` manually)::

        client = LTADataMall(url, key)
        records = await client.fetch("BusServices")
    """

    RECORD_LIMIT = 500
    REQUEST_TIMEOUT_SECONDS = 30

    def __init__(self, base_url: str, api_key: str) -> None:
        self.BASE_URL = base_url
        self.API_KEY = api_key
        self._session = None
        self.HEADERS = {
            "Accept": "application/json",
            "AccountKey": self.API_KEY,
        }

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------

    async def _get_session(self):
        """Get the shared aiohttp ClientSession, creating it lazily."""
        if self._session is None:
            self._session = ClientSession()
        return self._session

    async def close(self):
        """Close the shared HTTP session and release connections."""
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def fetch(
        self, endpoint: str, query_params: dict = None, records_key: str = "value"
    ):
        """Fetch an endpoint and return a flat list of record dicts.

        Args:
            endpoint: API path (e.g. ``"v3/BusArrival"``).
            query_params: Optional query-string parameters.
            records_key: JSON key holding the record array
                (default ``"value"``; use ``"Services"`` for Bus Arrival v3).

        Returns a flat list of record dicts.  Auto-paginates when the
        server returns 500-record pages.
        """
        url = self._build_url(endpoint, query_params)
        has_query = bool(query_params)
        skip_count = 0
        all_records = []

        while True:
            paginated_url = self._paginate(url, skip_count, has_query)
            curr_data = await self._request(paginated_url, endpoint)

            records = curr_data.get(records_key, [])

            if isinstance(records, list):
                all_records.extend(records)
                if len(records) < self.RECORD_LIMIT:
                    break
                skip_count += self.RECORD_LIMIT
            else:
                all_records.append(records)
                break

        return all_records

    async def fetch_value(self, endpoint: str, query_params: dict = None):
        """Fetch an endpoint where ``"value"`` is a single dict.

        Returns the ``value`` dict directly (not wrapped in a list).
        Use for APIs such as Train Service Alerts (Status, AffectedSegments).
        """
        url = self._build_url(endpoint, query_params)
        curr_data = await self._request(url, endpoint)
        return curr_data["value"]

    # ------------------------------------------------------------------
    # Internal: shared HTTP infrastructure
    # ------------------------------------------------------------------

    async def _request(self, url: str, endpoint: str):
        """Raw HTTP GET with a 30-second timeout.

        Returns parsed JSON.  Raises ``LTADataMallHTTPError`` on non-2xx
        responses and re-raises ``ClientConnectionError`` on network errors.
        """
        timeout = ClientTimeout(total=self.REQUEST_TIMEOUT_SECONDS)
        session = await self._get_session()
        try:
            async with session.get(
                url, headers=self.HEADERS, timeout=timeout
            ) as response:
                if not response.ok:
                    raise LTADataMallHTTPError(endpoint, response.status)
                return await response.json()
        except ClientConnectionError:
            raise

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_url(self, endpoint: str, query_params: dict = None) -> str:
        """Construct the URL with optional query parameters."""
        url = f"{self.BASE_URL}{endpoint}"
        if query_params:
            url += "?" + urlencode(query_params)
        return url

    @staticmethod
    def _paginate(url: str, skip_count: int, has_query: bool = False) -> str:
        """Append the ``$skip=N`` operator for the given page."""
        if skip_count == 0:
            return url
        sep = "&" if has_query else "?"
        return f"{url}{sep}$skip={skip_count}"
