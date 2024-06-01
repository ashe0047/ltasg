# ltasg

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/ltasg.svg)](https://badge.fury.io/py/your-package)
[![Python versions](https://img.shields.io/pypi/pyversions/ltasg.svg)](https://pypi.org/project/your-package/)
<!-- [![Documentation Status](https://readthedocs.org/projects/your-package/badge/?version=latest)](https://your-package.readthedocs.io/en/latest/?badge=latest) -->

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

# Example usage
base_url = "https://http://datamall2.mytransport.sg/ltaodataservice/"
api_key = <YOUR_LTA_DATAMALL_API_KEY>

bus = Bus(base_url, api_key)
result = bus.arrival(71111, '63')
print(result)
```

## Features

### Bus

1. Bus Arrival
2. Bus Routes
3. Bus Services

### Train

1. Train Service Alerts
2. Platform Crowd Density Realtime
3. Platform Crowd Density Forecast

## Documentation

> TBA

## License

This project is licensed under the MIT License - see the [LICENSE](/LICENSE) file for details.

