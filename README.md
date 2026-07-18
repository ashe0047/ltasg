# ltasg

[![Build Status](https://github.com/ashe0047/ltasg/actions/workflows/release.yml/badge.svg?event=push)](https://github.com/ashe0047/ltasg/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://img.shields.io/pypi/v/ltasg?logo=pypi)](https://badge.fury.io/py/your-package)
[![Python versions](https://img.shields.io/pypi/pyversions/ltasg.svg?logo=python)](https://pypi.org/project/ltasg/)

A LTA Datamall API Wrapper Library for Python

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Documentation](#documentation)
- [License](#license)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install `ltasg`:

```sh
pip install ltasg
```

## Usage

- **Bus Arrival**: Querying bus arrival timings

```python
from ltasg.transport.bus import Bus

# Default base URL uses HTTPS; optionally pass a custom base_url.
api_key = "<YOUR_LTA_DATAMALL_API_KEY>"

bus = Bus(api_key=api_key)
result = bus.arrival(71111, '63')
print(result)
```

## Features

### Bus (8 APIs)

1. Bus Arrival (v3)
2. Bus Services (with optional ServiceNo filter)
3. Bus Routes
4. Bus Stops (with optional BusStopCode filter)
5. Passenger Volume by Bus Stops (download Link)
6. Passenger Volume by Origin-Destination Bus Stops (download Link)
7. Planned Bus Routes
8. Stop Services (client-side route filter)

### Train (6 APIs)

1. Train Service Alerts
2. Facilities Maintenance (v2)
3. Station Crowd Density Real-time
4. Station Crowd Density Forecast
5. Passenger Volume by Origin-Destination Train Stations (download Link)
6. Passenger Volume by Train Stations (download Link)

### Taxi (2 APIs)

1. Taxi Availability
2. Taxi Stands

### Traffic (11 APIs)

1. Carpark Availability (v2)
2. Estimated Travel Times
3. Faulty Traffic Lights
4. Planned Road Openings
5. Approved Road Works
6. Traffic Images (v2)
7. Traffic Incidents
8. Traffic Speed Bands (v4)
9. VMS / EMAS
10. Traffic Flow (download Link)
11. Flood Alerts

### Other (4 APIs)

1. Bicycle Parking (v2)
2. Geospatial Whole Island
3. EV Charging Points
4. EV Charging Points Batch

## Documentation

Full API reference: [LTA DataMall API User Guide v6.8](https://datamall2.mytransport.sg)

For parameter details and response schemas, refer to the PDF guide.

## License

This project is licensed under the MIT License - see the [LICENSE](/LICENSE) file for details.
