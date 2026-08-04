"""ltasg — LTA DataMall API Wrapper Library for Python."""

__version__ = "1.0.0"

from .other import Other as Other
from .traffic import Traffic as Traffic
from .transport.bus import Bus as Bus
from .transport.taxi import Taxi as Taxi
from .transport.train import Train as Train

__all__ = ["Bus", "Other", "Taxi", "Train", "Traffic", "__version__"]
