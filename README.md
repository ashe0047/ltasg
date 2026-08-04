# ltasg

[![CI](https://github.com/ashe0047/ltasg/actions/workflows/ci.yml/badge.svg)](https://github.com/ashe0047/ltasg/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/ltasg?logo=pypi)](https://pypi.org/project/ltasg/)
[![Python versions](https://img.shields.io/pypi/pyversions/ltasg.svg?logo=python)](https://pypi.org/project/ltasg/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Async Python client for Singapore’s [LTA DataMall API](https://datamall.lta.gov.sg/), covering bus, train, taxi, traffic, and passenger-volume data.

## Requirements

- Python 3.12 or newer
- An LTA DataMall API key

## Installation

```sh
python -m pip install ltasg
```

## API key setup

Request an API key from the [LTA DataMall portal](https://datamall.lta.gov.sg/). Keep the key private and provide it when creating a client. The library does not read or persist credentials automatically.

## Usage

Clients are asynchronous context managers. The context closes the underlying `aiohttp` session when the client is no longer needed.

```python
import asyncio
import os

from ltasg.transport.bus import Bus


async def main() -> None:
    api_key = os.environ["LTA_API_KEY"]

    async with Bus(api_key=api_key) as bus:
        arrivals = await bus.arrival(71111, "63")
        print(arrivals)


if __name__ == "__main__":
    asyncio.run(main())
```

## Supported API groups

The client exposes the 30 upstream DataMall APIs implemented by this project. `Stop Services` is an additional convenience helper: it fetches Bus Routes once and filters service numbers locally, so it is not counted as a separate upstream endpoint.

- **Bus:** arrival, services, routes, stops, passenger volume by bus stops, passenger volume by origin-destination bus stops, and planned bus routes
- **Train:** service alerts, facilities maintenance, real-time and forecast station crowd density, and passenger volume by train stations and origin-destination train stations
- **Taxi:** availability and taxi stands
- **Traffic:** carpark availability, estimated travel times, faulty traffic lights, planned road openings, approved road works, traffic images, traffic incidents, traffic speed bands, VMS/EMAS, traffic flow, and flood alerts
- **Other:** bicycle parking, geospatial whole island, EV charging points, and batched EV charging points

Some passenger-volume and traffic-flow APIs return a DataMall download link rather than the dataset itself. Refer to the method docstrings and the official guide for response details.

## Documentation

The authoritative endpoint parameters and response schemas are in the [LTA DataMall API User Guide](https://datamall.lta.gov.sg/content/dam/datamall/datasets/LTA_DataMall_API_User_Guide.pdf?ref=public_apis).

## Troubleshooting

- **401 or 403 responses:** verify that `LTA_API_KEY` is present, valid, and passed as `api_key`.
- **Empty results:** DataMall datasets can legitimately be empty; check the endpoint and query parameters against the official guide.
- **Connection or timeout errors:** check network access and retry the request. Use one client context for a group of requests so the HTTP session is reused.
- **Unexpected response shapes:** confirm the DataMall API version and inspect the raw endpoint documentation; upstream datasets can change independently of this package.

## Contributing

Bug reports, improvements, and new API coverage are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md), [SUPPORT.md](SUPPORT.md), and the [issue tracker](https://github.com/ashe0047/ltasg/issues).

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
