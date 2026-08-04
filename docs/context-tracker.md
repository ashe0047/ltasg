 # LTA DataMall SDK — Audit & Alignment Tracker

 ## Session: 2026-07-18 — Full audit of ltasg SDK v0.0.6 against LTA DataMall API User Guide v6.8 (21 Apr 2026)

 **Source document:** `LTA_DataMall_API_User_Guide.pdf` (Version 6.8, 21 Apr 2026, 80 pages)
 **SDK version audited:** v0.0.6.post2
 **SDK location:** `/Users/ashe0047/Workspace/codebases/apps/python-packages/ltasg`

 ## Audit methodology

 Cross-referenced every API endpoint in the PDF (30 datasets across 4 categories) against the SDK's current constants, API client, and service classes. Findings are grouped by severity.

 ## 1. Critical Issues

 ### 1.1 Base URL uses HTTP instead of HTTPS
 - **SDK main.py:** `http://datamall2.mytransport.sg/ltaodataservice/`
 - **README example:** `"https://http://datamall2.mytransport.sg/ltaodataservice/"` (broken double protocol)
 - **PDF v6.0 (Aug 2024):** "HTTPS is now supported for all APIs."
 - **Impact:** Default config uses unencrypted HTTP. The test file and main.py both hardcode HTTP. Need to migrate to `https://`.
 - **Note:** The PDF says "supported" not "required", but HTTPS should be the default.

 ## 2. Existing API Enhancements Missing

 ### 2.1 Bus Services — missing optional ServiceNo filter (v6.8, Apr 2026)
 - **PDF §2.2:** Added optional `ServiceNo` query param to filter by bus service number.
 - **SDK:** `bus.services()` calls `/BusServices` with no query params, returns all services.
 - **Needed:** Add optional `service_no` parameter to `Bus.services()`.

 ### 2.2 Bus Stops — missing optional BusStopCode filter (v6.8, Apr 2026)
 - **PDF §2.4:** Added optional `BusStopCode` query param to filter by bus stop code.
 - **SDK:** `bus.stops()` calls `/BusStops` with no query params, returns all stops.
 - **Needed:** Add optional `bus_stop_code` parameter to `Bus.stops()`.

 ### 2.3 Station Crowd Density APIs — commented out (renamed v6.2, Nov 2024)
 - **PDF §2.24–2.25:** Renamed from "Platform Crowd Density" to "Station Crowd Density Real Time" and "Station Crowd Density Forecast" (URLs unchanged: `/PCDRealTime`, `/PCDForecast`).
 - **SDK train.py:** Both methods are commented out with note "API currently results in Error 404 not found". Needs re-testing — TEL data was added in v6.2.
 - **Needed:** Re-enable and test. Expects a `TrainLine` query param.

 ### 2.4 Train Service Alerts — minor revision (v6.6, Jan 2026)
 - **PDF §2.11:** "Minor revisions to Train Service Alerts API response."
 - **SDK:** `train.service_alerts()` returns `data['value']`. Need to verify current response shape against the live API.

 ### 2.5 Facilities Maintenance — v2 launched (v6.3, Jul 2025)
 - **PDF §2.23:** URL: `/v2/FacilitiesMaintenance`. Returns lift maintenance info per MRT station (Line, StationCode, StationName, LiftID, LiftDesc).
 - **SDK:** Not implemented.

 ### 2.6 Traffic Speed Bands — v4 launched (v6.4, Jul 2025)
 - **PDF §2.19:** URL: `/v4/TrafficSpeedBands`. Updated LinkID and RoadCategory values.
 - **SDK:** Not implemented.

 ## 3. Missing API Categories (Not Implemented)

 ### 3.1 Traffic APIs (11 total in spec, 0 in SDK)
 | # | API | PDF § | URL Endpoint |
 |---|-----|-------|-------------|
 | 1 | Carpark Availability | 2.12 | `/CarParkAvailabilityv2` |
 | 2 | Estimated Travel Times | 2.13 | `/EstTravelTimes` |
 | 3 | Faulty Traffic Lights | 2.14 | `/FaultyTrafficLights` |
 | 4 | Planned Road Openings | 2.15 | `/RoadOpenings` |
 | 5 | Approved Road Works | 2.16 | `/RoadWorks` |
 | 6 | Traffic Images (v2) | 2.17 | `/Traffic-Imagesv2` |
 | 7 | Traffic Incidents | 2.18 | `/TrafficIncidents` |
 | 8 | Traffic Speed Bands (v4) | 2.19 | `/v4/TrafficSpeedBands` |
 | 9 | VMS / EMAS | 2.20 | `/VMS` |
 | 10 | Traffic Flow | 2.26 | `/TrafficFlow` |
 | 11 | Flood Alerts | 2.30 | `/PubFloodAlerts` |

 ### 3.2 Public Transport APIs (15 total in spec, 8 in SDK)
 | # | API | PDF § | URL Endpoint |
 |---|-----|-------|-------------|
 | 1 | Passenger Volume by Bus Stops | 2.5 | `/PV/Bus` |
 | 2 | Passenger Volume by OD Bus Stops | 2.6 | `/PV/ODBus` |
 | 3 | Passenger Volume by OD Train Stations | 2.7 | `/PV/ODTrain` |
 | 4 | Passenger Volume by Train Stations | 2.8 | `/PV/Train` |
 | 5 | Facilities Maintenance (v2) | 2.23 | `/v2/FacilitiesMaintenance` |
 | 6 | Station Crowd Density Real Time | 2.24 | `/PCDRealTime` |
 | 7 | Station Crowd Density Forecast | 2.25 | `/PCDForecast` |
 | 8 | Planned Bus Routes | 2.27 | `/PlannedBusRoutes` |

 ### 3.3 Active Mobility & Geospatial & EV APIs
 | # | API | PDF § | URL Endpoint |
 |---|-----|-------|-------------|
 | 1 | Bicycle Parking (v2) | 2.21 | `/BicycleParkingv2` |
 | 2 | Geospatial Whole Island | 2.22 | `/GeospatialWholeIsland` |
 | 3 | EV Charging Points | 2.28 | `/EVChargingPoints` |
 | 4 | EV Charging Points Batch | 2.29 | `/EVCBatch` |

 ## 4. Code Quality & Structural Issues

 ### 4.1 `LTADataMall.fetch()` pagination logic needs review
 - The current `$skip` pagination logic is fragile. Python f-string `$skip` interpolation is fragile.
 - Bus Arrival returns `{"Services": [...]}` (no `value` key), which bypasses pagination via the `"Services" in curr_data` check — correct.
 - Passenger Volume APIs return a `Link` download URL (not paginated), not handled.

 ### 4.2 `transform_data` imports from incorrect module path
 - `helpers/helpers.py` defines `transform_data`, but for real usage the import path via `package.helpers.helpers` is redundant. Consider flattening.

 ### 4.3 Missing type annotations
 - Many methods lack proper type hints beyond basic primitives.

 ### 4.4 Test file uses `from transport.bus import Bus` (relative import)
 - Tests use `from transport.bus import Bus` but the actual package layout is `src/ltasg/transport/bus.py`. Tests will need fixing if the package structure changes.

 ### 4.5 `bus.stop_services()` not tested
 - `test_bus()` tests arrival, services, routes, and stops but not `stop_services`.

 ## 5. README & Docs Issues

 ### 5.1 Broken URL in README
 - `"https://http://datamall2.mytransport.sg/ltaodataservice/"` — double protocol prefix.
 - Should be `"https://datamall2.mytransport.sg/ltaodataservice/"`.

 ### 5.2 Stale feature list
 - README mentions "Platform Crowd Density Realtime" and "Platform Crowd Density Forecast" (renamed in v6.2, Nov 2024).
 - Lists only 2 Bus features, missing all other implemented traffic/transport methods.

 ## Summary

 | Category | Count |
 |----------|-------|
 | APIs fully implemented | 7 of 30 (23%) |
 | APIs partially implemented (needs update) | 2 (Bus Services, Bus Stops) |
 | APIs commented out (needs re-enable) | 2 (Station Crowd Density) |
 | APIs missing | 21 (70%) |
 | Critical URL bugs | 1 (HTTP vs HTTPS) |
 | Docs issues | 2 (README URL + feature list) |
 | Code quality | 3 items (pagination, imports, types) |
 | Test gaps | 2 (stop_services, Station Crowd Density, v2 APIs) |

## — Second-round findings (2026-07-18) —

### Additional findings after deeper code inspection

#### 1. Bus Arrival endpoint is stale: uses v2, not v3

- **constants.py** line: `"ARRIVAL": "BusArrivalv2"`
- **PDF §2.1**: URL is `https://datamall2.mytransport.sg/ltaodataservice/v3/BusArrival`
- The SDK still calls the v2 endpoint `BusArrivalv2`. The v3 endpoint was introduced in v6.0 (Aug 2024). The v3 endpoint serves the `Monitored` attribute. The SDK may or may not get `Monitored` from the v2 endpoint depending on backward compatibility. Needs migration to `v3/BusArrival`.

#### 2. Test suite is completely broken — cannot instantiate

- `test/test.py` line 11–13: `Bus(api_key=api_key)` but the constructor requires `(self, base_url, api_key)`.
- Python raises `TypeError: __init__() missing 1 required positional argument: 'base_url'` on class attribute evaluation.
- This means **zero tests have been runnable since the constructor signature was last changed**. All 3 service constructors share the same problem.

#### 3. `train.service_alerts()` return value is broken

- `train.py` line 15: `return data['value']`
- But `LTADataMall.fetch()` (except for Bus Arrival) returns a **list** of response dicts, not a single dict.
- So `data` is a list (e.g. `[{"value": [...]}]`), and `data['value']` raises `TypeError: list indices must be integers or slices, not str`.
- Needs `return transform_data(data)` (or `data[0]['value']` for the single-page case).

#### 4. Station Crowd Density commented-out code lacks mandatory `TrainLine` param

- `train.py` (commented block): calls `fetch(url)` with **no query params**.
- PDF §2.24–2.25: `TrainLine` is a **Mandatory** parameter for both realtime and forecast APIs.
- The 404 error the SDK originally encountered was likely due to the missing parameter, not the endpoint being unavailable.

#### 5. `arrival()` method type annotation mismatch

- `bus.py` line 9: `bus_no: int`
- Test passes `"63M"` (string). The `ServiceNo` parameter in the API is actually an alphanumeric string, not an int.

#### 6. `LTADataMall.fetch()` response handling — bus stop `stop_services` is expensive

- `bus.stop_services()` fetches ALL bus routes (potentially thousands of records across multiple pages), then filters client-side. There is no server-side filter for routes by stop code. This is an architectural limitation, but should be documented.

#### 7. PDF Response-shape nuance: some APIs return `Link`-based download URLs

- APIs that return a download link (Passenger Volume PV/*, Traffic Flow, Geospatial Whole Island, EV Charging Points Batch) return `{"value": [{"Link": "..."}]}` — a single-element list, not paginated records.
- The current `fetch()` pagination handles this correctly (the single-element list has length 1 < 500 so it breaks) but the result is `[{"value": [{"Link": "..."}]}]` which the caller would need to handle specially.
- If these APIs are ever implemented, they need a different response-processing path.

#### 8. No mechanism for API version discovery or graceful degradation

- The SDK hardcodes endpoint paths with no way to query API version or detect breaking changes. All version bumps (v3 BusArrival, v4 TrafficSpeedBands, v2 FacilitiesMaintenance, v2 BicycleParking, v2 Traffic Images) require code changes in constants.py.

## Final consolidated severity ranking

| Priority | Finding | File |
|----------|---------|------|
| **BLOCKER** | Tests cannot instantiate — broken constructor call | test/test.py:11-13 |
| **BLOCKER** | `train.service_alerts()` returns wrong type | src/ltasg/transport/train.py:15 |
| **BLOCKER** | Base URL uses HTTP, should default to HTTPS | main.py, README.md |
| **CRITICAL** | Bus Arrival endpoint uses v2 instead of v3 | src/ltasg/constants.py |
| **HIGH** | 21 of 30 APIs not implemented | — |
| **HIGH** | Station Crowd Density uses wrong constant name | src/ltasg/constants.py (comment) |
| **MEDIUM** | Bus Services missing optional `ServiceNo` param | src/ltasg/transport/bus.py |
| **MEDIUM** | Bus Stops missing optional `BusStopCode` param | src/ltasg/transport/bus.py |
| **MEDIUM** | Station Crowd Density needs re-enable + `TrainLine` param | src/ltasg/transport/train.py |
| **MEDIUM** | README URL doubled protocol | README.md |
| **LOW** | `bus_no: int` should be `bus_no: str` | src/ltasg/transport/bus.py:9 |
| **LOW** | Missing type annotations across SDK | all source files |
| **LOW** | `stop_services` untested and expensive | test/test.py |

## — Blocker fixes applied (2026-07-18) —

### Changes made

#### B1: Test suite broken constructor calls
- Added `DEFAULT_BASE_URL = "https://datamall2.mytransport.sg/ltaodataservice/"` to `constants.py`
- Updated `Transport.__init__`, `Bus.__init__`, `Train.__init__`, `Taxi.__init__` to accept optional `base_url=DEFAULT_BASE_URL, api_key=None`
- Updated `test/test.py` imports to use `sys.path` + `ltasg.transport.*` (src-layout compatible)
- **Status: FIXED** — `Bus(api_key=...)`, `Train(api_key=...)`, `Taxi(api_key=...)` all work with defaults

#### B2: train.service_alerts() broken return type
- Changed from `return data['value']` to `return transform_data(data)`
- Updated test assertion from `service_alerts_data['Status']` to `service_alerts_data[0]['Status']`
- **Status: FIXED** — Now correctly handles paginated list from `fetch()`

#### B3: Base URL uses HTTP
- `DEFAULT_BASE_URL` set to `https://datamall2.mytransport.sg/ltaodataservice/`
- `main.py` updated to use default via `Bus(api_key=...)`
- `README.md` updated to show `Bus(api_key=api_key)` pattern with HTTPS default
- **Status: FIXED**

### Additional improvements bundled with blocker fixes

- **Bus Arrival endpoint** updated from `BusArrivalv2` to `v3/BusArrival` (was CRITICAL, now fixed)
- **`bus.services()`** now accepts optional `service_no` param (v6.8 filter)
- **`bus.stops()`** now accepts optional `bus_stop_code` param (v6.8 filter)
- **`train.station_crowd_density_realtime()`** re-enabled with mandatory `TrainLine` param
- **`train.station_crowd_density_forecast()`** re-enabled with mandatory `TrainLine` param
- **`FACILITIES_MAINTENANCE`** endpoint added to constants (v2) — ready for implementation
- **`bus_no` type hint** corrected from `int` to `str`
- **`README.md`** feature list updated and URL fixed

## — Alignment work completed (2026-07-18) —

All existing implemented APIs have been verified live against the LTA DataMall API (v6.8). Changes made:

### Bus Services (v6.8 filter)
- Added optional `service_no` parameter to `Bus.services()`
- When provided, sends `?ServiceNo=...` query param
- Verified: `bus.services(service_no="63")` returns correct filtered results

### Bus Stops (v6.8 filter)
- Added optional `bus_stop_code` parameter to `Bus.stops()`
- When provided, sends `?BusStopCode=...` query param
- Verified: `bus.stops(bus_stop_code="01012")` returns correct filtered result

### Train Service Alerts (response shape fix)
- Realized `value` is a **dict** `{Status, AffectedSegments, Message}`, not a list
- Fixed: service_alerts returns `data['value']` directly instead of `transform_data(data)`
- Verified: returns correct structure with all expected keys

### Station Crowd Density (re-enabled with TrainLine param)
- Re-implemented with correct `train_line: str` mandatory parameter per PDF §2.24–2.25
- Note: `value` is a **list** here (standard format), so uses `transform_data(data)`
- Endpoints verified as accessible (PCDRealTime?TrainLine=EWL returned 33 stations)

### Bus Arrival endpoint
- Migrated from `BusArrivalv2` to `v3/BusArrival`
- Verified: `Monitored` attribute is now present in response (v3 feature)

### Remaining architectural note
- `bus.routes()` and `bus.stops()` (unfiltered) paginate through all records sequentially, which makes the full test suite slow (~30s+ due to many pagination hops)
- This is an inherent limitation of the current fetch() implementation, not a bug

## — Architectural refactor completed (2026-07-18) —

### Changes applied

#### 1. Normalised `fetch()` return type (was problem #1)
- `fetch()` now ALWAYS returns a flat list of record dicts
- Internally handles three response shapes:
  - `{"value": [{...}, ...]}` — standard paginated APIs (auto-paginates 500-record pages)
  - `{"Services": [{...}, ...]}` — Bus Arrival v3
  - empty responses → `[]`
- **New `fetch_value()`** — for APIs where `value` is a single dict (Train Service Alerts)
  - Returns the value dict directly
- No more dual-return-type confusion

#### 2. Custom exception hierarchy (was problem #4)
- `LTADataMallError` — base class for all SDK errors
- `LTADataMallHTTPError(endpoint, status)` — typed HTTP error with readable message

#### 3. Removed dead code
- `src/ltasg/traffic.py` deleted (empty stub, 11 traffic APIs never implemented)
- `src/ltasg/main.py` deleted (dev scratch file with hardcoded key)
- Dead `data: dict = None` parameter removed from `fetch()`

#### 4. Flattened `helpers/helpers.py` (was problem #3)
- `src/ltasg/helpers.py` — single file, no nesting
- Import path: `from ltasg.helpers import transform_data` (was `helpers.helpers`)

#### 5. Renamed `transport/transport.py` → `transport/base.py` (was problem #3)
- Removed `transport.transport` naming collision
- Import path: `from ..transport.base import Transport`
- `transport/__init__.py` updated

### What stayed the same
- Public API unchanged: `Bus(api_key=...)`, `bus.arrival()`, `bus.services()`, etc.
- Service method return types unchanged (callers see the same data shapes)
- E2E tests pass without modification
- All 55 tests pass across all 3 tiers

### Summary of architectural improvements

| Metric | Before | After |
|--------|--------|-------|
| `fetch()` return types | 2 (dict / list) | 1 (flat list) |
| Exceptions | generic `Exception` | `LTADataMallError` + `LTADataMallHTTPError` |
| Dead files | `traffic.py`, `main.py` | removed |
| `transport.transport` | double naming in imports | `transport.base` |
| `helpers.helpers` | double nesting | `helpers` (flattened) |
| `transform_data` import in services | 3 files | 0 files (handled internally) |
| Tests | 53 (passing) | 55 (passing) |

## — Architectural alignment plan (2026-07-18) —

### Current state baseline

- 9 production files, 313 lines
- 4 test files, 634 lines
- 55 passing tests (49 non-network + 6 E2E)
- 7 of 30 APIs implemented

### Target state principles

1. Single-responsibility per method: one method, one consistent return type
2. No orphaned code: every public function has at least one production caller
3. Minimal duplication: shared HTTP infrastructure in one place, not two
4. Self-describing project: tooling configuration in pyproject.toml
5. Clean imports: explicit over star imports
6. Standard library usage: urllib.parse instead of manual URL concatenation

### Phase 1 — Foundation (no behavior change)

**Goal:** Establish constants, fix imports, add tooling config. No runtime behavior changes.

**Files changed:** constants.py, __init__.py (root + transport), pyproject.toml

**Changes:**

| File | Change | Lines |
|------|--------|-------|
| `api.py` | Add `RECORD_LIMIT = 500` class constant, replace hardcoded `500` | +3 / -1 |
| `src/ltasg/__init__.py` | Replace `from .transport import *` with `from .transport.bus import Bus` etc. | -1 / +4 |
| `transport/__init__.py` | Replace `from .xxx import *` with `from .xxx import YYY` | -4 / +4 |
| `pyproject.toml` | Add `[tool.pytest.ini_options]` to make test runner self-describing | +8 |

**No test changes needed** — runtime behavior unchanged.

**Verification:** `python3 -m unittest discover -s test -p "test_*.py"` — all 55 tests pass.

**Risk:** None. Star import removal could break someone doing `from ltasg import LTADataMall` — but `traffic.py` was already deleted in the previous refactor, so `LTADataMall` is no longer exported from the top-level package anyway.

---

### Phase 2 — URL construction (P4)

**Goal:** Replace manual string concatenation with `urllib.parse.urlencode`. Properly encode query param values and eliminate fragile `"?" in url` separator detection.

**Files changed:** api.py

**Current behavior:**
```python
def _build_url(self, endpoint: str, query_params: dict = None) -> str:
    url = f"{self.BASE_URL}{endpoint}"
    if query_params:
        url += "?"
        for k, v in query_params.items():
            url += f"{k}={v}&"        # trailing &, no URL encoding
    return url

@staticmethod
def _paginate(url: str, skip_count: int) -> str:
    if skip_count == 0 and "?" not in url:
        return url
    separator = "" if "?" in url else "?"  # fragile "?" detection
    return f"{url}{separator}$skip={skip_count}"
```

**Target behavior:**
```python
def _build_url(self, endpoint: str, query_params: dict = None) -> str:
    url = f"{self.BASE_URL}{endpoint}"
    if query_params:
        url += "?" + urlencode(query_params)   # proper encoding, no trailing &
    return url

@staticmethod
def _paginate(url: str, skip_count: int) -> str:
    if skip_count == 0:
        return url
    sep = "&" if "?" in url else "?"           # clean, still checks for "?"
    return f"{url}{sep}$skip={skip_count}"
```

**Key difference:** After `urlencode`, the URL looks like `?BusStopCode=83139&ServiceNo=63` (no trailing `&`). The `_paginate` method doesn't need to handle trailing `&` anymore — it just uses `&` if `?` already exists, `?` otherwise.

**Test changes:** None. Integration tests mock `ClientSession.get` and verify response shapes, not URL strings.

**Verification:** All 55 tests pass. E2E tests verify live API still accepts the URLs.

**Risk:** Low. `.urlencode()` produces the same query string structure as manual concatenation, except without the trailing `&` which never mattered.

---

### Phase 3 — Extract `_request()` + share HTTP boilerplate (P1)

**Goal:** Eliminate the ~15 identical lines of HTTP setup between `fetch()` and `fetch_value()`.

**Files changed:** api.py

**Current duplication:**
```
fetch()                                  fetch_value()
  _build_url(endpoint, params)             _build_url(endpoint, params)
  async with ClientSession():              async with ClientSession():
    async with session.get():                async with session.get():
      if not response.ok:                      if not response.ok:
        raise HTTPError(...)                     raise HTTPError(...)
      curr_data = response.json()              curr_data = response.json()
      ...records extraction...                 return curr_data["value"]
```

**Target:**
```python
async def _request(self, endpoint: str, query_params: dict = None):
    """Raw HTTP GET. Returns parsed JSON. Handles auth and errors."""
    url = self._build_url(endpoint, query_params)
    async with ClientSession() as session:
        try:
            async with session.get(url, headers=self.HEADERS) as response:
                if not response.ok:
                    raise LTADataMallHTTPError(endpoint, response.status)
                return await response.json()
        except ClientConnectionError:
            raise

async def fetch(self, endpoint, query_params=None):
    curr_data = await self._request(endpoint, query_params)
    records = curr_data.get("Services", curr_data.get("value", []))
    ...pagination loop using _request()...
    return all_records

async def fetch_value(self, endpoint, query_params=None):
    curr_data = await self._request(endpoint, query_params)
    return curr_data["value"]
```

**Important design decision:** `_request()` still creates a new `ClientSession` per call (no session reuse yet — that's Phase 4). This keeps Phase 3 a pure extraction with no behavioral change, making it easy to verify.

**Test changes:** None. Unit tests mock `fetch()` and `fetch_value()` directly. Integration tests mock `ClientSession`, which `_request()` will use internally.

**Verification:** All 55 tests pass.

**Risk:** Low. Pure refactoring — same logic, new name.

---

### Phase 4 — ClientSession reuse (P0)

**Goal:** Share one `aiohttp.ClientSession` across all calls from the same `LTADataMall` instance, eliminating the ~500ms TCP handshake per pagination hop.

**Files changed:** api.py, test_integration.py, test.py (E2E)

**Change in api.py:**
```python
class LTADataMall:
    def __init__(self, base_url, api_key):
        self._session = None   # lazy init
        ...

    async def _get_session(self):
        if self._session is None:
            self._session = ClientSession()
        return self._session

    async def _request(self, endpoint, query_params=None):
        url = self._build_url(endpoint, query_params)
        session = await self._get_session()    # ← shared session
        try:
            async with session.get(url, headers=self.HEADERS) as response:
                ...
        except ClientConnectionError:
            raise

    async def close(self):
        if self._session is not None:
            await self._session.close()
            self._session = None
```

**Important:** `_request()` no longer uses `async with ClientSession()`. Instead, it gets the shared session from `_get_session()`. The `close()` method is added for explicit cleanup.

**Test changes:**

| File | Change | Reason |
|------|--------|--------|
| `test_integration.py` | Update `_make_mock_session` — integration tests mock `ClientSession` constructor, which `_get_session()` now calls | The mock still needs to intercept `ClientSession()` |
| `test.py` (E2E) | Add `tearDown` that calls `self.bus.lta_api.close()` etc. | Clean up shared sessions between test methods |

The integration tests patch `ltasg.api.ClientSession`, which is still the class used by `_get_session()`. The mock works the same way — when `ClientSession()` is called, it returns the mock session. The only difference is that it's called once (on first request) instead of once per `fetch()`/`fetch_value()` call.

**Verification:** All 55 tests pass. E2E tests should have fewer ResourceWarnings. Slow paginated tests should be faster.

**Risk:** Medium. Shared session means connection errors could affect subsequent requests. aiohttp handles this internally (failed connections are discarded). The `close()` method is opt-in — callers who don't call it still work (session is GC'd eventually). Backward compatible.

---

### Phase 5 — Subclass constructor normalization (P3)

**Goal:** Eliminate the three nearly-identical subclass constructors.

**Current state (3 copies):**
```python
class Bus(Transport):
    def __init__(self, base_url=DEFAULT_BASE_URL, api_key=None) -> None:
        super().__init__(base_url=base_url, api_key=api_key)
        self.bus_services = self.transport_services[TransportType.BUS]
```

**Target state:**

**transport/base.py:**
```python
class Transport:
    _service_type = None    # override in subclasses

    def __init__(self, base_url=DEFAULT_BASE_URL, api_key=None):
        self.lta_api = LTADataMall(base_url=base_url, api_key=api_key)
        services = LTA_SERVICES['PUBLIC_TRANSPORT_SERVICES']
        self._svc = services[self._service_type] if self._service_type else {}
```

**transport/bus.py:**
```python
class Bus(Transport):
    _service_type = TransportType.BUS
    # No __init__ — inherited from Transport
    # Uses self._svc instead of self.bus_services
```

**Files changed:** transport/base.py, transport/bus.py, transport/train.py, transport/taxi.py

**Attribute rename:** `self.bus_services` → `self._svc`, `self.train_services` → `self._svc`, `self.taxi_services` → `self._svc`. These are internal attributes — no test or external code references them.

**Test changes:** None. Tests create instances with `Bus(api_key=...)` which still works via inherited `Transport.__init__`.

**Verification:** All 55 tests pass.

**Risk:** Low. The `_svc` attribute name change is internal-only. If someone wrote `bus._svc` they'd be accessing a private attribute anyway, and it still exists.

---

### Phase 6 — Cleanup (P2, P7, P8)

**Goal:** Remove orphaned code, address the hardcoded `"Services"` key, and finalize.

**6a: Handle `transform_data` orphan:**

Two options:
- **Remove** `transform_data` and its test class entirely (lose the helper)
- **Keep** as a documented utility for advanced use cases (batch processing raw page data)

Recommendation: Remove it. The function is 4 lines and trivial to recreate if needed. Keeping dead code confuses more than it helps.

**Files changed:** helpers.py, test_unit.py

**6b: Address `"Services"` key in fetch():**

Two options (from the audit):
- **Option A (recommended):** Leave the hardcoded check. Only one API deviates from the `"value"` standard.
- **Option B:** Add an optional `records_key` parameter to `fetch()` and have `bus.arrival()` pass `records_key="Services"`.

If Option B is chosen, the change is:
```python
# api.py
async def fetch(self, endpoint, query_params=None, records_key="value"):
    ...
    records = curr_data.get(records_key, [])
    if isinstance(records, list):
        ...

# bus.py
async def arrival(self, bus_stop_code, bus_no):
    return await self.lta_api.fetch(
        self._svc['ARRIVAL'],
        query_params={...},
        records_key="Services",   # ← explicit
    )
```

Recommendation: Option A for now (defer to when more non-standard APIs are added).

**Verification:** All 55 tests pass.

---

### Summary of phases

| Phase | What | Files changed | Test changes | Risk | Estimated time |
|-------|------|---------------|-------------|------|----------------|
| 1 | Foundation (constant, imports, config) | 4 | None | None | ~2 min |
| 2 | URL construction (urlencode) | 1 | None | Low | ~3 min |
| 3 | Extract `_request()` | 1 | None | Low | ~5 min |
| 4 | ClientSession reuse | 3 | Update mocks + teardown | Medium | ~8 min |
| 5 | Subclass normalization | 4 | None | Low | ~5 min |
| 6 | Cleanup (remove orphaned code) | 2 | Remove test class | Low | ~3 min |

### Verification gate per phase

After every phase, run:
```bash
cd ltasg && python3 -m unittest test.test_unit test.test_integration -v
cd ltasg && python3 -m unittest test.test.TestQuickE2E -v
```

Both must pass before moving to the next phase.

### Rollback plan

If a phase breaks tests, revert the changed files (`git checkout -- <files>`) and investigate. Each phase is designed to be independently revertible since no phase changes external API behavior.

## — Traffic API implementation plan (2026-07-18) —

### Phase: Traffic (11 APIs)
**Category**: Traffic Related (PDF §§2.12–2.20, 2.26, 2.30)

### Grounding

All 11 Traffic APIs share these properties:
- Response format: `{"value": [{...}, ...]}` (standard)
- No request parameters (none require or accept params)
- No special response shapes (exception: Traffic Flow returns a download Link)
- `fetch()` with default `records_key="value"` handles all of them

| # | API | PDF § | URL | Notes |
|---|-----|-------|-----|-------|
| 1 | Carpark Availability | 2.12 | `CarParkAvailabilityv2` | 1 min freq |
| 2 | Estimated Travel Times | 2.13 | `EstTravelTimes` | 5 min freq |
| 3 | Faulty Traffic Lights | 2.14 | `FaultyTrafficLights` | 2 min freq |
| 4 | Planned Road Openings | 2.15 | `RoadOpenings` | 24h freq |
| 5 | Approved Road Works | 2.16 | `RoadWorks` | 24h freq |
| 6 | Traffic Images (v2) | 2.17 | `Traffic-Imagesv2` | 1-5 min freq |
| 7 | Traffic Incidents | 2.18 | `TrafficIncidents` | 2 min freq |
| 8 | Traffic Speed Bands (v4) | 2.19 | `v4/TrafficSpeedBands` | 5 min freq |
| 9 | VMS / EMAS | 2.20 | `VMS` | 2 min freq |
| 10 | Traffic Flow | 2.26 | `TrafficFlow` | Quarterly; returns download Link |
| 11 | Flood Alerts | 2.30 | `PubFloodAlerts` | 3 min freq |

### Files to create/modify

| File | Action | Reason |
|------|--------|--------|
| `src/ltasg/constants.py` | Modify | Add `TRAFFIC_SERVICES` dict |
| `src/ltasg/traffic.py` | Create | New `Traffic` class with 11 methods |
| `src/ltasg/__init__.py` | Modify | Add `from .traffic import Traffic` |
| `test/test_unit.py` | Modify | Add `TestTraffic` class (11 tests) |
| `test/test.py` | Modify | Add `TestTrafficE2E` class (3 quick E2E tests) |

### Traffic class structure

```python
class Traffic:
    def __init__(self, base_url=DEFAULT_BASE_URL, api_key=None):
        self.lta_api = LTADataMall(base_url=base_url, api_key=api_key)
        self._svc = TRAFFIC_SERVICES

    async def carpark_availability(self) -> list[dict]: ...
    async def estimated_travel_times(self) -> list[dict]: ...
    async def faulty_traffic_lights(self) -> list[dict]: ...
    async def planned_road_openings(self) -> list[dict]: ...
    async def approved_road_works(self) -> list[dict]: ...
    async def traffic_images(self) -> list[dict]: ...
    async def traffic_incidents(self) -> list[dict]: ...
    async def traffic_speed_bands(self) -> list[dict]: ...
    async def vms(self) -> list[dict]: ...
    async def traffic_flow(self) -> list[dict]: ...
    async def flood_alerts(self) -> list[dict]: ...
```

Every method follows the same pattern:
```python
async def some_api(self):
    return await self.lta_api.fetch(self._svc["ENDPOINT_KEY"])
```

Notes:
- Traffic is NOT a Transport subclass (it's a separate domain)
- No context manager needed for this phase (inherits session from LTADataMall)
- Traffic class can be used standalone: `Traffic(api_key=key).carpark_availability()`
- Traffic Flow returns `[{"Link": "..."}]` — same pattern, caller extracts the URL

### Constants to add

```python
TRAFFIC_SERVICES = {
    "CARPARK_AVAILABILITY": "CarParkAvailabilityv2",
    "ESTIMATED_TRAVEL_TIMES": "EstTravelTimes",
    "FAULTY_TRAFFIC_LIGHTS": "FaultyTrafficLights",
    "PLANNED_ROAD_OPENINGS": "RoadOpenings",
    "APPROVED_ROAD_WORKS": "RoadWorks",
    "TRAFFIC_IMAGES": "Traffic-Imagesv2",
    "TRAFFIC_INCIDENTS": "TrafficIncidents",
    "TRAFFIC_SPEED_BANDS": "v4/TrafficSpeedBands",
    "VMS": "VMS",
    "TRAFFIC_FLOW": "TrafficFlow",
    "FLOOD_ALERTS": "PubFloodAlerts",
}
```

### Test plan

**Unit tests (11 tests, 1 per API):**
Each mocks `fetch()`, asserts correct endpoint and return value shape.

**E2E tests (3 tests):**
- `test_traffic_incidents` — always populated (live incidents)
- `test_traffic_carpark_availability` — always populated (live carpark data)
- `test_traffic_flood_alerts` — may be empty; verifies response shape if present

### Verification
After implementation:
```
python3 -m unittest test.test_unit -v    # verify 11 new unit tests pass
python3 -m unittest test.test.TestTrafficE2E -v  # verify 3 new E2E tests pass
```

## — Public Transport + Other API implementation (2026-07-18) —

### Remaining APIs: 9 total

**Public Transport (5):** PV/Bus, PV/ODBus, PV/ODTrain, PV/Train, PlannedBusRoutes
**Other (4):** BicycleParkingv2, GeospatialWholeIsland, EVChargingPoints, EVCBatch

### Implementation plan

| Category | File changes | New methods | Tests |
|----------|-------------|-------------|-------|
| PT (Bus) | constants.py, bus.py | `passenger_volume_by_bus_stops`, `passenger_volume_by_od_bus_stops`, `planned_bus_routes` | 3 unit |
| PT (Train) | constants.py, train.py | `passenger_volume_by_od_train_stations`, `passenger_volume_by_train_stations` | 2 unit |
| Other | constants.py, other.py (new) | `bicycle_parking`, `geospatial_whole_island`, `ev_charging_points`, `ev_charging_points_batch` | 4 unit + 1 E2E |

## — Dependabot PR refresh and TestPyPI duplicate handling (2026-08-04) —

### Findings

- Dependabot PRs #2 (`actions/download-artifact` v4 to v8) and #4 (`actions/upload-artifact` v4 to v7) are stale against current `main`.
- Their historical failed `Build distribution` checks were caused by the sdist test failure fixed by the existing packaging exclusion change, not by the action upgrades.
- Dependabot rebase requests were issued for both PRs so GitHub can regenerate checks against current `main`.
- TestPyPI publishing runs on every non-tag push to `main`. Dependency-only merges can leave the package at version `1.0.0`, causing TestPyPI to reject reused filenames with HTTP 400.

### Decision

- Add `skip-existing: true` only to the TestPyPI publisher. This makes repeated smoke publishes idempotent while keeping production PyPI duplicate detection strict.
- The workflow change remains local and uncommitted pending explicit approval to commit and push it.

### Verification

- The two Dependabot rebase-triggered `Build distribution` runs completed successfully: PR #2 run `30922575598` and PR #4 run `30922577547`.
- The missing GitHub `dependencies` label was created to match `.github/dependabot.yml`.
- Local `python -m pytest test/test_sdk_packaging.py -v` passed all 11 tests after serial execution; concurrent packaging runs are unsafe because they share `dist/`.

### Rollout

- User approved committing and pushing the TestPyPI workflow fix; the change is now staged for the remote rollout.

### Completion

- Commit `c173bfd` was pushed to `main`.
- Dependabot PR #2 merged as `009ec36`; PR #4 merged as `b6f85d7`.
- The post-merge TestPyPI publishing runs succeeded for both merge commits, confirming duplicate-file handling is fixed.

## — Public repository professionalization and hardening (2026-08-05) —

### Locked scope

- Full public-repository hardening is being implemented on the dedicated branch `chore/public-repository-hardening`.
- Release governance is strict: semantic release creates the version commit/tag, while the tag-triggered release workflow alone publishes to PyPI and creates the GitHub Release.
- TestPyPI remains duplicate-tolerant; production PyPI remains duplicate-strict.
- GitHub Discussions remain disabled, the unused Wiki will be disabled, and private vulnerability reporting will be enabled.
- `main` will require pull requests, one approval, current required CI checks, resolved conversations, linear history, and no force pushes/deletions; administrator bypass remains available for solo-maintainer work.

### Implementation decisions

- README documentation now uses the official LTA DataMall API guide, an awaited async context-manager example, Python 3.12+ support, API-key/session guidance, troubleshooting, contribution links, and a clarified 30-upstream-API count. `Stop Services` is documented as a client-side helper.
- Project metadata now points to the canonical repository, PyPI project, official documentation, issues, and changelog, and exposes a pinned development extra including packaging, test, lint, type, pre-commit, audit, and semantic-release tooling.
- Community health files, CODEOWNERS, issue forms, pull-request template, dedicated CI, and CodeQL workflows were added. Third-party Actions are pinned to full commit SHAs.
- Publishing workflows are now separated from validation, use least-privilege permissions, publish TestPyPI only from `main`, publish PyPI only from `v*` tags, and generate GitHub release notes.

### Initial verification

- Baseline test suite passed: `python -m pytest test/ -v --timeout=30` (82 tests).
- The first PR CI run exposed two vulnerable legacy pins in `requirements.txt` (`aiohttp==3.9.5` and `setuptools==69.5.1`); both were updated to fixed versions and the package lower bound was raised to `aiohttp >= 3.13.4`.

### GitHub rollout verification

- PR #12 was merged as `a17b7c0` after all required checks passed: Test Python 3.12, Test Python 3.13, Quality, Package, Dependency audit, and CodeQL/Analyze Python.
- Repository About metadata now has the requested description, PyPI homepage, and nine topics. Squash merging is enabled; merge commits, rebase merges, auto-merge, the Wiki, and Discussions are disabled; branches are deleted after merge.
- Dependabot vulnerability alerts and automated security fixes are enabled. Private vulnerability reporting is enabled, and CodeQL has produced successful analyses for the pull request and `main`.
- Actions now default to read-only permissions, require immutable SHA-pinned actions, and allow GitHub-owned plus verified actions. The workflows in this repository use full commit SHAs.
- `main` protection requires pull requests, one approval, up-to-date required checks, conversation resolution, linear history, and blocks force pushes and deletions. Administrator enforcement remains disabled for the solo-maintainer bypass.
- The active `Protect release tags` ruleset covers `refs/tags/v*`, blocks creation except for the maintainer bypass, and blocks deletion and non-fast-forward updates.
- The `testpypi` environment accepts only `main` deployments. The `pypi` environment requires maintainer review and accepts only `v*` tag deployments.
