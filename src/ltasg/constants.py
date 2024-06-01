from enum import Enum


class TransportType(Enum):
    BUS = "bus"
    TRAIN = "mrt"
    TAXI = "taxi"

LTA_SERVICES = {
    "PUBLIC_TRANSPORT_SERVICES": {
        TransportType.BUS: {
            "ARRIVAL": "BusArrivalv2",
            "SERVICES": "BusServices",
            "ROUTES": "BusRoutes",
            "STOPS": "BusStops",
            # "PASSENGER_VOLUME": {
            #     "BUS_STOPS": "PV/Bus",
            #     "ORIGIN_TO_DEST": "PV/ODBus"
            # }
        },
        TransportType.TRAIN: {
            # "PASSENGER_VOLUME": {
            #     "ORIGIN_TO_DEST": "PV/ODTrain",
            # },
            "PLATFORM_CROWD_DENSITY": {
                "REALTIME": "PCDRealTime",
                "FORECAST": "PCDForecast"
            },
            "SERVICE_ALERTS": "TrainServiceAlerts"
        },
        TransportType.TAXI: {
            "AVAILABILITY": "Taxi-Availability",
            "STANDS": "TaxiStands",
        }
}}
