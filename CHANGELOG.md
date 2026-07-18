# CHANGELOG

<!-- version list -->

## v0.0.7 (2026-07-18)

### Features

- Full API parity: all 30 LTA DataMall v6.8 APIs implemented
- New Traffic class (11 APIs): carpark, travel times, traffic lights, road
  openings, road works, traffic images, incidents, speed bands, VMS/EMAS,
  traffic flow, flood alerts
- New Other class (4 APIs): bicycle parking, geospatial whole island,
  EV charging points, EV charging points batch
- Passenger Volume (PV) APIs for bus stops, OD bus, OD train, train stations
- Planned Bus Routes API

### Bug Fixes

- Bus Arrival endpoint migrated from v2 to v3
- Train service alerts response handling fixed (value is a dict, not a list)
- Station Crowd Density APIs re-enabled with mandatory TrainLine parameter
- Base URL migrated from HTTP to HTTPS
- Test suite completely rewritten and all 80 tests pass
- Constructor signature fix: base_url is now optional

### Documentation

- README updated with current feature list and correct URLs

## v0.0.6 (2024-08-16)

### Features

- Initial release with Bus, Train, Taxi transport APIs
- Bus Arrival, Services, Routes, Stops
- Taxi Availability, Taxi Stands
- Train Service Alerts
- Async aiohttp-based HTTP client with automatic pagination
